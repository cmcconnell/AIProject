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
    pos_dic = {}    # used for saving the possibilities for the empty square
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
    ################ display the sudoku ###########
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
            possibilities = [d for d in self.digits]
            for u in unit:
                if values[u] not in '0.':
                    possibilities.remove(values[u])
            if len(possibilities) == 1:
                values[s] = possibilities[0]
                break
        
    def single_possibility_rule(self,values,square):
        s = square
        
        for unit in self.units[s]:
            for u in unit:
                if values[u] not in '0.' and self.pos_dic[s].count(values[u]) > 0:
                    self.pos_dic[s].remove(values[u])
        if len(self.pos_dic[s]) == 1:
            values[s] = self.pos_dic[square][0]
        
    def service(self,e):
        if e == 1:
            return [2,3]
        elif e == 2:
            return [1,3]
        elif e == 3:
            return [1,2]
    def get_possible_spots(self,spot):
        temp = []
        temp.append([self.rows.index(spot[0]) / 3 + 1, self.digits.index(spot[1]) / 3 + 1])
        temp.append([self.rows.index(spot[0]) % 3 + 1, self.digits.index(spot[1]) % 3 + 1])
        
        result = []
        temp_result = []
        
        row_index = (temp[0][0] - 1) * 3 - 1
        for j in self.service(temp[1][0]):
            row = self.rows[row_index + j]
            for k in self.service(temp[0][1]):
                temp1 = []
                for a in range(3):
                    location = row + str((k - 1) * 3 + a + 1)
                    temp1.append(location)
                temp_result.append(temp1)    
        adjacents = []
        for j in self.service(temp[1][1]):
            adjacent = (temp[0][1] - 1 ) * 3 + j - 1
            location = spot[0] + self.digits[adjacent]
            adjacents.append(location)
            
        result.append(adjacents)
        result.append([temp_result[0],temp_result[3]])
        result.append([temp_result[1],temp_result[2]])
            
        
        temp_result = []
        
        col_index = (temp[0][1] - 1) * 3 - 1
        for j in self.service(temp[1][1]):
            col = self.digits[col_index + j]
            for k in self.service(temp[0][0]):
                temp1 = []
                for a in range(3):
                    location = self.rows[(k - 1) * 3 + a] + col
                    temp1.append(location)
                temp_result.append(temp1)
        adjacents = []
        for j in self.service(temp[1][0]):
            adjacent = (temp[0][0] - 1 ) * 3 + j - 1
            location = self.rows[adjacent] + spot[1]
            adjacents.append(location)
        result.append(adjacents)
        result.append([temp_result[0],temp_result[3]])
        result.append([temp_result[1],temp_result[2]])
    
        
        return result
        
    def two_out_of_three_rule(self,values,square):
        result = self.get_possible_spots(square)
        adjacents = [result[0],result[3]]
        i = 0
        for spots in result:
            tmp = []
            if i != 0 and i !=3:
                for squares in spots:
                    t = []
                    for s in squares:
                        if values[s] not in '0.':
                            t.append(values[s])
                    tmp.append(t)
                a = tmp[0]
                b = tmp[1]
                inter = list(set(a).intersection(set(b)))
                if len(inter) == 1:
                    flag = 1
                    if i == 1 or i == 2:
                        for s in adjacents[0]:
                            if values[s] in '0.':
                                if  self.pos_dic[s].count(inter[0]) == 1: 
                                    flag = 0
                            else:
                                if  values[s] == inter[0]:
                                    flag = 0 
                        if flag == 1:
                            values[square] = inter[0]
                            break
                    elif i == 4 or i == 5:
                        for s in adjacents[1]:
                            if values[s] in '0.':
                                if  self.pos_dic[s].count(inter[0]) == 1: 
                                    flag = 0
                            else:
                                if  values[s] == inter[0]:
                                    flag = 0 
                        if flag == 1:
                            values[square] = inter[0]
                            break      
            i += 1 
    def solve(self,values):
        #values = self.grid_values()
        empties = self.empty_squares(values)
        
        for square in empties:
            self.pos_dic[square] = [s for s in self.digits] 
        
        #print emptys
        while len(empties) > 0:
            print len(empties), "empty squares left"
            tmp = len(empties)
            for square in empties:
                self.only_choice(values, square)
                if values[square] in '0.':
                    self.single_possibility_rule(values, square) 
                if values[square]  in '0.':
                    self.two_out_of_three_rule(values, square)
            empties = self.empty_squares(values)
            if tmp == len(empties):
                print "cannot solve this puzzle"
                return 
#        self.two_out_of_three_rule(values, "B2")
if __name__ == '__main__':
    test_grid = "003020600900305001001806400008102900700000008006708200002609500800203009005010300"
    solver = Solver(test_grid)
    values = solver.grid_values()
    solver.solve(values)
    solver.display(values)
