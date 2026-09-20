import sqlite3
import threading
import time
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.console import Console
from constants import DB_NAME, ORDER_LIMIT
from db import init_db, orders_simulation, order_delivery_simulation

console = Console()

def generate_dashboard():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Ordini in preparazione
    cursor.execute(f"SELECT id, ora, cliente, pizza, prezzo FROM ordini WHERE stato = 'In preparazione' ORDER BY id LIMIT {ORDER_LIMIT}")
    prossimi_ordini = cursor.fetchall()

    # Incasso e totale ordini
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(prezzo), 0) FROM ordini")
    totale_ordini, incasso_totale = cursor.fetchone()

    # Ordini Consegnati
    cursor.execute("SELECT COUNT(*) FROM ordini WHERE stato = 'Consegnato'")
    ordini_consegnati = cursor.fetchone()[0]

    # Pizza più venduta
    cursor.execute("SELECT pizza, COUNT(*) as qty FROM ordini GROUP BY pizza ORDER BY qty DESC LIMIT 1")
    top_pizza_row = cursor.fetchone()
    top_pizza = top_pizza_row[0] if top_pizza_row else "Nessuna"

    conn.close()

    layout = Layout() 
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body", ratio=1),
        Layout(name="footer", size=3)
    )
    layout["body"].split_row(
        Layout(name="ordini", ratio=2),
        Layout(name="stats", ratio=1)
    )
    layout["header"].update(
        Panel("[bold white on red] DASHBOARD PIZZERIA [/]", style="red")
    )

    tabella = Table(title="Prossimi Ordini", expand=True)
    tabella.add_column("ID", style="dim", width=5)
    tabella.add_column("Ora", style="cyan")
    tabella.add_column("Cliente", style="bold yellow")
    tabella.add_column("Pizza", style="bold green")
    tabella.add_column("Prezzo", style="magenta")

    for i, o in enumerate(prossimi_ordini):
        stile = "white on yellow" if i == 0 else None
        tabella.add_row(str(o[0]), o[1], o[2], o[3], f"€ {o[4]:.2f}", style=stile)

    layout["ordini"].update(Panel(tabella, title="[bold]Monitor Cucina[/]"))
    layout["stats"].update(
        Panel(
            f"[bold yellow]Totale Ordini: [/]{totale_ordini}\n\n"
            f"[bold magenta]Ordini Consegnati: [/]{ordini_consegnati}\n\n"
            f"[bold green]Incasso Totale: [/]€ {incasso_totale:.2f}\n\n"
            f"[bold cyan]Pizza più venduta: [/]{top_pizza}",
            title="[bold]Monitor Cassa[/]"
        )
    )
    ora_live = time.strftime("%H:%M:%S")
    layout["footer"].update(
        Panel(f"[dim]Database: {DB_NAME} | Aggiornato alle {ora_live} | Premi CTRL + C per fermare[/]", style="grey50")
    )

    return layout

if __name__ == "__main__":
    init_db()

    t1 = threading.Thread(target=orders_simulation, daemon=True)
    t2 = threading.Thread(target=order_delivery_simulation, daemon=True)
    t1.start()
    t2.start()

    with Live(generate_dashboard(), refresh_per_second=2, screen=True) as live:
        try:
            while True:
                time.sleep(0.5)
                live.update(generate_dashboard())
        except KeyboardInterrupt:
            console.print("[bold red]Dashboard Interrotta.[/]")