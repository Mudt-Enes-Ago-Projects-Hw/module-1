#!/usr/bin/env python3
"""
Worker Management System - A CLI tool for managing workers and computing compatibility

Requirements:
    pip install rich bcrypt

Usage:
    python worker_management.py
"""

import sys
sys.dont_write_bytecode = True

from pathlib import Path
from components import DataManager, console, Auth
from components.worker_manager import WorkerManager
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

class WorkerManagementSystem:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.data_manager = DataManager(self.base_path)
        
        # Load data
        try:
            self.workers = self.data_manager.load_workers()
            self.languages = self.data_manager.load_simple_list(self.data_manager.languages_file)
            self.hobbies = self.data_manager.load_simple_list(self.data_manager.hobbies_file)
            self.positions = self.data_manager.load_simple_list(self.data_manager.positions_file)
            self.admin_credentials = self.data_manager.load_admin_credentials()
            
            # Initialize worker manager
            self.worker_manager = WorkerManager(
                self.workers,
                self.languages,
                self.hobbies,
                self.positions
            )
        except Exception as e:
            console.print(f"[red]Error loading data: {str(e)}[/red]")
            sys.exit(1)

    def main_menu(self):
        """Display and handle main menu"""
        while True:
            console.clear()
            self.display_stats()

            choice = Prompt.ask(
                "\n[bold cyan]Main Menu[/bold cyan]\n\n"
                "1 - Search worker\n"
                "2 - Add worker\n"
                "3 - Edit worker\n"
                "4 - Compare 2 workers\n"
                "5 - Find a team for worker\n"
                "6 - Edit Languages/Hobbies/Positions\n"
                "7 - Change Admin Password\n"
                "0 - Exit",
                choices=['0', '1', '2', '3', '4', '5', '6', '7']
            )

            try:
                if choice == '1':
                    self.worker_manager.search_worker()
                elif choice == '2':
                    worker = self.worker_manager.add_worker()
                    if worker:
                        self.data_manager.save_workers(self.workers)
                elif choice == '3':
                    if self.worker_manager.edit_worker():
                        self.data_manager.save_workers(self.workers)
                elif choice == '4':
                    self.worker_manager.compare_workers()
                elif choice == '5':
                    self.worker_manager.find_team()
                elif choice == '6':
                    self.worker_manager.edit_lists(self.data_manager)
                elif choice == '7':
                    Auth.change_admin_password(self.admin_credentials, self.data_manager)
                elif choice == '0':
                    if Confirm.ask("[yellow]Are you sure you want to exit?[/yellow]"):
                        console.print("[cyan]Goodbye![/cyan]")
                        break
            except Exception as e:
                console.print(f"[red]An error occurred: {str(e)}[/red]")

            if choice != '0':
                Prompt.ask("\nPress Enter to continue")

    def display_stats(self):
        """Display system statistics"""
        panel = Panel(
            f"[cyan]System Statistics[/cyan]\n\n"
            f"Total Workers: [green]{len(self.workers)}[/green]\n"
            f"Languages: [green]{len(self.languages)}[/green]\n"
            f"Hobbies: [green]{len(self.hobbies)}[/green]\n"
            f"Work Positions: [green]{len(self.positions)}[/green]\n"
            f"Admin Users: [green]{len(self.admin_credentials)}[/green]",
            title="Worker Management System",
            border_style="cyan"
        )
        console.print(panel)

def main():
    try:
        system = WorkerManagementSystem()
        
        # Verify login
        max_attempts = 3
        for attempt in range(max_attempts):
            if Auth.verify_login(system.admin_credentials):
                system.main_menu()
                break
            else:
                remaining = max_attempts - attempt - 1
                if remaining > 0:
                    console.print(f"[yellow]{remaining} attempts remaining[/yellow]")
                else:
                    console.print("[red]Maximum login attempts exceeded[/red]")
                    sys.exit(1)
                    
    except KeyboardInterrupt:
        console.print("\n[cyan]Goodbye![/cyan]")
    except Exception as e:
        console.print(f"[red]Fatal error: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()