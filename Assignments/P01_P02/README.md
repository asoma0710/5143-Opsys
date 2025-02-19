# Custom Shell and Virtual Filesystem

## Description
This project implements a **custom shell** with a **virtual filesystem** built using Python. It supports shell-like commands (e.g., `ls`, `mkdir`, `rm`, `cat`) and integrates with a database to simulate a filesystem. The project also provides an API for external interaction with the virtual filesystem.

## Features
- Virtual filesystem using SQLite
- Command-line interface supporting Linux-like commands
- API for filesystem interactions
- Supports basic file operations: create, read, update, delete
- Implements command parsing and execution

## Installation
### Prerequisites
- Python 3.12 or higher
- `pip` (Python package manager)

### Steps to Install
1. **Clone the repository**:
   ```sh
   git clone <repository-url>
   cd P01
   ```
2. **Set up a virtual environment** (recommended):
   ```sh
   python -m venv myvenv
   source myvenv/bin/activate  # On Windows use: myvenv\Scripts\activate
   ```
3. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```
4. **Initialize the database**:
   ```sh
   python database.py
   ```

## Usage
### Running the Shell
To start the interactive shell, run:
```sh
python shell.py
```
You can then execute commands like:
```sh
ls
mkdir test_dir
cd test_dir
pwd
```

### Running the API
To start the API server, run:
```sh
uvicorn api:app --reload
```
This will start the FastAPI server, accessible at `http://127.0.0.1:8000/docs` for API documentation.

## Command List
The following commands are supported:
- `ls` - List directory contents
- `mkdir <dir>` - Create a new directory
- `cd <dir>` - Change directory
- `pwd` - Print working directory
- `rm <file>` - Remove a file
- `cp <src> <dst>` - Copy a file
- `mv <src> <dst>` - Move a file
- `cat <file>` - Display file contents
- `grep <pattern> <file>` - Search in a file
- `chmod <permissions> <file>` - Change file permissions

## Recreating the Environment
To replicate the project in another environment:
1. Clone the repository
2. Set up a virtual environment
3. Install dependencies (`pip install -r requirements.txt`)
4. Run `database.py` to set up the database
5. Run `shell.py` or `api.py` to start the shell or API

## Contributing
Feel free to submit issues and pull requests to improve the project!

## License
This project is open-source

