from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from rich.live import Live
from core.settings import settings

console = Console()

def create_layout() -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )
    return layout

class Dashboard:
    def __init__(self):
        self.layout = create_layout()
        self.statuses = {
            "Kernel": "Starting...",
            "Redis": "Checking...",
            "Tracing": "Checking..."
        }

    def update_status(self, component: str, status: str):
        self.statuses[component] = status

    def get_renderable(self):
        table = Table(title=f"[bold blue]{settings.APP_NAME}[/bold blue] v{settings.APP_VERSION}")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="magenta")
        
        for comp, status in self.statuses.items():
            color = "green" if "Connected" in status or "Ready" in status else "yellow"
            if "Error" in status or "Disconnected" in status:
                color = "red"
            table.add_row(comp, f"[{color}]{status}[/{color}]")

        self.layout["main"].update(Panel(table))
        self.layout["header"].update(Panel(f"[bold white]PC Center OS — Broker Edition[/bold white]", style="blue"))
        self.layout["footer"].update(Panel(f"Settings: [italic]{settings.model_dump_json(include={'APP_NAME', 'REDIS_URL'})}[/italic]"))
        
        return self.layout

dashboard = Dashboard()
