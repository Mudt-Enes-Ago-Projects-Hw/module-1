from typing import List
import re
from rich.prompt import Prompt, Confirm
from rich.table import Table
from .worker import Worker
from .compatibility import CompatibilityCalculator
from .ui_utils import UIUtils, console

class WorkerManager:
    def __init__(self, workers: List[Worker], languages: set, hobbies: set, positions: set):
        self.workers = workers
        self.languages = languages
        self.hobbies = hobbies
        self.positions = positions
        self.ui = UIUtils()
        self.compatibility = CompatibilityCalculator()

    def validate_url(self, url: str) -> bool:
        """Simple URL validation"""
        if not url:
            return True  # Optional field
        return bool(re.match(r'^https?://[^\s/$.?#].[^\s]*$', url))

    def find_user_by_name(self, name: str, partial: bool = True) -> List[Worker]:
        """Find users by name, supporting partial matches"""
        name = name.lower()
        if partial:
            return [w for w in self.workers if name in w.name.lower()]
        return [w for w in self.workers if name == w.name.lower()]

    def search_worker(self):
        """Search for a worker and show compatibility"""
        console.print("\n[bold cyan]Search Worker[/bold cyan]")
        
        if not self.workers:
            console.print("[red]No workers available[/red]")
            return
            
        # Show all workers in a numbered list
        selection = self.ui.select_from_list(
            [w.name for w in self.workers],
            "Select worker to view"
        )[0]
        worker = self.workers[[w.name for w in self.workers].index(selection)]

        # Print worker details
        self.ui.print_worker_details(worker)

        # Calculate compatibility with other workers
        compatibilities = []
        for other in self.workers:
            if other != worker:
                score, breakdown = self.compatibility.compute_compatibility(worker, other)
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

    def add_worker(self) -> Worker:
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
        languages = self.ui.select_from_list(
            sorted(self.languages),
            "Select languages",
            multiple=True
        )
        hobbies = self.ui.select_from_list(
            sorted(self.hobbies),
            "Select hobbies",
            multiple=True
        )
        position = self.ui.select_from_list(
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

        # Create worker
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
        console.print("[green]Worker added successfully![/green]")
        return worker

    def edit_worker(self):
        """Edit an existing worker"""
        console.print("\n[bold cyan]Edit Worker[/bold cyan]")
        
        if not self.workers:
            console.print("[red]No workers available[/red]")
            return None
            
        # Show all workers in a numbered list
        selection = self.ui.select_from_list(
            [w.name for w in self.workers],
            "Select worker to edit"
        )[0]
        worker = self.workers[[w.name for w in self.workers].index(selection)]

        while True:
            console.print("\n[cyan]Current worker details:[/cyan]")
            self.ui.print_worker_details(worker)
            
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
                    console.print("[green]Worker deleted successfully![/green]")
                    return None
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
                worker.languages = self.ui.select_from_list(
                    sorted(self.languages),
                    "Select new languages",
                    multiple=True
                )

            elif choice == '5':
                worker.hobbies = self.ui.select_from_list(
                    sorted(self.hobbies),
                    "Select new hobbies",
                    multiple=True
                )

            elif choice == '6':
                worker.work_position = self.ui.select_from_list(
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

            console.print("[green]Worker updated successfully![/green]")
        return True  # Return True to indicate changes were made

    def compare_workers(self):
        """Compare two workers"""
        console.print("\n[bold cyan]Compare Workers[/bold cyan]")
        
        if len(self.workers) < 2:
            console.print("[red]Need at least 2 workers to compare[/red]")
            return

        # Select first worker
        worker_names = [w.name for w in self.workers]
        selection1 = self.ui.select_from_list(worker_names, "Select first worker")[0]
        worker1 = self.workers[worker_names.index(selection1)]

        # Select second worker
        other_workers = [w for w in self.workers if w != worker1]
        other_names = [w.name for w in other_workers]
        selection2 = self.ui.select_from_list(other_names, "Select second worker")[0]
        worker2 = other_workers[other_names.index(selection2)]

        # Calculate and show compatibility
        score, breakdown = self.compatibility.compute_compatibility(worker1, worker2)

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
        selection = self.ui.select_from_list(worker_names, f"Select worker to build team around")[0]
        worker = self.workers[worker_names.index(selection)]

        # Get all available positions for the team
        team_positions = list(self.positions)
        if not team_positions:
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
                ((c, *self.compatibility.compute_compatibility(worker, c)) for c in candidates),
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
                score = self.compatibility.compute_compatibility(worker, member)[0] if member != worker else 'Team Leader'
                table.add_row(position, member.name, str(score))
            else:
                table.add_row(position, "No candidate found", "-")

        console.print(table)

    def edit_lists(self, data_manager):
        """Edit languages, hobbies, and positions"""
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
            elif choice == '1':
                self._edit_single_list('Languages', self.languages, data_manager.languages_file, data_manager)
            elif choice == '2':
                self._edit_single_list('Hobbies', self.hobbies, data_manager.hobbies_file, data_manager)
            elif choice == '3':
                self._edit_single_list('Work Positions', self.positions, data_manager.positions_file, data_manager)

    def _edit_single_list(self, name: str, items: set, file_path, data_manager):
        """Edit a single list"""
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
                    data_manager.save_simple_list(items, file_path)
                    console.print("[green]Item added successfully![/green]")
            elif choice == '2':
                to_remove = self.ui.select_from_list(sorted(items), "Select item to remove")
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
                        data_manager.save_workers(self.workers)

                    items.remove(item)
                    data_manager.save_simple_list(items, file_path)
                    console.print("[green]Item removed successfully![/green]")