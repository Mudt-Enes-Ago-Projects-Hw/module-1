import getpass
import bcrypt
from rich.console import Console
from rich.prompt import Prompt
from typing import Dict

console = Console()

class Auth:
    @staticmethod
    def verify_login(admin_credentials: Dict[str, str], max_attempts: int = 3) -> bool:
        """Verify admin login credentials"""
        console.print("\n[bold cyan]Login Required[/bold cyan]")
        
        # Get username (use default if only one)
        if len(admin_credentials) == 1:
            username = next(iter(admin_credentials))
        else:
            username = Prompt.ask("Username")
            if username not in admin_credentials:
                console.print("[red]Invalid username[/red]")
                return False

        # Verify password
        password = getpass.getpass("Password: ")
        stored_hash = admin_credentials[username]
        
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            console.print("[green]Login successful![/green]")
            return True
        else:
            console.print("[red]Invalid password[/red]")
            return False