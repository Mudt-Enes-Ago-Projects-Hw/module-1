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
        
        # Get password only
        password = getpass.getpass("Password: ")
        
        # Get the stored hash (assuming single admin)
        stored_hash = list(admin_credentials.values())[0]
        
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            console.print("[green]Login successful![/green]")
            return True
        else:
            console.print("[red]Invalid password[/red]")
            return False

    @staticmethod
    def change_admin_password(admin_credentials: Dict[str, str], data_manager) -> bool:
        """Change admin password"""
        console.print("\n[bold cyan]Change Admin Password[/bold cyan]")
        
        # Verify old password
        old_password = getpass.getpass("Enter current password: ")
        
        # Get the stored hash (assuming single admin)
        stored_hash = list(admin_credentials.values())[0]
        
        if not bcrypt.checkpw(old_password.encode(), stored_hash.encode()):
            console.print("[red]Incorrect password[/red]")
            return False

        # Get and verify new password
        while True:
            new_password = getpass.getpass("Enter new password: ")
            if len(new_password) < 5:
                console.print("[red]Password must be at least 5 characters[/red]")
                continue

            confirm = getpass.getpass("Confirm new password: ")
            if new_password != confirm:
                console.print("[red]Passwords do not match[/red]")
                continue
            break

        # Update password
        username = list(admin_credentials.keys())[0]
        admin_credentials[username] = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        data_manager.save_admin_credentials(admin_credentials)
        console.print("[green]Password changed successfully![/green]")
        return True