import sqlite3
import time
import random
from constants import DB_NAME

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS ordini")
    cursor.execute("""
        CREATE TABLE ordini (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT,
            pizza TEXT,
            prezzo REAL,
            stato TEXT,
            ora TEXT
        )
    """)
    conn.commit()
    conn.close()

def orders_simulation():
    pizze = [
        ("Margherita", 6.00),
        ("Diavola", 6.50),
        ("Pistacchiosa", 8.50),
        ("Capricciosa", 7.00),
        ("Ortolana", 6.00)
    ]
    clienti = ["Mario", "Giulia", "Luca", "Sofia", "Antonio", "Elena", "Alfonso", "Francesco", "Marica", "Noemi"]

    while True:
        time.sleep(random.randint(2, 4))
        cliente = random.choice(clienti)
        pizza, prezzo = random.choice(pizze)
        ora = time.strftime("%H:%M:%S")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ordini (cliente, pizza, prezzo, stato, ora) VALUES (?, ?, ?, 'In preparazione', ?)",
            (cliente, pizza, prezzo, ora)
        )

        conn.commit()
        conn.close()

def order_delivery_simulation():
    while True:
        time.sleep(random.randint(10, 20))
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE ordini SET stato = 'Consegnato' WHERE id = (
                SELECT id FROM ordini WHERE stato = 'In preparazione' ORDER BY id LIMIT 1
            )
            """
        )
        conn.commit()
        conn.close()
        