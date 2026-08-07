"""Общие тексты и картинки для бота."""
from config import PAYMENT_DETAILS, SUPPORT_USERNAME, BOT_USERNAME

WELCOME = (
    "🎮 Добро пожаловать в <b>FAST GAME</b>!\n\n"
    "Надёжные и легальные подписки Xbox Game Pass Ultimate / Game Pass / EA Play / Xbox Live Gold, "
    "игры, аккаунты и СММ — всё под ключ. ⚡\n\n"
    "✔️ Мгновенная автовыдача ключей после подтверждения оплаты\n"
    "✔️ Подключаем подписку на ваш личный аккаунт\n"
    "✔️ Поддержка 24/7\n\n"
    "Выберите действие в меню ниже 👇"
)

HELP = (
    "🆘 <b>Помощь</b>\n\n"
    "1️⃣ Откройте «🛍 Каталог» и выберите товар.\n"
    "2️⃣ Нажмите «Купить» — бот создаст заказ.\n"
    "3️⃣ Оплатите переводом по реквизитам и нажмите «Я оплатил».\n"
    "4️⃣ Пришлите скриншот оплаты — менеджер проверит.\n"
    "5️⃣ После подтверждения ключ придёт автоматически 🔑\n\n"
    f"Реквизиты для оплаты:\n{PAYMENT_DETAILS}\n\n"
)

ORDER_NOT_FOUND = "Заказ не найден."


def product_card(p) -> str:
    return (
        f"<b>{p['name']}</b>\n\n"
        f"{p['description'] or 'Описание отсутствует'}\n\n"
        f"💰 Цена: <b>{p['price']} ₽</b>\n"
        f"📦 Осталось ключей: <b>{p.get('stock', '—')}</b>"
    )


def order_card(o) -> str:
    status = {
        "waiting_payment": "💰 Ожидает оплаты",
        "processing": "⏳ Ожидает подтверждения",
        "paid": "✅ Оплачен",
        "done": "🎁 Выдан",
        "cancelled": "❌ Отменён",
    }.get(o["status"], o["status"])
    return (
        f"🧾 Заказ №{o['id']}\n"
        f"📦 Товар: {o['product_name']}\n"
        f"💰 Сумма: {o['amount']} ₽\n"
        f"👤 Клиент: {o['username'] or o['user_id']}\n"
        f"🕐 Создан: {o['created_at']}\n"
        f"📌 Статус: {status}"
    )


def support_link() -> str:
    return f"https://t.me/{SUPPORT_USERNAME}" if SUPPORT_USERNAME else f"https://t.me/{BOT_USERNAME}"

BOT_LINK = f"https://t.me/{BOT_USERNAME}"
