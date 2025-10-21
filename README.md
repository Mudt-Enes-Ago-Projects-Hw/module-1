# Worker Management System

A comprehensive CLI-based worker management system with compatibility scoring, team formation, and secure authentication.

## Features

- **Worker Management**: Add, edit, search, and delete worker profiles
- **Compatibility Scoring**: Calculate compatibility between workers based on:
  - Shared hobbies (30 points max)
  - Common languages (30 points max)
  - Age similarity (40 points max)
- **Team Formation**: Automatically find optimal team compositions based on compatibility
- **Data Management**: Manage languages, hobbies, and work positions
- **Secure Authentication**: Bcrypt password hashing for admin access
- **Beautiful UI**: Rich terminal interface with colored output and tables

## Requirements

- Python 3.7+
- Required packages:
  - `rich` - For beautiful terminal UI
  - `bcrypt` - For secure password hashing

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd assignementOnePython
```

2. Install dependencies:
```bash
pip install rich bcrypt
```

## Project Structure

```
assignementOnePython/
├── main.py                 # Main application entry point
├── components/             # Modular components
│   ├── __init__.py
│   ├── worker.py          # Worker data class
│   ├── data_manager.py    # CSV file operations
│   ├── compatibility.py   # Compatibility calculation logic
│   ├── ui_utils.py        # UI helper functions
│   ├── auth.py            # Authentication logic
│   └── worker_manager.py  # Worker operations manager
├── data/                  # Data storage
│   ├── workers.csv        # Worker profiles
│   ├── languages.csv      # Available languages
│   ├── hobbies.csv        # Available hobbies
│   ├── workPositions.csv  # Available work positions
│   └── admin.csv          # Admin credentials
└── README.md
```

## Usage

Run the application:
```bash
python main.py
```

### Default Login
- Username: `admin`
- Password: `admin`

### Main Menu Options

1. **Search Worker** - View worker details and top 3 compatible workers
2. **Add Worker** - Create a new worker profile
3. **Edit Worker** - Modify existing worker information or delete workers
4. **Compare 2 Workers** - See detailed compatibility breakdown between two workers
5. **Find a Team** - Build optimal team based on all work positions
6. **Edit Lists** - Manage languages, hobbies, and work positions
7. **Change Admin Password** - Update admin credentials
0. **Exit** - Close the application

## Compatibility Scoring System

The system uses a percentage-based compatibility calculation:

### Hobbies (40 points max)
- Calculates what percentage of person A's hobbies match person B's
- Example: If A has 1 hobby and B has it → 100% → 40 points

### Languages (40 points max)
- Same percentage logic as hobbies
- Example: If A speaks 2 languages and B speaks both → 100% → 40 points

### Age (20 points max)
- ≤5 years difference: 20 points
- ≤10 years difference: 10 points
- >10 years difference: 0 points

**Maximum possible score: 100 points**

## Data Files

All data is stored in CSV format in the `data/` directory:

- **workers.csv**: Worker profiles with name, description, age, languages, hobbies, position, GitHub, and LinkedIn
- **languages.csv**: Available spoken languages (e.g., English, German, Turkish)
- **hobbies.csv**: Available hobbies
- **workPositions.csv**: Available job positions
- **admin.csv**: Admin credentials (bcrypt hashed passwords)

## Development

### Code Organization

The project is organized into modular components:

- **Worker**: Data class representing a worker
- **DataManager**: Handles all CSV file operations
- **CompatibilityCalculator**: Computes compatibility scores
- **WorkerManager**: Manages worker CRUD operations
- **UIUtils**: Terminal UI helpers
- **Auth**: Authentication logic

### Preventing `__pycache__`

The application includes `sys.dont_write_bytecode = True` to prevent Python from creating `__pycache__` directories.

## Security

- Passwords are hashed using bcrypt
- 3 login attempts before lockout
- Duplicate worker names are prevented
- Input validation on all fields

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request


## Authors

Enes Ago

Created as part of university project assignment.

---

## Python Decorators Explained

This project uses several Python decorators to make the code cleaner and more maintainable. Here's what they do:

### `@dataclass` - Automatic Class Generation

**Without `@dataclass` (manual approach):**
```python
class Worker:
    def __init__(self, name, short_description, age, languages, hobbies, 
                 work_position, github, linkedin):
        self.name = name
        self.short_description = short_description
        self.age = age
        self.languages = languages
        self.hobbies = hobbies
        self.work_position = work_position
        self.github = github
        self.linkedin = linkedin
    
    def __repr__(self):
        return (f"Worker(name={self.name}, short_description={self.short_description}, "
                f"age={self.age}, languages={self.languages}, hobbies={self.hobbies}, "
                f"work_position={self.work_position}, github={self.github}, "
                f"linkedin={self.linkedin})")
    
    def __eq__(self, other):
        if not isinstance(other, Worker):
            return False
        return (self.name == other.name and 
                self.short_description == other.short_description and
                self.age == other.age and
                self.languages == other.languages and
                self.hobbies == other.hobbies and
                self.work_position == other.work_position and
                self.github == other.github and
                self.linkedin == other.linkedin)
```

**With `@dataclass` (our approach):**
```python
from dataclasses import dataclass
from typing import List

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
```

**What `@dataclass` generates automatically:**
- `__init__()` - Constructor method
- `__repr__()` - String representation
- `__eq__()` - Equality comparison
- And more!

---

### `@classmethod` - Alternative Constructors

**Without `@classmethod`:**
```python
# Manual parsing required every time
worker = Worker(
    name=row['name'],
    short_description=row['shortDescription'],
    age=int(row['age']),
    languages=row['languages'].split(';') if row['languages'] else [],
    hobbies=row['hobbies'].split(';') if row['hobbies'] else [],
    work_position=row['workPosition'],
    github=row['github'],
    linkedin=row['linkedin']
)
```

**With `@classmethod`:**
```python
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

# Usage: Simple one-liner
worker = Worker.from_csv_row(row)
```

---

### `@staticmethod` - Utility Functions

**Without `@staticmethod`:**
```python
class UIUtils:
    def select_from_list(self, items, prompt):
        return items[0]

ui = UIUtils()  # Need to create instance
result = ui.select_from_list(items, "Choose")
```

**With `@staticmethod`:**
```python
class UIUtils:
    @staticmethod
    def select_from_list(items, prompt):
        return items[0]

result = UIUtils.select_from_list(items, "Choose")  # No instance needed
```

---

### Comparison Table

| Decorator | First Parameter | Use Case | Example |
|-----------|----------------|----------|---------|
| **(none)** | `self` | Access instance data | `def get_name(self): return self.name` |
| `@classmethod` | `cls` | Factory methods, alternative constructors | `def from_csv(cls, data): return cls(...)` |
| `@staticmethod` | *none* | Utility functions related to class | `def validate_url(url): return is_valid` |
| `@dataclass` | *N/A* | Auto-generate `__init__`, `__repr__`, etc. | Applied to entire class |
