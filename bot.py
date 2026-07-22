import os
import logging
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)

from rag_engine import RAGEngine

# Load environment
load_dotenv()

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Init RAG
rag = RAGEngine()

# Keyboard
main_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📚 Загрузить документ")],
        [KeyboardButton("❓ Задать вопрос"), KeyboardButton("📋 Список документов")],
        [KeyboardButton("🗑 Очистить базу"), KeyboardButton("ℹ️ Помощь")],
    ],
    resize_keyboard=True
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие."""
    await update.message.reply_text(
        "👋 Привет! Я KnowledgeBot — AI-ассистент, который отвечает "
        "на вопросы по вашим документам.\n\n"
        "📚 Загрузите PDF или текстовый файл\n"
        "❓ Задайте вопрос по содержимому\n\n"
        "Используйте кнопки меню для навигации.",
        reply_markup=main_keyboard
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Справка."""
    await update.message.reply_text(
        "📖 Как пользоваться:\n\n"
        "1. Нажмите «📚 Загрузить документ» и отправьте PDF или .txt файл\n"
        "2. Нажмите «❓ Задать вопрос» и напишите вопрос\n"
        "3. Бот найдёт релевантный контекст и ответит\n\n"
        "📌 Команды:\n"
        "/start — Начало\n"
        "/help — Помощь\n"
        "/list — Список загруженных документов\n"
        "/clear — Очистить базу знаний",
        reply_markup=main_keyboard
    )


async def list_documents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список документов."""
    docs = rag.list_documents()
    if not docs:
        await update.message.reply_text(
            "📭 База знаний пуста. Загрузите документ!",
            reply_markup=main_keyboard
        )
        return

    msg = "📚 Загруженные документы:\n\n"
    for i, doc in enumerate(docs, 1):
        msg += f"{i}. {doc['name']} ({doc['chunks']} фрагментов)\n"
    msg += f"\nВсего: {len(docs)} документов"
    await update.message.reply_text(msg, reply_markup=main_keyboard)


async def clear_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очистить базу."""
    rag.clear()
    await update.message.reply_text(
        "🗑 База знаний очищена!",
        reply_markup=main_keyboard
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка загруженных файлов."""
    document = update.message.document
    if not document:
        await update.message.reply_text("❌ Отправьте PDF или TXT файл.")
        return

    file_ext = Path(document.file_name).suffix.lower()
    if file_ext not in [".pdf", ".txt"]:
        await update.message.reply_text(
            "❌ Поддерживаются только PDF и TXT файлы."
        )
        return

    if document.file_size > 20 * 1024 * 1024:
        await update.message.reply_text("❌ Файл слишком большой (максимум 20MB).")
        return

    await update.message.reply_text("⏳ Обрабатываю документ...")

    try:
        file = await context.bot.get_file(document.file_id)
        temp_path = f"/tmp/{document.file_name}"
        await file.download_to_drive(temp_path)

        result = rag.add_document(temp_path, document.file_name)

        os.remove(temp_path)

        await update.message.reply_text(
            f"✅ Документ «{document.file_name}» загружен!\n\n"
            f"📊 Статистика:\n"
            f"• Фрагментов: {result['chunks']}\n"
            f"• Символов: {result['characters']}\n\n"
            f"Теперь задавайте вопросы по содержимому!",
            reply_markup=main_keyboard
        )
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        await update.message.reply_text(
            f"❌ Ошибка при обработке: {str(e)}\n\nПопробуйте другой файл.",
            reply_markup=main_keyboard
        )


async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка вопросов."""
    question = update.message.text

    docs = rag.list_documents()
    if not docs:
        await update.message.reply_text(
            "📭 База знаний пуста! Сначала загрузите документ.",
            reply_markup=main_keyboard
        )
        return

    await update.message.reply_text("🤔 Думаю...")

    try:
        result = rag.query(question)

        response = f"💡 Ответ:\n\n{result['answer']}\n"

        if result.get("sources"):
            response += "\n📚 Источники:\n"
            for source in result["sources"][:3]:
                response += f"• {source['document']}: {source['preview']}...\n"

        await update.message.reply_text(response, reply_markup=main_keyboard)
    except Exception as e:
        logger.error(f"Error querying RAG: {e}")
        await update.message.reply_text(
            f"❌ Ошибка: {str(e)}\n\nПопробуйте переформулировать вопрос.",
            reply_markup=main_keyboard
        )


def main():
    """Запуск бота."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return

    application = Application.builder().token(token).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_documents))
    application.add_handler(CommandHandler("clear", clear_database))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question)
    )

    logger.info("🤖 KnowledgeBot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
