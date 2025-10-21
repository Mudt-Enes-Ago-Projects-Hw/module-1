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

    @staticmethod
    def change_admin_password(admin_credentials: Dict[str, str], data_manager) -> bool:
        """Change admin password"""
        console.print("\n[bold cyan]Change Admin Password[/bold cyan]")
        
        # Verify old password
        username = Prompt.ask("Enter your username")
        old_password = getpass.getpass("Enter current password: ")
        
        # Check credentials
        if username not in admin_credentials:
            console.print("[red]Invalid username[/red]")
            return False
            
        if not bcrypt.checkpw(old_password.encode(), admin_credentials[username].encode()):
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
        admin_credentials[username] = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        data_manager.save_admin_credentials(admin_credentials)
        console.print("[green]Password changed successfully![/green]")
        return True