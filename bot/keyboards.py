"""Клавиатуры бота."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import SUPPORT_USERNAME


# ---------------------------------------------------------------- главное меню

def main_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🛍 Каталог", callback_data="catalog:0"))
    b.row(
        InlineKeyboardButton(text="📋 Мои заказы", callback_data="my_orders"),
        InlineKeyboardButton(text="🆘 Помощь", callback_data="help"),
    )
    b.row(InlineKeyboardButton(text="📣 Новости", url="https://t.me/No_i_Lord"))
    if is_admin:
        b.row(InlineKeyboardButton(text="⚙️ Админ-панель", callback_data="admin:panel"))
    return b.as_markup()


def categories_menu(categories: list) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for c in categories:
        b.row(InlineKeyboardButton(text=f"{c['emoji']} {c['name']}", callback_data=f"cat:{c['id']}"))
    b.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu"))
    return b.as_markup()


def products_menu(products: list, category_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for p in products:
        b.row(InlineKeyboardButton(text=f"{p['name']} — {p['price']} ₽", callback_data=f"prod:{p['id']}"))
    b.row(InlineKeyboardButton(text="🔙 Назад", callback_data="catalog:0"))
    return b.as_markup()


def product_actions(product_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🛒 Купить", callback_data=f"buy:{product_id}"))
    b.row(InlineKeyboardButton(text="🔙 Назад", callback_data="catalog:0"))
    return b.as_markup()


def confirm_order(order_id: int, product_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="✅ Да, подтверждаю", callback_data=f"confirm_yes:{order_id}"))
    b.row(
        InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_order:{order_id}"),
        InlineKeyboardButton(text="🔙 В каталог", callback_data="catalog:0"),
    )
    return b.as_markup()


def payed_screen(order_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="💸 Я оплатил(а)", callback_data=f"payed:{order_id}"))
    b.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu"))
    return b.as_markup()


def support_button() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    if SUPPORT_USERNAME:
        b.row(InlineKeyboardButton(text="👤 Связаться с поддержкой", url=f"https://t.me/{SUPPORT_USERNAME}"))
    return b.as_markup()


def back_to_product(product_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🔙 К товару", callback_data=f"prod:{product_id}"))
    return b.as_markup()


# ---------------------------------------------------------------- админка

def admin_panel() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="📦 Новые заявки", callback_data="admin:orders"))
    b.row(InlineKeyboardButton(text="🗂 Товары", callback_data="admin:products"))
    b.row(InlineKeyboardButton(text="➕ Добавить товар", callback_data="admin:add_product"))
    b.row(InlineKeyboardButton(text="🔑 Добавить ключи", callback_data="admin:add_keys"))
    b.row(InlineKeyboardButton(text="📊 Статистика", callback_data="admin:stats"))
    b.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu"))
    return b.as_markup()


def admin_products_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🔙 Админ-панель", callback_data="admin:panel"))
    b.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu"))
    return b.as_markup()


def admin_order_actions(order_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"admin_confirm:{order_id}"))
    b.row(InlineKeyboardButton(text="❌ Отменить", callback_data=f"admin_cancel:{order_id}"))
    return b.as_markup()


def admin_products_list(products: list) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for p in products:
        mark = "✅" if p["is_active"] else "🚫"
        b.row(
            InlineKeyboardButton(
                text=f"{mark} {p['name']} — {p['price']} ₽", callback_data=f"admin_prod:{p['id']}"
            )
        )
    b.row(InlineKeyboardButton(text="🔙 Админ-панель", callback_data="admin:panel"))
    return b.as_markup()


def admin_product_actions(product_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🔑 Добавить ключи", callback_data=f"admin_keys:{product_id}"))
    b.row(InlineKeyboardButton(text="🔁 Вкл/Выкл", callback_data=f"admin_toggle:{product_id}"))
    b.row(InlineKeyboardButton(text="🔙 К товарам", callback_data="admin:products"))
    return b.as_markup()
