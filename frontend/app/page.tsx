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

  const handleSolveClick = () => {
    console.log("Assembled Board Array:", board);
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen">
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

      <button
        onClick={handleSolveClick}
        className="mt-6 px-6 py-2 bg-blue-600 hover:bg-blue-500 rounded font-semibold"
      >
        Solve Puzzle
      </button>
    </main>
  );
}