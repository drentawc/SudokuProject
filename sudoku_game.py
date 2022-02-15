from bs4 import BeautifulSoup
from functools import partial
import tkinter as tk
import requests

#Sudoku UI class to build tkinter frame to hold all of the other frames and make board
class SudokuUI(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
         
        self.soup = SudokuWebScraper()
        self.board = self.soup.puzzle

        self.rowconfigure(0, weight=2)
        self.rowconfigure(1, weight=1)

        self.sudoku = SudokuBoard(self.board)
        self.sudoku.grid(row=0, column=0)
        self.button_frame = self.make_button_frame()
        self.button_frame.grid(row=1, column=0)

        self.difficulty_frame = self.make_difficulty_frame()
        self.difficulty_frame.grid(row=0, column=1)

        self.set_board()
        self.victory_counter = 0
        self.current_difficulty = 0

        self.after(2000, self.check_victory)

    #Check board state to see if victory has been achieved
    def check_victory(self):
        
        if (self.check_board()):
            
            print("Victory!")

            #Need to fix victory message
            # if self.victory_counter == 1:
            #     victory = tk.Toplevel(self)
            #     tk.Label(victory, text="Victory!").grid(row=0, column=0)
            #     tk.Button(victory, text="New Puzzle", command=partial(self.get_new_puzzle, self.current_difficulty)).grid(row=1, column=0)

        self.after(2000, self.check_victory)

    #Set the board depending on the game
    def set_board(self):
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0:
                    self.sudoku.boxes[row][col].insert(0, "")
                    self.sudoku.boxes[row][col].config(font=('Helvetica', 18, 'bold'))
                else:
                    self.sudoku.boxes[row][col].insert(0, self.board[row][col])
                    self.sudoku.boxes[row][col].config(font=('Helvetica', 18, 'bold'))
                    self.sudoku.boxes[row][col].config(state='disabled')

    #Make button frame for resetting and solving the puzzle
    def make_button_frame(self):
        frame = tk.Frame()
        tk.Button(frame, text="Reset Puzzle", command=partial(self.set_boxes, "")).grid(row=0, column=0)
        tk.Button(frame, text="Solve Puzzle", command=partial(self.solve_puzzle, 0, 0)).grid(row=0, column=1)

        return frame

    #Make button frame to set the boards puzzle with different difficulties
    def make_difficulty_frame(self):
        frame = tk.Frame()

        tk.Button(frame, text="Easy", command=partial(self.get_new_puzzle, 0)).grid(row=0, column=0)
        tk.Button(frame, text="Medium", command=partial(self.get_new_puzzle, 1)).grid(row=1, column=0)
        tk.Button(frame, text="Hard", command=partial(self.get_new_puzzle, 2)).grid(row=2, column=0)

        return frame

    #Get new puzzle from the web scraper class
    def get_new_puzzle(self, difficulty):
        self.soup.get_new_puzzle(difficulty)
        self.board = self.soup.puzzle
        self.current_difficulty = difficulty
        self.reset_board()
        self.set_board()

    #Reset the board to the starting positions
    def reset_board(self):
        self.victory_counter = 0

        for row in range(9):
            for col in range(9):
                self.sudoku.boxes[row][col].config(state='normal')
                self.sudoku.boxes[row][col].delete(0, tk.END)

    #Set all boxes to the character parameter
    def set_boxes(self, character):
        for row in range(9):
            for col in range(9):
                self.sudoku.boxes[row][col].delete(0, tk.END)
                self.sudoku.boxes[row][col].insert(0, character)
    
    #Solve puzzle using back tracking algorithm
    def solve_puzzle(self, row, col):

        if row == 0 and col == 0:
            self.set_boxes(0)

        if (row == 8 and col == 9):
            return True

        if col == 9:
            row += 1
            col = 0

        if int(self.sudoku.boxes[row][col].get()) > 0:
            return self.solve_puzzle(row, col+1)

        for digit in range(1, 10, 1):
            if self.valid_board(row, col, digit):
                self.sudoku.boxes[row][col].delete(0, tk.END)
                self.sudoku.boxes[row][col].insert(0, digit)

                if self.solve_puzzle(row, col+1):
                    self.victory_counter = 1
                    return True
            
            self.sudoku.boxes[row][col].delete(0, tk.END)
            self.sudoku.boxes[row][col].insert(0, 0)

        return False

    #Check if the board position is valids
    def valid_board(self, row, col, digit):
        for x in range(9):
            if int(self.sudoku.boxes[row][x].get()) == digit:
                return False

        for x in range(9):
            if int(self.sudoku.boxes[x][col].get()) == digit:
                return False

        startRow = row - row % 3
        startCol = col - col % 3

        for x in range(3):
            for y in range(3):
                if int(self.sudoku.boxes[x + startRow][y + startCol].get()) == digit:
                    return False
        return True

    #Check entire board to see if current solution is correct
    def check_board(self):

        for row in range(9):
            if not self.check_row(row):
                return False
        
        for col in range(9):
            if not self.check_column(col):
                return False

        for row in range(3):
            for col in range(3):
                if not self.check_square(row, col):
                    return False

        if self.victory_counter > 0:
            self.victory_counter += 1
        
        return True

    #Check 3x3 square of the board
    def check_square(self, row, col):
        return self.check_block(
            [
                self.sudoku.boxes[curr_row][curr_col].get()
                for curr_row in range(row * 3, (row + 1) * 3)
                for curr_col in range(col * 3, (col + 1) * 3)
            ]
        )

    #Check column of the board
    def check_column(self, col):
        current_col = []
        for i in range(9):
            current_col.append(self.sudoku.boxes[i][col].get())

        return self.check_block(current_col)

    #Check row of the board
    def check_row(self, row):
        current_row = []
        for i in range(9):
            current_row.append(self.sudoku.boxes[row][i].get())

        return self.check_block(current_row)

    #Check that the passed block contains one of each number
    def check_block(self, block):
        return set(block) == set(['1', '2', '3', '4', '5', '6', '7', '8', '9'])

#Class to get puzzles off of the web 
class SudokuWebScraper():
    def __init__(self):

        self.easy_url = 'https://menneske.no/sudoku/eng/random.html?diff=3'
        self.medium_url = 'https://menneske.no/sudoku/eng/random.html?diff=4'
        self.hard_url = 'https://menneske.no/sudoku/eng/random.html?diff=5'

        self.get_new_puzzle(0)

    #Get new puzzle depending on difficulty
    def get_new_puzzle(self, difficulty):
        if difficulty == 0:
            self.response = requests.get(self.easy_url)
        elif difficulty == 1:
            self.response = requests.get(self.medium_url)
        elif difficulty == 2:
            self.response = requests.get(self.hard_url)

        self.soup = BeautifulSoup(self.response.content, 'html.parser') 
        rows = self.soup.find_all("tr", {"class" : "grid"})

        self.puzzle = []
        self.data = []
        self.get_puzzle(rows)
        self.format_puzzle() 

    #Set data class variable with w
    def get_puzzle(self, rows):
        for row in rows:
            cols= row.find_all("td")
            for col in cols:
                digit = col.text
                if digit != '\xa0':
                    self.data.append(int(digit))
                else:
                    self.data.append(0)
    
    def format_puzzle(self):
        self.puzzle = [self.data[x:x+9] for x in range(0, len(self.data), 9)]

#Window to display when user completes sudoku board
class VictoryWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Victory")
        self.geometry("200x100")
        self.label = tk.Label(self, text="Victory!").grid(row=0, column=0)
        self.button = tk.Button(self, text="New Puzzle").grid(row=1, column=0)

#Class to build to sudoku board frame
class SudokuBoard(tk.Frame):
    def __init__(self, board):
        super().__init__()
        self.boxes = []
        self.board = board
        self.build_board()

    #Build sudoku board of 9x9 tkinter entries
    def build_board(self):
        for x in range(9):
            row = []
            for y in range(9):
                entry = tk.Entry(self, width=2, justify=tk.CENTER, selectborderwidth=2)
                entry.grid(row=x, column=y)
                row.append(entry)
            self.boxes.append(row)

def main():
    root = tk.Tk()
    root.title("Sudoku")
    root.geometry("500x400")

    root.columnconfigure(0, weight=2)
    root.columnconfigure(1, weight=1)

    frame = SudokuUI(root)
    frame.grid(row=0, column=1)

    time.sleep(5)
    root.mainloop()

if __name__ == '__main__':
    main()