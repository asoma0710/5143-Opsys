# Simulation and Job Scheduling System

## Description
This project implements a **simulation and job scheduling system** using Python. It manages job execution, scheduling, and visualization of results.

## Features
- Job scheduling system
- Simulation execution
- Logging system for results
- Visualization of job execution data
- Configurable settings via JSON

## Installation

### Prerequisites
- Python 3.12 or higher
- `pip` (Python package manager)

### Steps to Install
1. **Clone the repository**:
   ```sh
   git clone <repository-url>
   cd P03
   ```
2. **Set up a virtual environment** (recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. **Install dependencies** (if a requirements file exists):
   ```sh
   pip install -r requirements.txt
   ```
4. **Ensure configuration is set up**:
   - Modify `myConfig.json` as needed.

## Usage

### Running the Simulation
To execute the simulation:
```sh
python main.py
```
Logs will be saved in `simulation_output.log`.

### Running the Scheduler
To start job scheduling:
```sh
python scheduler.py
```

### Running the Job Manager
To manage job execution:
```sh
python job_manager.py
```

### Running Visualization
To visualize the output:
```sh
python visualization.py
```

## Configuration
- Modify `myConfig.json` to change job execution parameters and scheduling behavior.

## Recreating the Environment
To replicate the project in another environment:
1. Clone the repository
2. Set up a virtual environment
3. Install dependencies (`pip install -r requirements.txt` if available)
4. Configure settings via `myConfig.json`
5. Run `main.py` and install any additional dependencies if need to to run it on your system

## Contributing
Feel free to submit issues and pull requests to improve the project!

## License
This project is open-source.

