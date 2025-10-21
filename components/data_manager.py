import csv
from pathlib import Path
from typing import List, Dict, Set
from .worker import Worker

class DataManager:
    def __init__(self, base_path: Path):
        self.data_path = base_path / 'data'
        self.workers_file = self.data_path / 'workers.csv'
        self.languages_file = self.data_path / 'languages.csv'
        self.hobbies_file = self.data_path / 'hobbies.csv'
        self.positions_file = self.data_path / 'workPositions.csv'
        self.admin_file = self.data_path / 'admin.csv'

    def load_workers(self) -> List[Worker]:
        if self.workers_file.exists():
            with open(self.workers_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                return [Worker.from_csv_row(row) for row in reader]
        return []

    def save_workers(self, workers: List[Worker]):
        with open(self.workers_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'name', 'shortDescription', 'age', 'languages',
                'hobbies', 'workPosition', 'github', 'linkedin'
            ])
            writer.writeheader()
            for worker in workers:
                writer.writerow(worker.to_csv_row())

    def load_simple_list(self, file_path: Path) -> Set[str]:
        if file_path.exists():
            with open(file_path, 'r', newline='') as f:
                return {line.strip() for line in f if line.strip()}
        return set()

    def save_simple_list(self, items: Set[str], file_path: Path):
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            for item in sorted(items):
                writer.writerow([item])

    def load_admin_credentials(self) -> Dict[str, str]:
        if self.admin_file.exists():
            with open(self.admin_file, 'r', newline='') as f:
                reader = csv.reader(f)
                return dict(reader)
        return {}

    def save_admin_credentials(self, credentials: Dict[str, str]):
        with open(self.admin_file, 'w', newline='') as f:
            writer = csv.writer(f)
            for username, password_hash in credentials.items():
                writer.writerow([username, password_hash])