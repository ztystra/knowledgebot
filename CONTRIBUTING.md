# Contributing

Спасибо за интерес к проекту!

## Быстрый старт

1. Fork репозитория
2. `git clone https://github.com/YOUR_USERNAME/knowledgebot.git`
3. `python3 -m venv venv && source venv/bin/activate`
4. `pip install -r requirements.txt`
5. `cp .env.example .env` — заполнить ключи
6. `python bot.py`

## Разработка

- Код: `bot.py` (бот), `rag_engine.py` (RAG логика)
- Линтер: `flake8`, `black`, `isort`
- Тесты: `pytest tests/`

## Pull Request

1. Создайте ветку `feature/your-feature`
2. Внесите изменения
3. Убедитесь что `flake8` и `black` проходят
4. Отправьте PR с описанием изменений

## Вопросы?

Откройте issue — обсудим!
