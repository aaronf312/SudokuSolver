# Sudoku Solver

A high-performance Sudoku solver featuring a constraint-propagation and backtracking search algorithm implemented in Python, paired with an interactive React frontend and FastAPI backend.

## Current Project Status

* **Backend (Incomplete):** FastAPI server (`api.py`) hosting endpoints for solving puzzles (`/solve`) and fetching external unsolved puzzles (`/getBoard`). Adding custom CNN model to support user submitted puzzles by image.
* **Frontend (Complete):** React and Tailwind CSS interface supporting automatic solving, board clearing, and dynamic puzzle fetching.
* **Core Engine:** Implements Peter Norvig’s constraint propagation (eliminating impossible values) combined with recursive depth-first search.

## Tech Stack

* **Backend:** Python, FastAPI, Uvicorn, Pydantic, Requests, PyTorch,
  * Constraint propagation and recursive search algorithms
  * REST API endpoints with CORS configuration
  * Custom CNN digit classifier (SudokuCNN) trained on MNIST
* **Frontend:** React, Tailwind CSS
  * Grid-based interactive UI with centralized error handling

## How It Works

1. **Board Ingestion:** Fetches an active puzzle grid via the external Dosuku API or accepts manual user input.
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