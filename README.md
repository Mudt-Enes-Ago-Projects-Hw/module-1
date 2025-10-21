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

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install rich bcrypt
```

## Project Structure

```
assignementOnePython/
├── main.py                 # Main application entry point
├── worker_management.py    # Legacy monolithic version (deprecated)
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

### Hobbies (30 points max)
- Calculates what percentage of person A's hobbies match person B's
- Example: If A has 1 hobby and B has it → 100% → 30 points

### Languages (30 points max)
- Same percentage logic as hobbies
- Example: If A speaks 2 languages and B speaks both → 100% → 30 points

### Age (40 points max)
- ≤2 years difference: 40 points
- ≤5 years difference: 25 points
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

## License

This project is created for educational purposes.

## Authors

Created as part of university project assignment.
