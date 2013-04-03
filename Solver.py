'''
Created on 2013-4-3

@author: Administrator
'''
## Throughout this program we have:
##   r is a row,    e.g. 'A'
##   c is a column, e.g. '3'
##   s is a square, e.g. 'A3'
##   d is a digit,  e.g. '9'
##   u is a unit,   e.g. ['A1','B1','C1','D1','E1','F1','G1','H1','I1']
##   grid is a grid,e.g. 81 non-blank chars, e.g. starting with '.18...7...
##   values is a dict of possible values, e.g. {'A1':'12349', 'A2':'8', ...}
def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

class Solver:
    digits   = '123456789'
    rows     = 'ABCDEFGHI'
    cols     = digits
    squares  = cross(rows, cols)
    
    def __init__(self,grid):
        self.unitlist = ([cross(self.rows, c) for c in self.cols] +
                    [cross(r, self.cols) for r in self.rows] +
                    [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')])
        self.units = dict((s, [u for u in self.unitlist if s in u])
                     for s in self.squares)
        self.peers = dict((s, set(sum(self.units[s],[]))-set([s]))
                     for s in self.squares)
        self.grid = grid
    ################ Parse a Grid ################
    def grid_values(self):
        "Convert grid into a dict of {square: char} with '0' or '.' for empties."
        chars = [c for c in self.grid if c in self.digits or c in '0.']
        assert len(chars) == 81
        return dict(zip(self.squares, chars))

    def display(self, values):
        "Display these values as a 2-D grid."
        width = 1+max(len(values[s]) for s in self.squares)
        line = '+'.join(['-'*(width*3)]*3)
        for r in self.rows:
            print ''.join(values[r+c].center(width)+('|' if c in '36' else '')
                          for c in self.cols)
            if r in 'CF': print line
        print
    ################ Apply rules ####################

    def empty_squares(self,values):
        "Returns a list of the empty squares in values"
        return [s for s in self.squares if values[s] in '0.']
    
    # for each empty square, apply the rules in order; return false if grid doesn't change
    
    def only_choice(self,values, square):
        s = square
        for unit in self.units[s]:
            possibilities = ['1','2','3','4','5','6','7','8','9']
            for u in unit:
                if values[u] not in '0.':
                    possibilities.remove(values[u])
            if len(possibilities) == 1:
                values[s] = possibilities[0]
                break
        
    def single_possibility_rule(self,values,square):
        s = square
        possibilities = ['1','2','3','4','5','6','7','8','9']
        for unit in self.units[s]:
            for u in unit:
                if values[u] not in '0.' and possibilities.count(values[u]) > 0:
                    possibilities.remove(values[u])
        if len(possibilities) == 1:
            values[s] = possibilities[0]
        #print possibilities
    def solve(self,values):
        #values = self.grid_values()
        emptys = self.empty_squares(values)
        #print emptys
        while len(emptys) > 0:
            #print len(emptys)
            for square in emptys:
                self.only_choice(values, square)
                if values[square] in '0.':
                    self.single_possibility_rule(values, square) 
            emptys = self.empty_squares(values)

if __name__ == '__main__':
    test_grid = ".....89126...9534..98342.678..761....2...3.9171..24...96153..8.....1963.34...61.."
    solver = Solver(test_grid)
    values = solver.grid_values()
    solver.solve(values)
    solver.display(values)
