"""Общие команды: /start, /help, мои заказы, главное меню."""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import CallbackQuery, Message

import db
import keyboards as kb
import texts
from config import ADMIN_IDS

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    payload = parts[1] if len(parts) > 1 else ""
    if payload:
        p = db.get_product_by_code(payload)
        if p:
            p["stock"] = db.count_available_keys(p["id"])
            await message.answer(
                texts.product_card(p), reply_markup=kb.product_actions(p["id"])
            )
            return
    await message.answer(texts.WELCOME, reply_markup=kb.main_menu(_is_admin(message.from_user.id)))


@router.callback_query(F.data == "menu")
async def cb_menu(cq: CallbackQuery) -> None:
    await cq.message.edit_text(
        texts.WELCOME, reply_markup=kb.main_menu(_is_admin(cq.from_user.id))
    )
    await cq.answer()


@router.message(Command("help"))
async def help_cmd(message: Message) -> None:
    await message.answer(texts.HELP, reply_markup=kb.support_button())


@router.callback_query(F.data == "help")
async def cb_help(cq: CallbackQuery) -> None:
    await cq.message.edit_text(texts.HELP, reply_markup=kb.support_button())
    await cq.answer()


@router.callback_query(F.data == "my_orders")
async def cb_my_orders(cq: CallbackQuery) -> None:
    orders = db.list_orders(user_id=cq.from_user.id, limit=15)
    if not orders:
        await cq.message.edit_text(
            "📋 У вас пока нет заказов.\nОткройте каталог и выберите товар 👇",
            reply_markup=kb.categories_menu(db.list_categories()),
        )
        await cq.answer()
        return
    lines = ["📋 <b>Ваши заказы</b>\n"]
    for o in orders:
        lines.append(texts.order_card(o))
        lines.append("—" * 28)
    await cq.message.edit_text("\n".join(lines), reply_markup=kb.categories_menu(db.list_categories()))
    await cq.answer()