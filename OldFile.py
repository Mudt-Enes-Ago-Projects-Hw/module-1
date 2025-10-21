#!/usr/bin/env python3
"""
Worker Management System - A CLI tool for managing workers and computing compatibility

Requirements:
    pip install rich bcrypt

Usage:
    python worker_management.py

Features:
    - Worker management (add, edit, search, delete)
    - Compatibility scoring between workers
    - Team formation based on compatibility
    - Management of languages, hobbies, and work positions
    - Secure admin authentication
"""

import csv
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
import getpass
import bcrypt
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import print as rprint
from rich.text import Text

# Initialize Rich console
console = Console()

@dataclass
class Worker:
    name: str
    short_description: str
    age: int
    languages: List[str]
    hobbies: List[str]
    work_position: str
    github: str
    linkedin: str

    @classmethod
    def from_csv_row(cls, row: Dict[str, str]) -> 'Worker':
        return cls(
            name=row['name'],
            short_description=row['shortDescription'],
            age=int(row['age']),
            languages=row['languages'].split(';') if row['languages'] else [],
            hobbies=row['hobbies'].split(';') if row['hobbies'] else [],
            work_position=row['workPosition'],
            github=row['github'],
            linkedin=row['linkedin']
        )

    def to_csv_row(self) -> Dict[str, str]:
        return {
            'name': self.name,
            'shortDescription': self.short_description,
            'age': str(self.age),
            'languages': ';'.join(self.languages),
            'hobbies': ';'.join(self.hobbies),
            'workPosition': self.work_position,
            'github': self.github,
            'linkedin': self.linkedin
        }

