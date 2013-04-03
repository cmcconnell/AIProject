"""
Foundations of Artificial Intelligence, Spring 2013

This version of our program takes a rules-based approach to solving sudoku
puzzles. It applies strategy rules to fill in blanks in the sudoku puzzle
like a person solving the puzzle would.

Sources:
Peter Norvig's program -  http://norvig.com/sudopy.shtml
Sudoku strategies - http://www.sudokudragon.com/sudokustrategy.htm
"""

from Solver import Solver

def run():
    filename = 'sudoku'
    file = open(filename)
    grid = file.read().strip()
    solver = Solver(grid)
    values = solver.grid_values()
    print "-----------------------------initial------------------------------"
    solver.display(values)
    solver.solve(values)
    print "---------------------------after solving--------------------------"
    solver.display(values)
if __name__ == '__main__':
    run()


