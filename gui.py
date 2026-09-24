import requests
from tkinter import *
from tkinter import ttk

url = "https://sudoku-api.vercel.app/api/dosuku"
response = requests.get(url)
data = response.json()
board = data['newboard']['grids'][0]['value']

root = Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()

for r in range(9):
    for c in range(9):
        entry = ttk.Entry(root, width=3, justify='center')
        entry.grid(row=r,column=c)
        if(board[r][c] != 0):
            entry.insert(0, board[r][c])





root.mainloop()