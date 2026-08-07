"""Простая обёртка над sqlite3 для бота."""
import sqlite3
import threading
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "store.db")

_lock = threading.Lock()


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    emoji TEXT DEFAULT '🎮'
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    code TEXT UNIQUE,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    price INTEGER NOT NULL,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY(category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    value TEXT NOT NULL,
    status TEXT DEFAULT 'available',
    FOREIGN KEY(product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    username TEXT DEFAULT '',
    product_id INTEGER NOT NULL,
    status TEXT DEFAULT 'waiting_payment',
    amount INTEGER,
    screenshot_file_id TEXT DEFAULT '',
    comment TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    confirmed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_keys_status ON keys(status);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
"""


def init_db() -> None:
    with _lock:
        conn = get_conn()
        conn.executescript(SCHEMA)
        conn.commit()
        conn.close()


# ---------------------------------------------------------------- категории

def list_categories() -> list:
    with _lock:
        conn = get_conn()
        rows = conn.execute("SELECT * FROM categories ORDER BY id").fetchall()
        conn.close()
        return [dict(r) for r in rows]


def get_product_by_code(code: str):
    with _lock:
        conn = get_conn()
        row = conn.execute("SELECT * FROM products WHERE code = ?", (code,)).fetchone()
        conn.close()
        return dict(row) if row else None


def get_category(cid: int):
    with _lock:
        conn = get_conn()
        row = conn.execute("SELECT * FROM categories WHERE id = ?", (cid,)).fetchone()
        conn.close()
        return dict(row) if row else None


def get_product(pid: int):
    with _lock:
        conn = get_conn()
        row = conn.execute("SELECT * FROM products WHERE id = ?", (pid,)).fetchone()
        conn.close()
        return dict(row) if row else None


def list_products(category_id: int, active_only: bool = True) -> list:
    with _lock:
        conn = get_conn()
        sql = "SELECT * FROM products WHERE category_id = ?"
        args = [category_id]
        if active_only:
            sql += " AND is_active = 1"
        sql += " ORDER BY price"
        rows = conn.execute(sql, args).fetchall()
        conn.close()
        return [dict(r) for r in rows]


def list_all_products() -> list:
    with _lock:
        conn = get_conn()
        rows = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
        conn.close()
        return [dict(r) for r in rows]


def add_category(name: str, emoji: str = "🎮") -> int:
    with _lock:
        conn = get_conn()
        cur = conn.execute("INSERT INTO categories (name, emoji) VALUES (?, ?)", (name, emoji))
        conn.commit()
        cid = cur.lastrowid
        conn.close()
        return cid


def delete_category(cid: int) -> None:
    with _lock:
        conn = get_conn()
        conn.execute("DELETE FROM categories WHERE id = ?", (cid,))
        conn.commit()
        conn.close()


# ---------------------------------------------------------------- товары

def add_product(category_id: int, name: str, price: int, code: str = None, description: str = "") -> int:
    with _lock:
        conn = get_conn()
        cur = conn.execute(
            "INSERT INTO products (category_id, code, name, description, price) VALUES (?, ?, ?, ?, ?)",
            (category_id, code, name, description, price),
        )
        conn.commit()
        pid = cur.lastrowid
        conn.close()
        return pid


def set_product_active(pid: int, active: int) -> None:
    with _lock:
        conn = get_conn()
        conn.execute("UPDATE products SET is_active = ? WHERE id = ?", (active, pid))
        conn.commit()
        conn.close()


# ---------------------------------------------------------------- ключи

def insert_key(product_id: int, value: str) -> None:
    with _lock:
        conn = get_conn()
        conn.execute("INSERT INTO keys (product_id, value) VALUES (?, ?)", (product_id, value))
        conn.commit()
        conn.close()


def insert_keys_bulk(product_id: int, values: list) -> None:
    with _lock:
        conn = get_conn()
        conn.executemany(
            "INSERT INTO keys (product_id, value) VALUES (?, ?)",
            [(product_id, v) for v in values if v.strip()],
        )
        conn.commit()
        conn.close()


def take_available_key(product_id: int):
    """Достаёт первый свободный ключ и помечает его как выданный."""
    with _lock:
        conn = get_conn()
        row = conn.execute(
            "SELECT id, value FROM keys WHERE product_id = ? AND status = 'available' ORDER BY id LIMIT 1",
            (product_id,),
        ).fetchone()
        if row:
            conn.execute("UPDATE keys SET status = 'used' WHERE id = ?", (row["id"],))
            conn.commit()
            conn.close()
            return row["value"]
        conn.close()
        return None


def count_available_keys(product_id: int) -> int:
    with _lock:
        conn = get_conn()
        n = conn.execute(
            "SELECT COUNT(*) FROM keys WHERE product_id = ? AND status = 'available'", (product_id,)
        ).fetchone()[0]
        conn.close()
        return n


# ---------------------------------------------------------------- заказы

STATUSES = {
    "waiting_payment": "💰 Ожидает оплаты",
    "processing": "⏳ Ожидает подтверждения",
    "paid": "✅ Оплачен",
    "done": "🎁 Выдан",
    "cancelled": "❌ Отменён",
}


def create_order(user_id: int, username: str, product_id: int, amount: int) -> int:
    with _lock:
        conn = get_conn()
        cur = conn.execute(
            "INSERT INTO orders (user_id, username, product_id, status, amount) VALUES (?, ?, ?, 'waiting_payment', ?)",
            (user_id, username, product_id, amount),
        )
        conn.commit()
        oid = cur.lastrowid
        conn.close()
        return oid


def get_order(oid: int):
    with _lock:
        conn = get_conn()
        row = conn.execute("SELECT * FROM orders WHERE id = ?", (oid,)).fetchone()
        conn.close()
        return dict(row) if row else None


def get_order_with_product(oid: int):
    with _lock:
        conn = get_conn()
        row = conn.execute(
            """SELECT o.*, p.name AS product_name
               FROM orders o JOIN products p ON p.id = o.product_id
               WHERE o.id = ?""",
            (oid,),
        ).fetchone()
        conn.close()
        return dict(row) if row else None


def mark_payed(oid: int, screenshot_file_id: str) -> None:
    with _lock:
        conn = get_conn()
        conn.execute(
            "UPDATE orders SET status = 'processing', screenshot_file_id = ? WHERE id = ?",
            (screenshot_file_id, oid),
        )
        conn.commit()
        conn.close()


def set_order_status(oid: int, status: str) -> None:
    with _lock:
        conn = get_conn()
        if status == "paid":
            conn.execute(
                "UPDATE orders SET status = ?, confirmed_at = datetime('now', 'localtime') WHERE id = ?",
                (status, oid),
            )
        else:
            conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, oid))
        conn.commit()
        conn.close()


def list_orders(status: str = None, user_id: int = None, limit: int = 30) -> list:
    with _lock:
        conn = get_conn()
        sql = """SELECT o.*, p.name AS product_name
                 FROM orders o JOIN products p ON p.id = o.product_id"""
        where, args = [], []
        if status:
            where.append("o.status = ?")
            args.append(status)
        if user_id:
            where.append("o.user_id = ?")
            args.append(user_id)
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY o.id DESC LIMIT ?"
        args.append(limit)
        rows = conn.execute(sql, args).fetchall()
        conn.close()
        return [dict(r) for r in rows]


def stats():
    with _lock:
        conn = get_conn()
        row = conn.execute(
            "SELECT COUNT(*) AS total, "
            "COUNT(CASE WHEN status IN ('paid','done') THEN 1 END) AS paid_count, "
            "COALESCE(SUM(CASE WHEN status IN ('paid','done') THEN amount ELSE 0 END), 0) AS revenue "
            "FROM orders"
        ).fetchone()
        conn.close()
        return dict(row)


# ---------------------------------------------------------------- наполнение по умолчанию

DEFAULT_CATEGORIES = [
    ("⚡ Game Pass", "⚡"),
    ("🎮 Игры и аккаунты", "🎮"),
    ("📈 СММ накрутка", "📈"),
]

DEFAULT_PRODUCTS = [
    # (category_index, code, name, price, description)
    (0, "gpu_1m", "Xbox Game Pass Ultimate — 1 месяц", 900,
     "Более 450 игр. Консоль + ПК. Мультиплеер. EA Play включён. Активация на ваш аккаунт."),
    (0, "gpu_3m", "Xbox Game Pass Ultimate — 3 месяца", 2500,
     "Более 450 игр. Консоль + ПК. Мультиплеер. EA Play включён. Эксклюзивные скидки. Приоритетная поддержка."),
    (0, "gpu_6m", "Xbox Game Pass Ultimate — 6 месяцев", 4800,
     "Более 450 игр. Консоль + ПК. Мультиплеер. EA Play включён. Персональный менеджер."),
    (0, "gpu_12m", "Xbox Game Pass Ultimate — 12 месяцев", 9600,
     "VIP-статус + 1 игра в подарок. Персональный менеджер. Максимальная выгода."),
    (1, "gta5_sc", "GTA 5 (Social Club)", 650, "Лицензионный аккаунт с игрой. Смена данных. Гарантия."),
    (1, "gta5_steam", "GTA 5 (Steam)", 1000, "Лицензионный ключ для активации в Steam. Гарантия."),
    (1, "rdr2_sc", "Red Dead Redemption 2 (Social Club)", 500,
     "Лицензионный аккаунт. Смена данных. Гарантия."),
    (1, "gta5_rdr2", "GTA 5 + RDR 2 (Social Club)", 1000, "Два аккаунта. Смена данных. Гарантия."),
    (1, "gta5_money", "GTA 5: аккаунт с 3 млрд валюты", 2500,
     "Аккаунт с деньгами, Social Club. Гарантия."),
    (2, "smm_subs", "1000 подписчиков Telegram", 100, "Навсегда. Без ботов. Быстро."),
    (2, "smm_reactions", "1000 реакций Telegram", 100, "Навсегда. Реальные. Быстро."),
]


def seed_if_empty() -> None:
    with _lock:
        conn = get_conn()
        if conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 0:
            held = {}
            for i, (name, emoji) in enumerate(DEFAULT_CATEGORIES):
                cur = conn.execute("INSERT INTO categories (name, emoji) VALUES (?, ?)", (name, emoji))
                held[i] = cur.lastrowid
            for ci, code, name, price, desc in DEFAULT_PRODUCTS:
                conn.execute(
                    "INSERT INTO products (category_id, code, name, description, price) VALUES (?, ?, ?, ?, ?)",
                    (held[ci], code, name, desc, price),
                )
            conn.commit()
        conn.close()