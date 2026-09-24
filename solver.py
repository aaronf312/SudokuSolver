import requests


url = "https://sudoku-api.vercel.app/api/dosuku"
response = requests.get(url)
data = response.json()
board = data['newboard']['grids'][0]['value']


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

valueMap = getCoordinates(board)
#print(board,valueMap)
#print(valueMap)
rowGroups = getRowGroups()
colGroups = getColGroups()
boxGroups = getBoxGroups()

unitList = rowGroups + colGroups + boxGroups

def findPeers(unitlist):
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

peers = findPeers(unitList)
#print(valueMap)

def eliminate(values,peers):
    for cell, value in values.items():
        if len(value) == 1:
            for peer in peers[cell]:
                if value in values[peer]:
                    values[peer] = values[peer].replace(value,"")
    return values
count = 0
while True:
    count += 1
    print("Loop Number: ", count)
    prev_values = valueMap.copy()

    values = eliminate(valueMap,peers)

    if values == prev_values:
        break


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

display_board(valueMap)