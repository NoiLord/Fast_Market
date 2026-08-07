"""Админ-панель: подтверждение заказов, автовыдача ключей, управление товарами."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import db
import keyboards as kb
from config import PAYMENT_DETAILS
from filters import IsAdmin
from states import AdminStates

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- панель

@router.message(Command("admin"))
async def admin_cmd(message: Message) -> None:
    await message.answer("⚙️ <b>Админ-панель</b>", reply_markup=kb.admin_panel())


@router.callback_query(F.data == "admin:panel")
async def cb_admin_panel(cq: CallbackQuery) -> None:
    await cq.message.edit_text("⚙️ <b>Админ-панель</b>", reply_markup=kb.admin_panel())
    await cq.answer()


@router.callback_query(F.data == "admin:stats")
async def cb_admin_stats(cq: CallbackQuery) -> None:
    s = db.stats()
    await cq.message.edit_text(
        f"📊 <b>Статистика</b>\n\n"
        f"Всего заказов: <b>{s['total']}</b>\n"
        f"Оплаченных: <b>{s['paid_count']}</b>\n"
        f"Выручка: <b>{s['revenue']} ₽</b>",
        reply_markup=kb.admin_panel(),
    )
    await cq.answer()


# ---------------------------------------------------------------- заявки

@router.callback_query(F.data == "admin:orders")
async def cb_admin_orders(cq: CallbackQuery) -> None:
    orders = db.list_orders(status="processing") + db.list_orders(status="waiting_payment")
    orders = {o["id"]: o for o in orders}.values()
    if not orders:
        await cq.message.edit_text("📦 Новых заявок нет.", reply_markup=kb.admin_panel())
        await cq.answer()
        return
    lines = ["📦 <b>Заявки</b>\n"]
    for o in list(orders)[:20]:
        lines.append(db_status_line(o))
    lines.append("\nНажмите кнопку под заявкой, чтобы подтвердить или отменить.")
    await cq.message.edit_text("\n".join(lines), reply_markup=kb.admin_panel())
    await cq.answer()


def db_status_line(o: dict) -> str:
    st = {
        "waiting_payment": "💰 не оплачен",
        "processing": "⏳ ждёт проверки",
        "paid": "✅ оплачен",
        "done": "🎁 выдан",
        "cancelled": "❌ отменён",
    }.get(o["status"], o["status"])
    return (
        f"#{o['id']} {o['product_name']} | {o['amount']}₽ | {st}\n"
        f"   👤 {o['username'] or o['user_id']} | {o['created_at']}"
    )


@router.callback_query(F.data.startswith("admin_confirm:"))
async def cb_admin_confirm(cq: CallbackQuery) -> None:
    order_id = int(cq.data.split(":")[1])
    order = db.get_order_with_product(order_id)
    if not order:
        await cq.answer("Заказ не найден", show_alert=True)
        return

    key = db.take_available_key(order["product_id"])
    db.set_order_status(order_id, "paid")

    if key:
        db.set_order_status(order_id, "done")
        try:
            await cq.bot.send_message(
                order["user_id"],
                f"🎁 <b>Заказ №{order_id} подтверждён!</b>\n\n"
                f"📦 {_esc(order['product_name'])}\n\n"
                f"🔑 <b>Ваш ключ:</b>\n<code>{key}</code>\n\n"
                "Спасибо за покупку! Если нужна помощь — напишите в поддержку 🆘",
            )
        except Exception:
            pass
        await cq.message.answer(
            f"✅ Заказ №{order_id} подтверждён, ключ отправлен клиенту:\n<code>{key}</code>"
        )
    else:
        try:
            await cq.bot.send_message(
                order["user_id"],
                f"✅ <b>Заказ №{order_id} оплачен!</b> "
                "Ключ выдаст менеджер в ближайшее время, следите за сообщениями 🙌",
            )
        except Exception:
            pass
        await cq.message.answer(
            f"⚠️ <b>Заказ №{order_id}</b>: оплата подтверждена, но свободных ключей нет.\n"
            "Добавьте ключи через админ-панель и выдайте клиенту вручную."
        )

    await cq.message.answer(f"👤 Сумма: {order['amount']} ₽. {PAYMENT_DETAILS}")
    await cq.answer()


@router.callback_query(F.data.startswith("admin_cancel:"))
async def cb_admin_cancel(cq: CallbackQuery) -> None:
    order_id = int(cq.data.split(":")[1])
    order = db.get_order_with_product(order_id)
    db.set_order_status(order_id, "cancelled")
    if order:
        try:
            await cq.bot.send_message(
                order["user_id"],
                f"❌ <b>Заказ №{order_id}</b> отклонён.\n"
                "Если вы оплачивали — напишите в поддержку для возврата средств.",
            )
        except Exception:
            pass
    await cq.message.answer(f"Заказ №{order_id} отменён.")
    await cq.answer()


# ---------------------------------------------------------------- товары

@router.callback_query(F.data == "admin:products")
async def cb_admin_products(cq: CallbackQuery) -> None:
    products = db.list_all_products()
    if not products:
        await cq.message.edit_text("Товаров пока нет.", reply_markup=kb.admin_products_menu())
        await cq.answer()
        return
    text = "🗂 <b>Товары</b>\n\n"
    for p in products:
        stock = db.count_available_keys(p["id"])
        mark = "✅" if p["is_active"] else "🚫"
        text += f"{mark} {_esc(p['name'])} — {p['price']}₽ (ключей: {stock})\n"
    await cq.message.edit_text(text, reply_markup=kb.admin_products_list(products))
    await cq.answer()


@router.callback_query(F.data.startswith("admin_prod:"))
async def cb_admin_prod(cq: CallbackQuery) -> None:
    product_id = int(cq.data.split(":")[1])
    p = db.get_product(product_id)
    if not p:
        await cq.answer("Товар не найден", show_alert=True)
        return
    stock = db.count_available_keys(product_id)
    await cq.message.edit_text(
        f"{'✅' if p['is_active'] else '🚫'} <b>{_esc(p['name'])}</b>\n"
        f"Цена: {p['price']} ₽\n"
        f"Код для ссылки: {p['code']}\n"
        f"Свободных ключей: {stock}",
        reply_markup=kb.admin_product_actions(product_id),
    )
    await cq.answer()


@router.callback_query(F.data.startswith("admin_toggle:"))
async def cb_admin_toggle(cq: CallbackQuery) -> None:
    product_id = int(cq.data.split(":")[1])
    p = db.get_product(product_id)
    if p:
        db.set_product_active(product_id, 0 if p["is_active"] else 1)
        await cb_admin_prod(cq)


# ---------------------------------------------------------------- добавление ключей

@router.callback_query(F.data.startswith("admin_keys:"))
async def cb_admin_keys(cq: CallbackQuery, state: FSMContext) -> None:
    product_id = int(cq.data.split(":")[1])
    await state.set_state(AdminStates.add_keys_values)
    await state.update_data(add_keys_product=product_id)
    await cq.message.answer(
        "🔑 Пришлите ключи, каждый с новой строки.\n"
        "Первая строка — порядок выдачи. Отправьте /cancel чтобы выйти."
    )
    await cq.answer()


@router.message(AdminStates.add_keys_values, F.text)
async def got_admin_keys(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    product_id = data["add_keys_product"]
    values = [v.strip() for v in message.text.splitlines() if v.strip()]
    if not values:
        await message.answer("Пусто. Отправьте ключи строками.")
        return
    db.insert_keys_bulk(product_id, values)
    await state.clear()
    await message.answer(f"✅ Добавлено ключей: {len(values)}", reply_markup=kb.admin_panel())


# ---------------------------------------------------------------- добавление товара

@router.callback_query(F.data == "admin:add_product")
async def cb_admin_add_product(cq: CallbackQuery, state: FSMContext) -> None:
    categories = db.list_categories()
    await state.set_state(AdminStates.add_product_category)
    text = "В какую категорию добавить товар? Ответьте номером:\n"
    for c in categories:
        text += f"{c['id']}. {c['emoji']} {c['name']}\n"
    await cq.message.answer(text)
    await cq.answer()


@router.message(AdminStates.add_product_category, F.text)
async def got_admin_cat(message: Message, state: FSMContext) -> None:
    try:
        cid = int(message.text.strip())
    except ValueError:
        await message.answer("Введите номер категории цифрами.")
        return
    if not db.get_category(cid):
        await message.answer("Категории с таким номером нет. Попробуйте ещё раз.")
        return
    await state.update_data(add_product_category=cid)
    await state.set_state(AdminStates.add_product_name)
    await message.answer("Название товара:")


@router.message(AdminStates.add_product_name, F.text)
async def got_admin_name(message: Message, state: FSMContext) -> None:
    await state.update_data(add_product_name=message.text.strip())
    await state.set_state(AdminStates.add_product_price)
    await message.answer("Цена в рублях (только число):")


@router.message(AdminStates.add_product_price, F.text)
async def got_admin_price(message: Message, state: FSMContext) -> None:
    try:
        price = int(message.text.strip())
    except ValueError:
        await message.answer("Введите цену числом, например: 900")
        return
    await state.update_data(add_product_price=price)
    await state.set_state(AdminStates.add_product_desc)
    await message.answer("Описание товара (одна строка, или отправьте «-» чтобы пропустить):")


@router.message(AdminStates.add_product_desc, F.text)
async def got_admin_desc(message: Message, state: FSMContext) -> None:
    if message.text.strip() not in ("-",):
        await state.update_data(add_product_desc=message.text.strip())
    else:
        await state.update_data(add_product_desc="")
    data = await state.get_data()
    code = _make_code(data["add_product_name"])
    if db.get_product_by_code(code):
        code = code + "_" + str(db.get_product_by_code(code)["id"])
    pid = db.add_product(
        category_id=data["add_product_category"],
        name=data["add_product_name"],
        price=data["add_product_price"],
        code=code,
        description=data["add_product_desc"],
    )
    await state.clear()
    await message.answer(
        f"✅ Товар добавлен!\n"
        f"Ссылка с выбором товара: https://t.me/{BOT_USERNAME}?start={code}\n"
        f"Код для «Купить» на сайте: {code}\n\nТеперь можно добавить ключи.",
        reply_markup=kb.admin_panel(),
    )


def _make_code(name: str) -> str:
    import re
    code = re.sub(r"[^a-z0-9]+", "_", name.lower())
    return code.strip("_")[:32] or "item"


from config import BOT_USERNAME  # noqa: E402