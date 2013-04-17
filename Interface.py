# Program: UI for Sudoku
# Author: Vishwanath Pai
# Creation Date: 03/27/2013 23:16
# UI for the Sudoku agent

import pygtk
pygtk.require('2.0')
import gtk
import math
import time
from random import *

#Import both the Sudoku solvers 
from RulesVersion import * 
import ConstraintVersion

#Method: ui_cross
#Short Desc: Same as cross method in ConstraintsVersion.py
#Param1: A list
#Param2: A list
#Return: List of AxB
def ui_cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

ui_digits   = '123456789'
ui_rows     = 'ABCDEFGHI'
ui_cols     = ui_digits
ui_squares  = ui_cross(ui_rows, ui_cols)
                    
alpha_to_numbers = {}
for i in range(0,9):
    alpha_to_numbers[ui_rows[i]] = ui_digits[i]    

class MainWindow:
    
    index = 0
    entry = gtk.Entry()
    filesel = gtk.FileSelection("Select a file")
    values = {}
    solver = ''
    grid = ''
    
    #Method: displayDialog
    #Short Desc: Displays message in a dislog box
    #Param1: 'A Message to display'
    #Return: None
    def displayDialog(self,message):
        md = gtk.MessageDialog(self.window,
                               0, gtk.MESSAGE_INFO,
                               gtk.BUTTONS_CLOSE, message)
        md.run()
        md.destroy()

    #This callback quits the program
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False
    
    #Just a place holder, does nothing.
    def square_callback(self, widget, data=None):
        pass
    
    #Just a place holder, does nothing.   
    def insert_callback(self, widget, data=None):
        pass
    
    #Method: solve_callback
    #Short Desc: Event handler for 'Solve' button click. 
    #Param1: The widget which raised the event
    #Param2: Any data that needs to be passed to the function
    #Return: None    
    def solve_callback(self, widget, data=None):
        #To calculate total time of execution
        startTime = time.time()
        
        #Based on the value of the radio button call constraints or rules version
        if(self.radio_button_constraints.get_active()):
            ret = self.solve_constraints()
        else:
            ret = self.solve_rules()
            
        endTime = time.time()
        duration = (endTime - startTime) * 1000
            
        #Display error if solver returns False
        if(ret == False):
            self.displayDialog('Could not solve the puzzle')
            return
        
        #Display time on the label next to 'Reset'
        if ret != 'EINVAL':
            self.status_label.set_text("Time: " + str(duration) + " ms")        
      
    #Method: reset_callback
    #Short Desc: Event handler for 'Reset' button click. 
    #Param1: The widget which raised the event
    #Param2: Any data that needs to be passed to the function
    #Return: None    
    def reset_callback(self, widget, data=None):
        #Blank out all labels of the squares
        for square in ui_squares:
            self.buttons[square].set_label("       ")
        
        #Reset all other data
        self.values = {}
        self.grid = ''
        self.status_label.set_text('')
        
    #Method: set_square
    #Short Desc: Assign value to a particular square (display the value) 
    #Param1: Square
    #Param2: Digit
    #Return: None
    def set_square(self, square, value):
        self.buttons[square].set_label("   " + str(value) + "   ")
        
    #Method: open_callback
    #Short Desc: Event handler for 'Open' button click. 
    #Param1: The widget which raised the event
    #Param2: Any data that needs to be passed to the function
    #Return: None
    def open_callback(self, widget, data=None):
        self.filesel.show()
        
    #Method: file_ok_sel
    #Short Desc: Event handler for 'Ok' button click in the file select window 
    #Param1: The widget which raised the event
    #Return: None
    def file_ok_sel(self, w):
        #Display the selected file name in the text box
        self.entry.set_text(self.filesel.get_filename())
        
        #Hide the file select dialog
        self.filesel.hide()
        
        #Try to open the file and read
        try:
            #Open file in read only mode
            file = open(self.entry.get_text(),"r")
            tmp = file.read()
            if(len(tmp) == 0):
                print "Invalid File"
                return False
            
            grid = ''
            
            #Parse only digits and dots. Ignore all else
            for i in tmp:
                if i.isdigit() or i == '.':
                    grid = grid + i
                    
            self.grid = grid
            
            #Get the values from Solver (parse the grid)
            self.solver = Solver(self.grid)
            self.values = self.solver.grid_values()
            
            #Display the puzzle on screen
            self.display_sudoku(self.values)
        except IOError, e:
            print "Error opening file ({0}): {1}".format(e.errno, e.strerror)
            return False
            
    #Method: display_sudoku
    #Short Desc: Display values on screen 
    #Param1: Values dictionary
    #Return: None
    def display_sudoku(self, values):
        keys = values.keys()
        
        for key in keys:
            self.buttons[key].set_label("   " + values[key] + "   ")

    def __init__(self):
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        # Set the window title The widget which raised the eventand set resizable to False
        self.window.set_title("SuDoKu")
        self.window.set_resizable(False)

        # Set a handler for delete_event that immediately
        # exits GTK.
        self.window.connect("delete_event", self.delete_event)

        # Sets the border width of the window.
        self.window.set_border_width(20)        
        
        #Set event handlers for OK and Cancel buttons in the file selector
        self.filesel.ok_button.connect("clicked", self.file_ok_sel)
        self.filesel.cancel_button.connect("clicked", lambda w: self.filesel.hide())
        
        #Create a vertical box that holds all the widgets in the screen
        vbox = gtk.VBox(False, spacing=10)
        
        #Add the vbox to the window (all other widgets will be added to this vbox
        self.window.add(vbox)  
        
        # Create a 12x14 table which holds the sudoku grid
        sudoku_grid = gtk.Table(12, 14, False) 
        
        #Buttons holds all the buttons on the grid. This is helpful to populate
        #them with values
        self.buttons = {}
        
        #For each square create a button on the grid
        for square in ui_squares:
            #Calculate the row and column in which each square goes 
            #(we translate A,B,C etc to 1,2,3... for row numbers)
            row = int(alpha_to_numbers[square[0]])
            column = int(square[1])
            
            #Row 4,8 are filled with '|'
            if (row > 3 and row < 7):
                row += 1
            elif (row > 6):
                row += 2
            
            #Column 4,8 are filled with '----'    
            if (column > 3 and column < 7):
                column += 1
            elif (column > 6):
                column += 2
                 
            #Create new button and attach it to the table
            button = gtk.ToggleButton(square)
            button.set_label("       ")
            button.connect("toggled", self.square_callback, square)
            sudoku_grid.attach(button, column - 1, column, row - 1, row)
            button.show()
        
            self.buttons[square] = button
            
        #Add '------' for column 5,8
        for i in range (1,10):
            if not (i == 4 or i == 8):
                continue
            for j in range (1,12):
                if(j == 4 or j == 8):
                    continue
                label = gtk.Label("-------")
                sudoku_grid.attach(label, j - 1, j, i - 1, i)
                label.show()
           
        #Add '|' for row 4,8    
        for i in range (1,10):
            if not (i == 4 or i == 8):
                continue
            for j in range (1,12):
                label = gtk.Label("|")
                sudoku_grid.attach(label, i - 1, i, j - 1, j)
                label.show()
        
        #Show the grid and pack it into the vbox
        sudoku_grid.show()
        vbox.show()
        vbox.pack_start(sudoku_grid, False, False, padding=0)
        
        #Add radio buttons
        hbox = gtk.HBox(False,10)
        hbox.show()
        
        self.radio_button_constraints = gtk.RadioButton(group=None, label='Constraints Version')
        self.radio_button_constraints.show()
        
        hbox.pack_start(self.radio_button_constraints, False, False, padding=0)
        
        self.radio_button_rules = gtk.RadioButton(group=self.radio_button_constraints, label='Rules Version')
        self.radio_button_rules.show()
        
        hbox.pack_start(self.radio_button_rules, False, False, padding=0)
        
        vbox.pack_start(hbox, False, False, padding=0)
        
        #Display the file selection widgets
        file_grid = gtk.Table(1, 3, False)
        
        label = gtk.Label("Select input file: ")
        file_grid.attach(label, 0, 1, 0, 1)
        label.show()
        
        self.entry.set_width_chars(30)
        file_grid.attach(self.entry, 1, 2, 0, 1)
        self.entry.show()
        
        button = gtk.Button("File")
        button.set_label("Open")
        button.connect("clicked", self.open_callback, "File")
        button.show()
        file_grid.attach(button, 2, 3, 0, 1)
        file_grid.show()
        
        vbox.pack_start(file_grid, False, False, padding=0)
        
        hbox = gtk.HBox(False,10)
        hbox.show()
        
        #Display the Solve, Reset buttons and the Time display label
        button = gtk.Button("Solve")
        button.set_label("Solve")
        button.connect("clicked", self.solve_callback, "Solve")
        button.show()
        
        hbox.pack_start(button, False, False, padding=0)
        
        button = gtk.Button("Reset")
        button.set_label("Reset")
        button.connect("clicked", self.reset_callback, "Reset")
        button.show()
        
        hbox.pack_start(button, False, False, padding=10)
        
        self.status_label = gtk.Label('')
        self.status_label.show()
        hbox.pack_start(self.status_label, False, False, padding=0)        
        
        vbox.pack_start(hbox, False, False, padding=0)
        
        self.window.show()
        
    #Method: solve_constraints
    #Short Desc: Solve puzzle using constraints version
    #Param1: None
    #Return: 'EINVAL' on invalid file and False if puzzle couldn't be solved
    def solve_constraints(self):
        ret = True
        if self.grid == '':
            ret = self.file_ok_sel(None)
        
        if ret == False:
            return 'EINVAL'

        ret = self.values = ConstraintVersion.solve(self.grid)
        if ret: 
            self.display_sudoku(self.values)
        else:
            return False
    
    #Method: solve_constraints
    #Short Desc: Solve puzzle using rules version
    #Param1: None
    #Return: 'EINVAL' on invalid file and False if puzzle couldn't be solved
    def solve_rules(self):
        ret = True
        if self.grid == '':
            ret = self.file_ok_sel(None)
        
        if ret == False:
            return 'EINVAL'
        
        self.solver = Solver(self.grid)
        ret = self.solver.solve(self.values)
        self.display_sudoku(self.values)        
        return ret
    
#Main function. Starts the UI.
def main():
    grid1  = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
    grid2 = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
    gtk.main()
    return 0       

if __name__ == "__main__":
    MainWindow()
    main()
    
