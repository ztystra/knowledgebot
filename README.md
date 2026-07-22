# 🤖 KnowledgeBot

[![CI](https://github.com/ztystra/knowledgebot/actions/workflows/ci.yml/badge.svg)](https://github.com/ztystra/knowledgebot/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Telegram Bot API](https://img.shields.io/badge/Telegram-Bot%20API-26A5E4.svg)](https://core.telegram.org/bots/api)
[![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek-red.svg)](https://platform.deepseek.com)

> **AI-ассистент для Telegram, который отвечает на вопросы по вашим документам.**  
> Загружаете PDF или TXT → бот создаёт базу знаний → задаёте вопросы → получаете ответы с источниками.

---

## 🎯 Что это?

KnowledgeBot — это готовый к продакшну Telegram-бот с RAG (Retrieval-Augmented Generation). В отличие от обычных чат-ботов, он работает на **ваших данных** — загруженных документах, а не на общем знании интернета.

### Почему это круто?

| Обычный AI-бот | KnowledgeBot (RAG) |
|---------------|---------------------|
| Отвечает из общих знаний | Отвечает из **ваших документов** |
| Может выдумать факты | Цитирует **конкретные источники** |
| Не знает ваш бизнес | Знает **ваши цены, услуги, FAQ** |
| Одинаков для всех | **Настраивается** под вашу нишу |

---

## ✨ Возможности

- 📚 **Загрузка документов** — PDF и TXT (до 20MB)
- 🔍 **RAG-поиск** — ChromaDB находит релевантные фрагменты
- 💬 **Умные ответы** — DeepSeek API генерирует ответы с контекстом
- 📖 **Источники** — каждый ответ ссылается на фрагменты документа
- 🎨 **Клавиатура** — удобное меню в Telegram
- 📋 **Управление** — список документов, очистка базы
- ⚡ **Быстрый старт** — 5 минут от клонирования до запуска
- 💰 **~300₽/мес** — DeepSeek API стоит копейки

---

## 📸 Как это работает

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Загрузка   │ ──→ │  Индексация  │ ──→ │   Хранение  │
│  PDF/TXT    │     │  ChromaDB    │     │  Фрагменты  │
└─────────────┘     └──────────────┘     └─────────────┘
                                              │
                    ┌──────────────┐           │
                    │    Вопрос    │ ──────────┘
                    │   клиента    │
                    └──────────────┘
                          │
                    ┌──────────────┐     ┌─────────────┐
                    │  DeepSeek    │ ──→ │   Ответ с   │
                    │  API (LLM)   │     │  источниками│
                    └──────────────┘     └─────────────┘
```

---

## 🚀 Быстрый старт

### 1. Клонируйте

```bash
git clone https://github.com/ztystra/knowledgebot.git
cd knowledgebot
```

### 2. Установите зависимости

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Настройте

```bash
cp .env.example .env
```

Отредактируйте `.env` — вставьте ключи:

```env
DEEPSEEK_API_KEY=your_key_here
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 4. Запустите

```bash
python bot.py
```

Готово! Бот работает. Загружайте документы и задавайте вопросы.

---

## 🔧 Конфигурация

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DEEPSEEK_API_KEY` | API ключ DeepSeek | — |
| `TELEGRAM_BOT_TOKEN` | Токен Telegram-бота | — |
| `LLM_MODEL` | Модель DeepSeek | `deepseek-chat` |
| `CHROMA_DB_PATH` | Путь к ChromaDB | `./chroma_db` |
| `SYSTEM_PROMPT` | Системный промпт | Текущий |

### Кастомизация промпта

```env
SYSTEM_PROMPT=Ты юрист. Отвечай на основе загруженных документов. Цитируй статьи.
```

---

## 📖 Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Приветствие и главное меню |
| `/help` | Справка по использованию |
| `/list` | Список загруженных документов |
| `/clear` | Очистить базу знаний |
| 📚 Загрузить документ | Загрузка PDF/TXT |
| ❓ Задать вопрос | Вопрос по документам |

---

## 💰 Стоимость

| Компонент | Бесплатно | Платно |
|-----------|-----------|--------|
| DeepSeek API | 5M токенов (30 дней) | ~300₽/мес |
| Telegram Bot | Безлимитно | — |
| ChromaDB | Локально | — |

**Средний ответ:** ~500 токенов = ~$0.0001 за запрос.

---

## 🏗 Архитектура

```
knowledgebot/
├── bot.py              # Telegram-бот (обработчики команд)
├── rag_engine.py       # RAG: ChromaDB + DeepSeek
├── requirements.txt    # Зависимости
├── .env.example        # Шаблон конфигурации
├── .github/            # CI/CD и шаблоны
├── CONTRIBUTING.md     # Гайд для контрибьюторов
├── SECURITY.md         # Политика безопасности
├── CHANGELOG.md        # История изменений
└── README.md           # Эта документация
```

---

## 🤝 Контрибьюция

Смотри [CONTRIBUTING.md](CONTRIBUTING.md) для подробностей.

---

## 📝 Лицензия

[MIT License](LICENSE) — используйте как угодно.

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=ztystra/knowledgebot&type=Date)](https://star-history.com/#ztystra/knowledgebot&Date)

---

**Сделано с 💜 [Меру](https://github.com/ztystra)**
