
import requests
from pydantic import BaseModel,Field
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/getBoard")
def get_unsolved():
    url = "https://sudoku-api.vercel.app/api/dosuku?query={newboard(limit:1){grids{value,solution}}}"
    response = requests.get(url)
    data = response.json()

    grid_info = data['newboard']['grids'][0]

    board = grid_info['value']
    solution = grid_info['solution']
    return {"board": board}



cols = '123456789'
rows = 'ABCDEFGHI'



def getRowGroups():
    rowGroups = []
    for row in rows:
        group = []
        for col in cols:
            group.append(row+col)
        rowGroups.append(group)
    return rowGroups

def getColGroups():
    colGroups = []
    for col in cols:
        group = []
        for row in rows:
            group.append(row+col)
        colGroups.append(group)
    return colGroups
def getBoxGroups():
    rowBlocks = ['ABC','DEF','GHI']
    colBlocks = ['123','456','789']
    boxGroups = []
    for row in rowBlocks:
        
        for col in colBlocks:
            group = []
            for r in row:
                for c in col:
                    group.append(r+c)
            boxGroups.append(group)
    return boxGroups

def getCoordinates(board):
    valueMap = {}
    for x,col in enumerate(rows):
        for y,row in enumerate(cols):
            val =  board[x][y]
            if val == 0:
                valueMap[col+row] = '123456789'
                
            else:
                valueMap[col+row] = str(val)
    return valueMap


rowGroups = getRowGroups()
colGroups = getColGroups()
boxGroups = getBoxGroups()

global unitList
unitList = rowGroups + colGroups + boxGroups

def findPeers(unitlist,valueMap):
    peers = {}

    for c in valueMap:
        cVals = set()
        for unit in unitList:
            if c in unit:
                for r in unit:
                    if r != c:
                        cVals.add(r)
        peers[c] = cVals
    return peers

#print(valueMap)

def eliminate(values, peers):
    for cell, value in values.items():
        if len(value) == 0:
            return False #Catch any dead ends coming in 
        if len(value) == 1:
            for peer in peers[cell]:
                if value in values[peer]:
                    values[peer] = values[peer].replace(value, "")
                    if len(values[peer]) == 0:
                        return False  # Contradiction: dead end
    for unit in unitList:
        for c in '123456789':
            count = 0
            valid_square = None
            
            for square in unit:
                if c in values[square]:
                    count += 1
                    valid_square = square
            if count == 0:
                return False
            if count == 1:
                values[valid_square] = c  # Use valid_square here, not square
                if len(values[valid_square]) == 0:
                    return False


    return values



def display_board(values):
    rows = 'ABCDEFGHI'
    cols = '123456789'
    for r in rows:
        row_str = ""
        for c in cols:
            val = values[r + c]
            char = val if len(val) == 1 else '.'
            row_str += char + " "
        print(row_str)



def reduce_puzzle(values, peers):
    while True:
        prev_values = values.copy()
        values = eliminate(values, peers)
        if values is False:
            return False
        if values == prev_values:
            return values


def recursive_search(values,peers):
    min_len = 10
    min_cell = None
    max_len = 0
    for cell, value in values.items():
        if 1 < len(value) < min_len:
            min_len = len(value)
            min_cell = cell
        if len(value) > max_len:
            max_len = len(value)
    if max_len == 1:
        print("IS GOOD")
        return values
    if min_len == 0:
        return False
    for c in values[min_cell]:
        copy = values.copy()
        copy[min_cell] = c

        reduced = reduce_puzzle(copy,peers)
        if reduced is not False:
            result = recursive_search(reduced,peers)
            if result:
                return result
    return False

class SudokuInput(BaseModel):
    board: List[List[int]]

@app.post("/solve")
def solve_sudoku(data: SudokuInput):
    board = data.board
    valueMap = getCoordinates(board)
    peers = findPeers(unitList,valueMap)
    values = reduce_puzzle(valueMap, peers)
    
    if values is False:
        raise HTTPException(status_code=422, detail="Invalid board.")
        
    final_result = recursive_search(values,peers)
    
    if not final_result:
        raise HTTPException(status_code=422, detail="No solution found.")
        
    solved_board = [
        [int(final_result[col + row]) for y, row in enumerate(cols)]
        for x, col in enumerate(rows)
    ]
    
    return {"solution": solved_board}