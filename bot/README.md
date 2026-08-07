# 🤖 Telegram-бот для FAST GAME

Автоматический магазин: каталог, заказ, ручная оплата (скриншот), подтверждение
менеджером и **автовыдача ключа** клиенту.

## Возможности

- 🛍 Каталог с категориями и товарами (Game Pass, игры/аккаунты, СММ)
- 🛒 Оформление заказа: клиент оставляет контакт → видит реквизиты → шлёт скриншот
- ⚙️ Админ-панель (`/admin`): подтверждение/отмена заказов, добавление товаров и ключей, статистика
- 🔑 Автовыдача ключа после подтверждения оплаты
- 🔗 Deep-ссылки с сайта: `https://t.me/<бот>?start=<code>` сразу открывают нужный товар

## Установка и запуск

```bash
cd bot
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Настройка:

```bash
copy .env.example .env        # Windows
# отредактируйте .env: BOT_TOKEN (от @BotFather), ADMIN_IDS, PAYMENT_DETAILS и т.д.
```

Запуск:

```bash
python main.py
```

## .env

| Переменная | Описание |
|---|---|
| `BOT_TOKEN` | Токен от @BotFather |
| `ADMIN_IDS` | ID админов через запятую (узнать: @userinfobot) |
| `PAYMENT_DETAILS` | Текст с реквизитами, показывается клиенту при оплате |
| `SUPPORT_USERNAME` | Ник поддержки (без @), кнопка «Поддержка» |
| `BOT_USERNAME` | Ник бота (без @), используется в deep-ссылках |

## Как это работает

1. Клиент открывает бота (`/start` или по ссылке `?start=gpu_3m`), выбирает товар → «Купить»
2. Указывает контакт → получает номер заказа и реквизиты → платит
3. Жмёт «Я оплатил» и присылает скриншот — заявка уходит админам
4. Админ в чате нажимает «✅ Подтвердить» → бот сам выдаёт первый свободный ключ клиенту 🔑

## Связь с сайтом

На страницах «Купить» используются ссылки вида
`https://t.me/<BOT_USERNAME>?start=<code>` (например `gpu_3m`).
Код товара виден в админке: «🗂 Товары → товар».

## Деплой

Скопируйте папку `bot` на VPS/хостинг, запустите через `systemd`:

```ini
[Unit]
Description=Fast Game Bot
After=network.target

[Service]
WorkingDirectory=/opt/fast-game/bot
ExecStart=/opt/fast-game/bot/.venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Либо используйте бесплатный хостинг **Railway / Render** (start command: `python main.py`).