class WorkerManagementSystem:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.workers_file = self.base_path / 'data/workers.csv'
        self.languages_file = self.base_path / 'data/languages.csv'
        self.hobbies_file = self.base_path / 'data/hobbies.csv'
        self.positions_file = self.base_path / 'data/workPositions.csv'
        self.admin_file = self.base_path / 'data/admin.csv'
        
        # Load data
        self.workers: List[Worker] = []
        self.languages: Set[str] = set()
        self.hobbies: Set[str] = set()
        self.positions: Set[str] = set()
        self.admin_credentials: Dict[str, str] = {}
        
        self.load_all_data()

    def load_all_data(self):
        """Load all data from CSV files"""
        try:
            # Load workers
            if self.workers_file.exists():
                with open(self.workers_file, 'r', newline='') as f:
                    reader = csv.DictReader(f)
                    self.workers = [Worker.from_csv_row(row) for row in reader]

            # Load simple lists
            self.languages = self.load_simple_list(self.languages_file)
            self.hobbies = self.load_simple_list(self.hobbies_file)
            self.positions = self.load_simple_list(self.positions_file)

            # Load admin credentials
            if self.admin_file.exists():
                with open(self.admin_file, 'r', newline='') as f:
                    reader = csv.reader(f)
                    self.admin_credentials = dict(reader)

        except Exception as e:
            console.print(f"[red]Error loading data: {str(e)}[/red]")
            sys.exit(1)

    def load_simple_list(self, file_path: Path) -> Set[str]:
        """Load a simple list from a CSV file"""
        if file_path.exists():
            with open(file_path, 'r', newline='') as f:
                return {line.strip() for line in f if line.strip()}
        return set()

    def save_workers(self):
        """Save workers to CSV file"""
        with open(self.workers_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'name', 'shortDescription', 'age', 'languages',
                'hobbies', 'workPosition', 'github', 'linkedin'
            ])
            writer.writeheader()
            for worker in self.workers:
                writer.writerow(worker.to_csv_row())

    def save_simple_list(self, items: Set[str], file_path: Path):
        """Save a simple list to a CSV file"""
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            for item in sorted(items):
                writer.writerow([item])

    def save_admin_credentials(self):
        """Save admin credentials to CSV file"""
        with open(self.admin_file, 'w', newline='') as f:
            writer = csv.writer(f)
            for username, password_hash in self.admin_credentials.items():
                writer.writerow([username, password_hash])

    def compute_compatibility(self, user_a: Worker, user_b: Worker) -> Tuple[int, Dict]:
        """Compute compatibility score between two workers"""
        hobby_matches = len(set(user_a.hobbies) & set(user_b.hobbies))
        lang_matches = len(set(user_a.languages) & set(user_b.languages))
        age_diff = abs(user_a.age - user_b.age)

        hobby_points = hobby_matches * 20
        lang_points = lang_matches * 15
        
        if age_diff <= 2:
            age_points = 25
        elif age_diff <= 5:
            age_points = 15
        elif age_diff <= 10:
            age_points = 7
        else:
            age_points = 0

        raw_score = hobby_points + lang_points + age_points
        final_score = min(100, raw_score)

        breakdown = {
            'hobby_matches': hobby_matches,
            'hobby_points': hobby_points,
            'lang_matches': lang_matches,
            'lang_points': lang_points,
            'age_diff': age_diff,
            'age_points': age_points,
            'final_score': final_score,
            'matching_hobbies': list(set(user_a.hobbies) & set(user_b.hobbies)),
            'matching_languages': list(set(user_a.languages) & set(user_b.languages))
        }

        return final_score, breakdown

    def find_user_by_name(self, name: str, partial: bool = True) -> List[Worker]:
        """Find users by name, supporting partial matches"""
        name = name.lower()
        if partial:
            return [w for w in self.workers if name in w.name.lower()]
        return [w for w in self.workers if name == w.name.lower()]

    def validate_url(self, url: str) -> bool:
        """Simple URL validation"""
        if not url:
            return True  # Optional field
        return bool(re.match(r'^https?://[^\s/$.?#].[^\s]*$', url))

    def select_from_list(self, items: List[str], prompt: str, multiple: bool = False) -> List[str]:
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
                    # Parse and validate all indices first
                    indices = []
                    for x in selection.split(','):
                        idx = int(x.strip()) - 1
                        if not 0 <= idx < max_index:
                            raise ValueError(f"Selection {idx + 1} is out of range (1-{max_index})")
                        indices.append(idx)
                    
                    # If we get here, all indices are valid
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

    def print_worker_details(self, worker: Worker):
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

    def add_worker(self):
        """Add a new worker"""
        console.print("\n[bold cyan]Adding New Worker[/bold cyan]")

        # Name validation
        while True:
            name = Prompt.ask("Name").strip()
            if not name:
                console.print("[red]Name cannot be empty[/red]")
                continue
            existing = self.find_user_by_name(name, partial=False)
            if existing:
                console.print("[red]Error: A worker with this name already exists[/red]")
                continue
            break

        # Get other fields with validation
        short_desc = Prompt.ask("Short description").strip()
        
        while True:
            try:
                age = int(Prompt.ask("Age"))
                if not 1 <= age <= 119:
                    raise ValueError()
                break
            except ValueError:
                console.print("[red]Please enter a valid age (1-119)[/red]")

        # Select from existing lists
        languages = self.select_from_list(
            sorted(self.languages),
            "Select languages",
            multiple=True
        )
        hobbies = self.select_from_list(
            sorted(self.hobbies),
            "Select hobbies",
            multiple=True
        )
        position = self.select_from_list(
            sorted(self.positions),
            "Select work position"
        )[0]

        # Optional fields with validation
        while True:
            github = Prompt.ask("GitHub URL (optional)").strip()
            if not github or self.validate_url(github):
                break
            console.print("[red]Please enter a valid URL or leave empty[/red]")

        while True:
            linkedin = Prompt.ask("LinkedIn URL (optional)").strip()
            if not linkedin or self.validate_url(linkedin):
                break
            console.print("[red]Please enter a valid URL or leave empty[/red]")

        # Create and save worker
        worker = Worker(
            name=name,
            short_description=short_desc,
            age=age,
            languages=languages,
            hobbies=hobbies,
            work_position=position,
            github=github,
            linkedin=linkedin
        )

        self.workers.append(worker)
        self.save_workers()
        console.print("[green]Worker added successfully![/green]")

    def edit_worker(self):
        """Edit an existing worker"""
        console.print("\n[bold cyan]Edit Worker[/bold cyan]")
        
        # Find worker
        name = Prompt.ask("Enter worker name to edit")
        matches = self.find_user_by_name(name)
        
        if not matches:
            console.print("[red]No workers found with that name[/red]")
            return
        
        if len(matches) > 1:
            console.print("\n[yellow]Multiple matches found:[/yellow]")
            worker = matches[int(self.select_from_list(
                [w.name for w in matches],
                "Select worker to edit"
            )[0]) - 1]
        else:
            worker = matches[0]

        while True:
            console.print("\n[cyan]Current worker details:[/cyan]")
            self.print_worker_details(worker)
            
            console.print("\nWhat would you like to edit?")
            choice = Prompt.ask(
                "1 - Name\n"
                "2 - Short description\n"
                "3 - Age\n"
                "4 - Languages\n"
                "5 - Hobbies\n"
                "6 - Work position\n"
                "7 - GitHub\n"
                "8 - LinkedIn\n"
                "9 - Delete this worker\n"
                "0 - Done editing",
                choices=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            )

            if choice == '0':
                break
            elif choice == '9':
                if Confirm.ask("[red]Are you sure you want to delete this worker?[/red]"):
                    self.workers.remove(worker)
                    self.save_workers()
                    console.print("[green]Worker deleted successfully![/green]")
                    return
                continue

            # Handle other edits
            if choice == '1':
                while True:
                    new_name = Prompt.ask("New name").strip()
                    if not new_name:
                        console.print("[red]Name cannot be empty[/red]")
                        continue
                    existing = self.find_user_by_name(new_name, partial=False)
                    if existing and existing[0] != worker:
                        console.print("[red]Error: A worker with this name already exists[/red]")
                        continue
                    worker.name = new_name
                    break

            elif choice == '2':
                worker.short_description = Prompt.ask("New short description").strip()

            elif choice == '3':
                while True:
                    try:
                        age = int(Prompt.ask("New age"))
                        if 1 <= age <= 119:
                            worker.age = age
                            break
                    except ValueError:
                        pass
                    console.print("[red]Please enter a valid age (1-119)[/red]")

            elif choice == '4':
                worker.languages = self.select_from_list(
                    sorted(self.languages),
                    "Select new languages",
                    multiple=True
                )

            elif choice == '5':
                worker.hobbies = self.select_from_list(
                    sorted(self.hobbies),
                    "Select new hobbies",
                    multiple=True
                )

            elif choice == '6':
                worker.work_position = self.select_from_list(
                    sorted(self.positions),
                    "Select new work position"
                )[0]

            elif choice == '7':
                while True:
                    github = Prompt.ask("New GitHub URL (optional)").strip()
                    if not github or self.validate_url(github):
                        worker.github = github
                        break
                    console.print("[red]Please enter a valid URL or leave empty[/red]")

            elif choice == '8':
                while True:
                    linkedin = Prompt.ask("New LinkedIn URL (optional)").strip()
                    if not linkedin or self.validate_url(linkedin):
                        worker.linkedin = linkedin
                        break
                    console.print("[red]Please enter a valid URL or leave empty[/red]")

            self.save_workers()
            console.print("[green]Worker updated successfully![/green]")

    def search_worker(self):
        """Search for a worker and show compatibility"""
        console.print("\n[bold cyan]Search Worker[/bold cyan]")
        
        if not self.workers:
            console.print("[red]No workers available[/red]")
            return
            
        # Show all workers in a numbered list
        selection = self.select_from_list(
            [w.name for w in self.workers],
            "Select worker to view"
        )[0]
        worker = self.workers[[w.name for w in self.workers].index(selection)]

        # Print worker details
        self.print_worker_details(worker)

        # Calculate compatibility with other workers
        compatibilities = []
        for other in self.workers:
            if other != worker:
                score, breakdown = self.compute_compatibility(worker, other)
                compatibilities.append((other, score, breakdown))

        # Sort by score and show top 3
        compatibilities.sort(key=lambda x: x[1], reverse=True)
        
        console.print("\n[cyan]Top Compatible Workers:[/cyan]")
        table = Table(title="Compatibility Matches")
        table.add_column("Name", style="cyan")
        table.add_column("Score", style="green")
        table.add_column("Details", style="yellow")

        for other, score, breakdown in compatibilities[:3]:
            details = (
                f"Matching hobbies ({len(breakdown['matching_hobbies'])}): {', '.join(breakdown['matching_hobbies'])}\n"
                f"Matching languages ({len(breakdown['matching_languages'])}): {', '.join(breakdown['matching_languages'])}\n"
                f"Age difference: {breakdown['age_diff']} years"
            )
            table.add_row(other.name, str(score), details)

        console.print(table)

    def compare_workers(self):
        """Compare two workers"""
        console.print("\n[bold cyan]Compare Workers[/bold cyan]")
        
        if len(self.workers) < 2:
            console.print("[red]Need at least 2 workers to compare[/red]")
            return

        # Select first worker
        worker_names = [w.name for w in self.workers]
        selection1 = self.select_from_list(worker_names, "Select first worker")[0]
        worker1 = self.workers[worker_names.index(selection1)]

        # Select second worker
        other_workers = [w for w in self.workers if w != worker1]
        other_names = [w.name for w in other_workers]
        selection2 = self.select_from_list(other_names, "Select second worker")[0]
        worker2 = other_workers[other_names.index(selection2)]

        # Calculate and show compatibility
        score, breakdown = self.compute_compatibility(worker1, worker2)

        console.print(f"\n[cyan]Compatibility Score: {score}%[/cyan]")
        
        table = Table(title="Compatibility Breakdown")
        table.add_column("Category", style="cyan")
        table.add_column("Details", style="green")
        table.add_column("Points", style="yellow")

        table.add_row(
            "Hobbies",
            f"Matches ({breakdown['hobby_matches']}): {', '.join(breakdown['matching_hobbies'])}",
            str(breakdown['hobby_points'])
        )
        table.add_row(
            "Languages",
            f"Matches ({breakdown['lang_matches']}): {', '.join(breakdown['matching_languages'])}",
            str(breakdown['lang_points'])
        )
        table.add_row(
            "Age",
            f"Difference: {breakdown['age_diff']} years",
            str(breakdown['age_points'])
        )

        console.print(table)

    def find_team(self):
        """Find optimal team for a worker"""
        console.print("\n[bold cyan]Find a team for worker[/bold cyan]")
        
        if len(self.workers) < 3:
            console.print("[red]Need at least 3 workers to form a team[/red]")
            return

        # Get the target worker
        worker_names = [w.name for w in self.workers]
        selection = self.select_from_list(worker_names, f"Select worker to build team around")[0]
        worker = self.workers[worker_names.index(selection)]

        # Get all available positions for the team
        team_positions = list(self.positions)
        if not team_positions:  # Just check if there are any positions defined
            console.print("[red]No work positions defined[/red]")
            return

        console.print(f"\n[cyan]Finding optimal team using all positions: {', '.join(team_positions)}[/cyan]")

        # Find best matches for other positions
        team = {worker.work_position: worker}
        needed_positions = [pos for pos in team_positions if pos != worker.work_position]

        for position in needed_positions:
            candidates = [
                w for w in self.workers
                if w.work_position == position and w != worker
            ]
            
            if not candidates:
                console.print(f"[red]No candidates found for position: {position}[/red]")
                continue

            # Find the most compatible candidate
            best_candidate = max(
                ((c, *self.compute_compatibility(worker, c)) for c in candidates),
                key=lambda x: x[1]
            )
            team[position] = best_candidate[0]

        # Display team
        console.print("\n[bold cyan]Team Composition:[/bold cyan]")
        table = Table()
        table.add_column("Position", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Compatibility", style="yellow")

        for position in team_positions:
            member = team.get(position)
            if member:
                score = self.compute_compatibility(worker, member)[0] if member != worker else 'Team Leader'
                table.add_row(position, member.name, str(score))
            else:
                table.add_row(position, "No candidate found", "-")

        console.print(table)

    def edit_lists(self):
        """Edit languages, hobbies, and positions lists"""
        while True:
            console.print("\n[bold cyan]Edit Lists[/bold cyan]")
            choice = Prompt.ask(
                "1 - Languages\n"
                "2 - Hobbies\n"
                "3 - Work Positions\n"
                "0 - Back to main menu",
                choices=['0', '1', '2', '3']
            )

            if choice == '0':
                break

            list_type = {
                '1': ('Languages', self.languages, self.languages_file),
                '2': ('Hobbies', self.hobbies, self.hobbies_file),
                '3': ('Work Positions', self.positions, self.positions_file)
            }[choice]

            self.edit_single_list(*list_type)

    def edit_single_list(self, name: str, items: Set[str], file_path: Path):
        """Edit a single list (languages, hobbies, or positions)"""
        while True:
            console.print(f"\n[bold cyan]Edit {name}[/bold cyan]")
            console.print("\nCurrent items:")
            for item in sorted(items):
                console.print(f"  [green]•[/green] {item}")

            choice = Prompt.ask(
                "\n1 - Add item\n"
                "2 - Remove item\n"
                "0 - Back",
                choices=['0', '1', '2']
            )

            if choice == '0':
                break

            elif choice == '1':
                new_item = Prompt.ask(f"Enter new {name.lower()[:-1]}").strip()
                if new_item:
                    items.add(new_item)
                    self.save_simple_list(items, file_path)
                    console.print("[green]Item added successfully![/green]")

            elif choice == '2':
                to_remove = self.select_from_list(
                    sorted(items),
                    "Select item to remove"
                )
                if to_remove:
                    item = to_remove[0]
                    # Check if item is in use
                    users = []
                    for worker in self.workers:
                        if (name == 'Languages' and item in worker.languages) or \
                           (name == 'Hobbies' and item in worker.hobbies) or \
                           (name == 'Work Positions' and item == worker.work_position):
                            users.append(worker.name)

                    if users:
                        console.print(f"[yellow]Warning: This item is used by: {', '.join(users)}[/yellow]")
                        if not Confirm.ask("Remove anyway? (will be removed from workers too)"):
                            continue

                        # Remove from workers
                        for worker in self.workers:
                            if name == 'Languages' and item in worker.languages:
                                worker.languages.remove(item)
                            elif name == 'Hobbies' and item in worker.hobbies:
                                worker.hobbies.remove(item)
                            elif name == 'Work Positions' and item == worker.work_position:
                                worker.work_position = ''
                        self.save_workers()

                    items.remove(item)
                    self.save_simple_list(items, file_path)
                    console.print("[green]Item removed successfully![/green]")

    def change_admin_password(self):
        """Change admin password"""
        console.print("\n[bold cyan]Change Admin Password[/bold cyan]")
        
        # Get username (use default if only one)
        if len(self.admin_credentials) == 1:
            username = next(iter(self.admin_credentials))
        else:
            username = Prompt.ask("Enter admin username")
            if username not in self.admin_credentials:
                console.print("[red]Admin user not found[/red]")
                return

        # Verify old password
        old_password = getpass.getpass("Enter current password: ")
        stored_hash = self.admin_credentials[username]
        if not bcrypt.checkpw(old_password.encode(), stored_hash.encode()):
            console.print("[red]Incorrect password[/red]")
            return

        # Get and verify new password
        while True:
            new_password = getpass.getpass("Enter new password: ")
            if len(new_password) < 6:
                console.print("[red]Password must be at least 6 characters[/red]")
                continue

            confirm = getpass.getpass("Confirm new password: ")
            if new_password != confirm:
                console.print("[red]Passwords do not match[/red]")
                continue

            break

        # Update password
        self.admin_credentials[username] = bcrypt.hashpw(
            new_password.encode(), bcrypt.gensalt()
        ).decode()
        self.save_admin_credentials()
        console.print("[green]Password changed successfully![/green]")

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
                "8 - Exit",
                choices=['1', '2', '3', '4', '5', '6', '7', '8']
            )

            try:
                if choice == '1':
                    self.search_worker()
                elif choice == '2':
                    self.add_worker()
                elif choice == '3':
                    self.edit_worker()
                elif choice == '4':
                    self.compare_workers()
                elif choice == '5':
                    self.find_team()
                elif choice == '6':
                    self.edit_lists()
                elif choice == '7':
                    self.change_admin_password()
                elif choice == '8':
                    if Confirm.ask("[yellow]Are you sure you want to exit?[/yellow]"):
                        console.print("[cyan]Goodbye![/cyan]")
                        break
            except Exception as e:
                console.print(f"[red]An error occurred: {str(e)}[/red]")

            if choice != '8':
                Prompt.ask("\nPress Enter to continue")

def verify_login(system) -> bool:
    """Verify admin login credentials"""
    console.print("\n[bold cyan]Login Required[/bold cyan]")
    
    # Get username (use default if only one)
    if len(system.admin_credentials) == 1:
        username = next(iter(system.admin_credentials))
    else:
        username = Prompt.ask("Username")
        if username not in system.admin_credentials:
            console.print("[red]Invalid username[/red]")
            return False

    # Verify password
    password = getpass.getpass("Password: ")
    stored_hash = system.admin_credentials[username]
    
    if bcrypt.checkpw(password.encode(), stored_hash.encode()):
        console.print("[green]Login successful![/green]")
        return True
    else:
        console.print("[red]Invalid password[/red]")
        return False

def main():
    try:
        system = WorkerManagementSystem()
        
        # Verify login
        max_attempts = 3
        for attempt in range(max_attempts):
            if verify_login(system):
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