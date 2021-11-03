import sys
import tkinter as tk

def valid(board, row, col, digit):
    for x in range(9):
        if board[row][x] == digit:
            return False

    for x in range(9):
        if board[x][col] == digit:
            return False

    startRow = row - row % 3
    startCol = col - col % 3

    for x in range(3):
        for y in range(3):
            if board[x + startRow][y + startCol] == digit:
                return False

    return True 

def solve(board, row, col):
    
    if (row == 8 and col == 9):
        return True

    if col == 9:
        row += 1
        col = 0

    if board[row][col] > 0:
        return solve(board, row, col+1)

    for digit in range(1, 10, 1):

        if valid(board, row, col, digit):
            board[row][col] = digit

            if solve(board, row, col+1):
                return True

        board[row][col] = 0
    return False

def print_game(board):
    for i in range(9):
        for j in range(9):
            print(board[i][j], end = " ")
        print()

def main():
    board = [ 
            [3, 0, 2, 6, 0, 0, 9, 0, 1],
            [0, 0, 0, 9, 1, 0, 0, 0, 2],
            [0, 9, 0, 0, 5, 4, 0, 0, 8],
            [0, 2, 0, 0, 4, 5, 8, 1, 7],
            [8, 5, 0, 7, 0, 0, 3, 0, 0],
            [4, 0, 0, 0, 0, 0, 2, 6, 5],
            [6, 0, 5, 0, 0, 9, 0, 2, 0],
            [0, 3, 0, 0, 0, 2, 5, 0, 0],
            [0, 0, 9, 5, 0, 8, 0, 4, 6],
            ]
    
    board1 = [ 
             [0, 7, 0, 0, 2, 0, 9, 0, 0],
             [0, 4, 0, 8, 0, 6, 0, 0, 0],
             [0, 1, 2, 0, 0, 0, 3, 0, 0],
             [0, 0, 0, 0, 0, 0, 8, 7, 0],
             [0, 6, 0, 9, 7, 2, 0, 5, 0],
             [0, 2, 5, 0, 0, 0, 0, 0, 0],
             [0, 0, 1, 0, 0, 0, 2, 9, 0],
             [0, 0, 0, 5, 0, 4, 0, 3, 0],
             [0, 0, 7, 0, 6, 0, 0, 1, 0],
             ]   

    print_game(board1)
    print()
    solve(board1, 0, 0)
    print_game(board1)

if __name__ == '__main__':
    main()