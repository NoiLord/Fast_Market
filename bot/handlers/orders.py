"""Оформление заказа: username -> оплата -> скриншот -> подтверждение -> автовыдача."""
from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import db
import keyboards as kb
import texts
from config import PAYMENT_DETAILS
from services import notify_admins
from states import OrderStates

router = Router()


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


@router.callback_query(F.data.startswith("buy:"))
async def cb_buy(cq: CallbackQuery, state: FSMContext) -> None:
    product_id = int(cq.data.split(":")[1])
    p = db.get_product(product_id)
    if not p or not p["is_active"]:
        await cq.answer("Товар недоступен", show_alert=True)
        return
    await state.set_state(OrderStates.waiting_username)
    await state.update_data(product_id=product_id)
    await cq.message.answer(
        "📝 Напишите ваш <b>Telegram username</b> (например @username) или любой контакт, "
        "куда прислать ключ:",
        reply_markup=kb.back_to_product(product_id),
    )
    await cq.answer()


@router.message(OrderStates.waiting_username, F.text)
async def got_username(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    product_id = data["product_id"]
    p = db.get_product(product_id)
    if not p:
        await state.clear()
        await message.answer("Товар не найден.")
        return

    username = message.text.strip().replace(" ", "")
    order_id = db.create_order(
        user_id=message.from_user.id, username=username, product_id=product_id, amount=p["price"]
    )
    await state.clear()

    await message.answer(
        f"✅ <b>Заказ №{order_id} создан!</b>\n\n"
        f"📦 {_esc(p['name'])}\n"
        f"💰 Сумма: <b>{p['price']} ₽</b>\n"
        f"👤 Контакт для выдачи: {_esc(username)}\n\n"
        f"💳 <b>Оплата</b>\n{PAYMENT_DETAILS}\n\n"
        f"Введите номер заказа <b>{order_id}</b> в комментарии к переводу.\n"
        f"После оплаты нажмите кнопку ниже 🧾",
        reply_markup=kb.payed_screen(order_id),
    )


@router.callback_query(F.data.startswith("payed:"))
async def cb_payed(cq: CallbackQuery, state: FSMContext) -> None:
    order_id = int(cq.data.split(":")[1])
    order = db.get_order(order_id)
    if not order:
        await cq.answer("Заказ не найден", show_alert=True)
        return
    if order["status"] not in ("waiting_payment",):
        await cq.answer("По этому заказу оплата уже обрабатывается", show_alert=True)
        return
    await state.set_state(OrderStates.waiting_screenshot)
    await state.update_data(order_id=order_id)
    await cq.message.answer(
        "🖼 Отправьте <b>скриншот оплаты</b>.\n"
        "Менеджер проверит платёж и выдаст ключ автоматически."
    )
    await cq.answer()


@router.message(OrderStates.waiting_screenshot, F.photo)
async def got_screenshot(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    order_id = data["order_id"]
    order = db.get_order_with_product(order_id)
    if not order:
        await state.clear()
        await message.answer("Заказ не найден.")
        return

    file_id = message.photo[-1].file_id
    db.mark_payed(order_id, file_id)
    await state.clear()

    await message.answer(
        "✅ Скриншот получен!\n"
        "Заказ передан на проверку. Ключ придёт автоматически, как только менеджер подтвердит оплату 🎁"
    )

    admin_text = (
        f"🆕 <b>НОВЫЙ ЗАКАЗ №{order_id}</b>\n\n"
        f"📦 {_esc(order['product_name'])}\n"
        f"💰 {order['amount']} ₽\n"
        f"👤 Клиент: {_esc(order['username']) or order['user_id']}\n"
        f"🕐 {order['created_at']}\n\n"
        f"Скриншот оплаты ниже 👇"
    )
    await notify_admins(
        message.bot,
        admin_text,
        reply_markup=kb.admin_order_actions(order_id),
    )
    await _send_admin_photos(message.bot, file_id, order_id)


@router.message(OrderStates.waiting_screenshot)
async def got_wrong_screenshot(message: Message) -> None:
    await message.answer("📷 Пожалуйста, пришлите <b>скриншот оплаты</b> (фото). Скриншот можно сделать в приложении банка.")


@router.message(OrderStates.waiting_username)
async def got_wrong_username(message: Message) -> None:
    await message.answer("Отправьте ваш Telegram username текстом, например @your_name.")


async def _send_admin_photos(bot: Bot, file_id: str, order_id: int, caption: str = "") -> None:
    from config import ADMIN_IDS

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_photo(
                admin_id,
                file_id,
                caption=f"🧾 Скриншот оплаты к заказу №{order_id}",
            )
        except Exception:
            pass