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
    def displayDialog(self,message):
        md = gtk.MessageDialog(self.window,
                               0, gtk.MESSAGE_INFO,
                               gtk.BUTTONS_CLOSE, message)
        md.run()
        md.destroy()

    # This callback quits the program
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False
    
    def square_callback(self, widget, data=None):
        pass
        
    def insert_callback(self, widget, data=None):
        pass
        
    def solve_callback(self, widget, data=None):
        startTime = time.time()
        
        if(self.radio_button_constraints.get_active()):
            ret = self.solve_constraints()
        else:
            ret = self.solve_rules()
            
        endTime = time.time()
        duration = (endTime - startTime) * 1000
            
        if(ret == False):
            self.displayDialog('Could not solve the puzzle')
            return
        
        if ret != 'EINVAL':
            self.status_label.set_text("Time: " + str(duration) + " ms")        
        
        
    def reset_callback(self, widget, data=None):
        for square in ui_squares:
            self.buttons[square].set_label("       ")
        
        self.values = {}
        self.grid = ''
        self.status_label.set_text('')
        
    def set_square(self, square, value):
        self.buttons[square].set_label("   " + str(value) + "   ")
        
    def open_callback(self, widget, data=None):
        self.filesel.show()
        
    def file_ok_sel(self, w):
        self.entry.set_text(self.filesel.get_filename())
        self.filesel.hide()
        try:
            file = open(self.entry.get_text(),"r")
            tmp = file.read()
            if(len(tmp) == 0):
                print "Invalid File"
                return False
            
            grid = ''
            for i in tmp:
                if i.isdigit():
                    grid = grid + i
                    
            self.grid = grid
            self.solver = Solver(self.grid)
            self.values = self.solver.grid_values()
            #print self.values
            self.display_sudoku(self.values)
        except IOError, e:
            print "Error opening file ({0}): {1}".format(e.errno, e.strerror)
            return False
            
    def display_sudoku(self, values):
        keys = values.keys()
        
        for key in keys:
            self.buttons[key].set_label("   " + values[key] + "   ")

    def __init__(self):
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        # Set the window title
        self.window.set_title("SuDoKu")
        self.window.set_resizable(False)

        # Set a handler for delete_event that immediately
        # exits GTK.
        self.window.connect("delete_event", self.delete_event)

        # Sets the border width of the window.
        self.window.set_border_width(20)
        
        
        self.filesel.ok_button.connect("clicked", self.file_ok_sel)
        self.filesel.cancel_button.connect("clicked", lambda w: self.filesel.hide())
        
        vbox = gtk.VBox(False, spacing=10)
        
        # Put the table in the main window
        self.window.add(vbox)  
        
        #vbox.pack_start(child, expand=False, fill=True, padding=0)

        # Create a 12x14 table
        sudoku_grid = gtk.Table(12, 14, False) 
        
        self.buttons = {}
        
        for square in ui_squares:
            row = int(alpha_to_numbers[square[0]])
            column = int(square[1])
            
            if (row > 3 and row < 7):
                row += 1
            elif (row > 6):
                row += 2
                
            if (column > 3 and column < 7):
                column += 1
            elif (column > 6):
                column += 2
                
            button = gtk.ToggleButton(square)
            button.set_label("       ")
            button.connect("toggled", self.square_callback, square)
            sudoku_grid.attach(button, column - 1, column, row - 1, row)
            button.show()
        
            self.buttons[square] = button
            
        for i in range (1,10):
            if not (i == 4 or i == 8):
                continue
            for j in range (1,12):
                if(j == 4 or j == 8):
                    continue
                label = gtk.Label("-------")
                sudoku_grid.attach(label, j - 1, j, i - 1, i)
                label.show()
                
        for i in range (1,10):
            if not (i == 4 or i == 8):
                continue
            for j in range (1,12):
                label = gtk.Label("|")
                sudoku_grid.attach(label, i - 1, i, j - 1, j)
                label.show()
                
        for i in range(1,10):
            row = i
            column = 14
            button = gtk.Button(square)
            button.set_label("   " + str(i) + "   ")
            button.connect("clicked", self.insert_callback, row)
            sudoku_grid.attach(button, column - 1, column, row - 1, row)
            #button.show()
        
        sudoku_grid.show()
        vbox.show()
        vbox.pack_start(sudoku_grid, False, False, padding=0)
        
        #Add check boxes here
        hbox = gtk.HBox(False,10)
        hbox.show()
        
        self.radio_button_constraints = gtk.RadioButton(group=None, label='Constraints Version')
        self.radio_button_constraints.show()
        
        hbox.pack_start(self.radio_button_constraints, False, False, padding=0)
        
        self.radio_button_rules = gtk.RadioButton(group=self.radio_button_constraints, label='Rules Version')
        self.radio_button_rules.show()
        
        hbox.pack_start(self.radio_button_rules, False, False, padding=0)
        
        vbox.pack_start(hbox, False, False, padding=0)
        
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
    

def main():
    grid1  = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
    grid2 = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
    gtk.main()
    return 0       

if __name__ == "__main__":
    MainWindow()
    main()
    
