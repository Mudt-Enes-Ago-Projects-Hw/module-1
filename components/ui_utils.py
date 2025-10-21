from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from typing import List
from .worker import Worker

console = Console()

class UIUtils:
    @staticmethod
    def select_from_list(items: List[str], prompt: str, multiple: bool = False) -> List[str]:
        """Present a numbered list and get user selection"""
        if not items:
            console.print("[yellow]No items available to select from[/yellow]")
            return []

        # Sort and number the items
        items = sorted(items)
        table = Table(show_header=False)
        for i, item in enumerate(items, 1):
            table.add_row(f"[cyan]{i}[/cyan]", item)
        console.print(table)

        max_index = len(items)
        while True:
            if multiple:
                selection = Prompt.ask(
                    f"{prompt} (comma-separated numbers 1-{max_index}, or Enter for none)")
                if not selection:
                    return []
                
                try:
                    indices = []
                    for x in selection.split(','):
                        idx = int(x.strip()) - 1
                        if not 0 <= idx < max_index:
                            raise ValueError(f"Selection {idx + 1} is out of range (1-{max_index})")
                        indices.append(idx)
                    selected = [items[i] for i in indices]
                    return selected
                except ValueError as e:
                    console.print(f"[red]Invalid selection: {str(e)}[/red]")
            else:
                selection = Prompt.ask(f"{prompt} (enter a number 1-{max_index})")
                try:
                    index = int(selection) - 1
                    if 0 <= index < max_index:
                        return [items[index]]
                    else:
                        console.print(f"[red]Invalid selection: Please enter a number between 1 and {max_index}[/red]")
                except ValueError:
                    console.print("[red]Invalid selection: Please enter a valid number[/red]")

    @staticmethod
    def print_worker_details(worker: Worker):
        """Print worker details in a nice table"""
        table = Table(title=f"Worker Details: {worker.name}")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Name", worker.name)
        table.add_row("Description", worker.short_description)
        table.add_row("Age", str(worker.age))
        table.add_row("Languages", ", ".join(worker.languages))
        table.add_row("Hobbies", ", ".join(worker.hobbies))
        table.add_row("Position", worker.work_position)
        table.add_row("GitHub", worker.github or "N/A")
        table.add_row("LinkedIn", worker.linkedin or "N/A")

        console.print(table)