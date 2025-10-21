from dataclasses import dataclass
from typing import List, Dict

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