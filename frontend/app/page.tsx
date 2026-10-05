'use client';
import { useState } from 'react';



function SubGrid({
  gridIndex,
  board,
  onCellChange
}: {
  
  gridIndex: number;
  board: number[][];
  onCellChange: (row: number, col: number, value: string) => void;
}) {
  
  return (
    
    <div className="grid grid-cols-3">
      {Array.from({ length: 9 }).map((_, cellIndex) => {
        const row = Math.floor(gridIndex / 3) * 3 + Math.floor(cellIndex / 3);
        const col = (gridIndex % 3) * 3 + (cellIndex % 3);
        const val = board[row][col];

        return (
          <input
            key={cellIndex}
            type="text"
            maxLength={1}
            value={val === 0 ? '' : val}
            onChange={(e) => onCellChange(row, col, e.target.value)}
            className="w-10 h-10 text-center bg-gray-900 text-white border border-gray-700 select-none focus:outline-none"
          />
        );
      })}
    </div>
  );
}

export default function SudokuPage() {
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [board, setBoard] = useState<number[][]>(
    Array(9).fill(0).map(() => Array(9).fill(0))
  );

  const handleCellChange = (row: number, col: number, value: string) => {
    const num = value === '' ? 0 : parseInt(value, 10);
    if (isNaN(num) || num < 1 || num > 9) return;

    setBoard(prev => {
      const newBoard = prev.map(r => [...r]);
      newBoard[row][col] = num;
      return newBoard;
    });
  };

  const handleSolveClick = async () => {
    
    setErrorMessage(null);
    try {
      const response = await fetch("http://localhost:8000/solve", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ board }), // Sends your 9x9 matrix wrapped in the expected key
      });

      const data = await response.json();

      if (response.ok) {
        setBoard(data.solution); // Replaces your grid state with the solved response
      } else {
        setErrorMessage(data.detail);
        console.error("Solver error:", data.detail);
        
      }
    } catch (err) {
      setErrorMessage("Failed to connect to backend server.");
      console.error("Network error:", err);
    }
  };

  const handleNewBoard = async () => {
    setErrorMessage(null);
    try {
      const response = await fetch("http://localhost:8000/getBoard");

      const data = await response.json();

      if (response.ok) {
        setBoard(data.board); // Replaces your grid state with the solved response
      } else {
        setErrorMessage("Bad Server Response");
        console.error("Server Error");
      }
    } catch (err) {
      setErrorMessage("Failed to connect to backend server.");
      console.error("Network error:", err);
    }
  };

  const handleResetBoard = () => {
    setBoard(Array(9).fill(0).map(() => Array(9).fill(0)));
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen">
      {/* ERROR POPUP BANNER */}
      {errorMessage && (
        <div className="fixed top-5 left-1/2 transform -translate-x-1/2 bg-red-600 text-white px-6 py-3 rounded shadow-lg z-50 flex items-center gap-4">
          <span>{errorMessage}</span>
          <button
            onClick={() => setErrorMessage(null)}
            className="font-bold text-white cursor-pointer bg-transparent border-none"
          >
            ✕
          </button>
        </div>
      )}
      <h1 className="text-2xl font-bold mb-6">Sudoku Solver</h1>

      <div className="grid grid-cols-3 gap-1 bg-gray-700">
        {Array.from({ length: 9 }).map((_, gridIndex) => (
          <SubGrid
            key={gridIndex}
            gridIndex={gridIndex}
            board={board}
            onCellChange={handleCellChange}
          />
        ))}
      </div>
      <div className="flex flex-col gap-3 mt-6 w-64">
        <button
          onClick={handleSolveClick}
          className="w-full py-2 bg-blue-600 hover:bg-blue-500 rounded font-semibold text-white text-sm"
        >
          Solve Puzzle
        </button>
        <button
          onClick={handleResetBoard}
          className="w-full py-2 bg-gray-700 hover:bg-gray-600 rounded font-semibold text-white text-sm"
        >
          Clear Board
        </button>
        <button
          onClick={handleNewBoard}
          className="w-full py-2 bg-blue-600 hover:bg-blue-500 rounded font-semibold text-white text-sm"
        >
          Get Unsolved Puzzle
        </button>
      </div>
      
    </main>
  );
}