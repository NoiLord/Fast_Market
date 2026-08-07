# Fast_Market — fast-game.ru

Магазин цифровых товаров: ✅ подписки Xbox Game Pass Ultimate / Game Pass / EA Play / Xbox Live Gold, игры, аккаунты и СММ — всё под ключ. Подключаем на ваш личный аккаунт.

## Структура

- `index.html` — лендинг магазина (FAST GAME): тарифы, аккаунты, СММ, гарантии, FAQ, кнопки «Купить» открывают Telegram-бота с выбранным товаром (`?start=<code>`).
- `privacy.html`, `terms.html` — политика и условия.
- `bot/` — **Telegram-бот магазина** (Python / aiogram). Каталог, заказы, ручная оплата, автовыдача ключей, админ-панель. Подробнее: `bot/README.md`.

## Быстрый старт бота

```bash
cd bot
python -m pip install -r requirements.txt
copy .env.example .env   # заполнить BOT_TOKEN, ADMIN_IDS, реквизиты
python main.py
```

## Связь сайта и бота

Кнопки «Купить» на сайте ведут в бота со start-параметром, например:
`https://t.me/Fast_Market_Games_BOT?start=gpu_3m`. Код товара задаётся в боте
(сид в `bot/db.py` или через админ-панель «➕ Добавить товар»).