# Sudoku Solver

A high-performance Sudoku solver featuring a constraint-propagation and backtracking search algorithm implemented in Python, paired with an interactive React frontend.

## Current Project Status

* **Core Engine (Complete):** The backend solver successfully fetches puzzles via API, applies constraint propagation (eliminating impossible values), and resolves complex boards using a recursive depth-first search. I plan to add a backend script to allow the frontend to fetch from a similar backend.
* **Frontend (In Progress):** A React-based interface is under active development which will allow users to input boards and get the puzzle solution back.

## Tech Stack

* **Backend / Solver:** Python
  * Constraint propagation and recursive search algorithms
  * REST API integration for dynamic puzzle ingestion
* **Frontend:** React *(In Development)*

## How It Works

1. **Board Ingestion:** Fetches an active puzzle grid.
2. **Constraint Mapping:** Maps rows, columns, and 3x3 box constraints (units and peers) to evaluate valid state spaces.
3. **Reduction & Search:** Iteratively eliminates invalid options through constraint propagation, falling back on recursive backtracking search to resolve empty cells.

## Installation & Setup

### Prerequisites
* Python 3.x installed locally
* Node.js and npm (for the React frontend)

### Running the Backend
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install requests fastapi uvicorn pydantic