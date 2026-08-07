"""Прокси-модуль для инлайн-каталога и покупки."""
from aiogram import Router, F
from aiogram.types import CallbackQuery

import db
import keyboards as kb
import texts

router = Router()


@router.callback_query(F.data == "catalog:0")
async def cb_catalog(cq: CallbackQuery) -> None:
    await cq.message.edit_text(
        "🛍 <b>Каталог</b>\nВыберите категорию:", reply_markup=kb.categories_menu(db.list_categories())
    )
    await cq.answer()


@router.callback_query(F.data.startswith("cat:"))
async def cb_category(cq: CallbackQuery) -> None:
    category_id = int(cq.data.split(":")[1])
    products = db.list_products(category_id)
    if not products:
        await cq.answer("В этой категории пока нет товаров 👀", show_alert=True)
        return
    await cq.message.edit_text(
        "Выберите товар:",
        reply_markup=kb.products_menu(products, category_id),
    )
    await cq.answer()


@router.callback_query(F.data.startswith("prod:"))
async def cb_product(cq: CallbackQuery) -> None:
    product_id = int(cq.data.split(":")[1])
    p = db.get_product(product_id)
    if not p:
        await cq.answer("Товар не найден", show_alert=True)
        return
    p["stock"] = db.count_available_keys(product_id)
    await cq.message.edit_text(texts.product_card(p), reply_markup=kb.product_actions(product_id))
    await cq.answer()