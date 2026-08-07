from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    waiting_username = State()
    waiting_screenshot = State()


class AdminStates(StatesGroup):
    add_product_category = State()
    add_product_name = State()
    add_product_price = State()
    add_product_desc = State()
    add_keys_product = State()
    add_keys_values = State()
    manual_delivery = State()
