"""
RAG Engine — Retrieval-Augmented Generation для KnowledgeBot.
ChromaDB для хранения эмбеддингов + DeepSeek/Groq API для генерации ответов.
"""

import os
import hashlib
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings
from openai import OpenAI
from PyPDF2 import PdfReader


class RAGEngine:
    """RAG engine с ChromaDB + DeepSeek/Groq."""

    def __init__(self):
        # ChromaDB — persistent storage
        self.db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="knowledge",
            metadata={"hnsw:space": "cosine"}
        )

        # DeepSeek API (primary)
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.deepseek_client = OpenAI(
            api_key=self.deepseek_key,
            base_url="https://api.deepseek.com"
        ) if self.deepseek_key else None

        # Groq API (free fallback)
        self.groq_key = os.getenv("GROQ_API_KEY", "")
        self.groq_client = OpenAI(
            api_key=self.groq_key,
            base_url="https://api.groq.com/openai/v1"
        ) if self.groq_key else None

        # Models
        self.deepseek_model = os.getenv("LLM_MODEL", "deepseek-chat")
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

        # System prompt
        self.system_prompt = os.getenv(
            "SYSTEM_PROMPT",
            "Ты helpful ассистент. Отвечай на основе загруженных документов. "
            "Если в документах нет информации для ответа — скажи честно, "
            "что не нашёл релевантной информации. Отвечай на том языке, "
            "на котором задан вопрос."
        )

    def add_document(self, file_path: str, filename: str) -> dict:
        """Загрузить документ в базу знаний."""
        file_path = Path(file_path)

        if file_path.suffix.lower() == ".pdf":
            text = self._extract_pdf(file_path)
        elif file_path.suffix.lower() == ".txt":
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        else:
            raise ValueError(f"Неподдерживаемый формат: {file_path.suffix}")

        if not text.strip():
            raise ValueError("Документ пустой или не удалось извлечь текст.")

        # Разбить на чанки
        chunks = self._split_text(text, chunk_size=1000, overlap=200)

        # Сгенерировать ID для документа
        doc_id = hashlib.md5(filename.encode()).hexdigest()[:12]

        # Добавить в ChromaDB
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "document": filename,
                "doc_id": doc_id,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            for i in range(len(chunks))
        ]

        self.collection.add(
            ids=ids,
            documents=chunks,
            metadatas=metadatas
        )

        return {
            "chunks": len(chunks),
            "characters": len(text),
            "doc_id": doc_id
        }

    def query(self, question: str, top_k: int = 5) -> dict:
        """Задать вопрос и получить ответ на основе документов."""
        # Найти релевантные фрагменты
        results = self.collection.query(
            query_texts=[question],
            n_results=min(top_k, self.collection.count() or 1)
        )

        if not results["documents"][0]:
            return {
                "answer": "📭 База знаний пуста. Загрузите документ для начала работы.",
                "sources": []
            }

        # Собрать контекст
        context_parts = []
        sources = []
        for i, (doc, meta) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0]
        )):
            context_parts.append(f"[Фрагмент {i+1}] {doc}")
            sources.append({
                "document": meta.get("document", "unknown"),
                "preview": doc[:100]
            })

        context = "\n\n".join(context_parts)

        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": (
                    f"Контекст из документов:\n\n{context}\n\n"
                    f"---\nВопрос: {question}\n\n"
                    "Ответь на основе приведённого контекста. "
                    "Если контекста недостаточно — скажи об этом."
                )
            }
        ]

        # Пробуем DeepSeek, потом Groq
        answer = None

        if self.deepseek_client:
            try:
                response = self.deepseek_client.chat.completions.create(
                    model=self.deepseek_model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1500
                )
                answer = response.choices[0].message.content
            except Exception as e:
                print(f"⚠️ DeepSeek failed: {e}. Trying Groq...")

        if not answer and self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    model=self.groq_model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1500
                )
                answer = response.choices[0].message.content
            except Exception as e:
                print(f"⚠️ Groq failed: {e}")

        if not answer:
            answer = (
                "❌ Не удалось получить ответ. "
                "Проверьте API ключи DeepSeek или Groq."
            )

        return {
            "answer": answer,
            "sources": sources
        }

    def list_documents(self) -> list:
        """Список загруженных документов."""
        if self.collection.count() == 0:
            return []

        all_data = self.collection.get(include=["metadatas"])
        docs = {}
        for meta in all_data["metadatas"]:
            doc_name = meta.get("document", "unknown")
            if doc_name not in docs:
                docs[doc_name] = 0
            docs[doc_name] += 1

        return [
            {"name": name, "chunks": count}
            for name, count in docs.items()
        ]

    def clear(self):
        """Очистить базу знаний."""
        self.client.delete_collection("knowledge")
        self.collection = self.client.get_or_create_collection(
            name="knowledge",
            metadata={"hnsw:space": "cosine"}
        )

    def _extract_pdf(self, file_path: Path) -> str:
        """Извлечь текст из PDF."""
        reader = PdfReader(str(file_path))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n\n".join(text_parts)

    def _split_text(
        self,
        text: str,
        chunk_size: int = 1000,
        overlap: int = 200
    ) -> list[str]:
        """Разбить текст на перекрывающиеся чанки."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk.strip())
            start = end - overlap
        return chunks
