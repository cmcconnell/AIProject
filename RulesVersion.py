'''
Created on 2013-4-3

@author: Hao Zou
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
        self.row_units = [cross(r, self.cols) for r in self.rows]
        self.col_units = [cross(self.rows, c) for c in self.cols]
        self.box_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
        self.sub_groups = self.get_all_subgroups()
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
    ############################################################################################    
    # There may be only one possible choice for a particular Sudoku square. In the simplest 
    # case you have a group (row, column or region) that has eight squares allocated leaving 
    # only one remaining choice available; so the remaining number must go in that empty square.
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
    # When you look at individual squares you will often find that there is only one possibility 
    # left for the square. [Note: If there eight squares solved in the group then this is just the 
    # same as the only choice rule.] 
    def single_possibility_rule(self,values,square):
        s = square
        
        for unit in self.units[s]:
            for u in unit:
                if values[u] not in '0.' and self.pos_dic[s].count(values[u]) > 0:
                    self.pos_dic[s].remove(values[u])
        if len(self.pos_dic[s]) == 1:
            values[s] = self.pos_dic[square][0]
    # helper function for the two_out_of_three rule
    def service(self,e):
        if e == 1:
            return [2,3]
        elif e == 2:
            return [1,3]
        elif e == 3:
            return [1,2]
    # helper function for the two_out_of_three rule
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
    # Often you will find within a group of Sudoku squares that there is 
    # only one place that can take a particular number.    
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
            
    #Method: is_same_sg
    #Short Desc: Given a set of squares returns true if they are in 
    #the same sub group
    #Param1: A list of squares - ['A1','A2']
    #Return: True if squares in same sub group
    def is_same_sg(self,squares):
        #If squares is empty reurn false
        if(len(squares) < 1):
            return False
        #Handle list of size 2
        elif(len(squares) == 2):
            #self.sub_groups contains a list of all possible subgroups. Loop through each
            #of those and see if both squares in the list belong to the same sub group
            for sg in self.sub_groups:
                if squares[0] in sg and squares[1] in sg:
                    return True
            return False
        #If there are three squares
        elif(len(squares) == 3):
            #Same as above but for three squares
            for sg in self.sub_groups:
                if squares[0] in sg and squares[1] in sg and squares[2] in sg:
                    return True
            return False
        #If length > 3 return false
        else:
            return False 
    
    #Method: sg_assign
    #Short Desc: Assign a digit to square
    #Param1: Values {dict(square : value)}
    #Param2: Dictionary of all possible values in each square
    #Param3: Square. ex: 'A1'
    #Param4: A digit. ex: '1' or '2'
    #Return: None
    def sg_assign(self,values,pos,square,digit):
        #If value is already between 1-9 do nothing
        if (values[square]) not in '0.':
            return
        
        #Assign value, Set pos to '-'
        values[square] = digit
        pos[square] = ['-']
        
        #Remove the assigned value from all peers (row, column and box)
        for sq in self.peers[square]:
            tmp = pos[sq]
            if digit in tmp:
                tmp.remove(digit)     
                
    #Method: generate_pos
    #Short Desc: Generate possibility dictionary for a given grid
    #Param1: Values {dict(square : value)}
    #Return: Pos dictionary
    def generate_pos(self,values):
        #Create an array for each square with possibility[square] = [1-9]
        pos = {}
        for square in values.keys():
            pos[square] = [i for i in self.digits]
        
        #Eliminate possibilities from each square based on values of peers
        for square in values.keys():
            tmp = pos[square]
        
            #If a value is assigned its pos must be set to '-'
            if values[square] not in '0.':
                pos[square] = '-'
                continue
            
            #For each assigned square remove it from pos of all peers
            for i in self.peers[square]:
                if values[i] not in '0.' and values[i] in tmp:
                    tmp.remove(values[i])
                
            pos[square] = tmp
            
        return pos
        
    #Method: shared_subgroups_rule
    #Short Desc: Function implementing the shared subgroups rule. This will apply the rule on
    #values and update any squares which could be solved
    #Param1: Values {dict(square : value)}
    #Return: None
    def shared_subgroups_rule(self,values):
        #get the pos dictionary
        pos = self.generate_pos(values)
        
        #Try sub-group rule. This how it works:
        #1. For each row/column count number of times a digit occurs in pos dictionary of each square
        #2. If a number occurs only 2 or 3 times check if those squares are in same subgroup
        #3. If squares are in same SG then the digit can be eliminated from all other squares in the box
        for num in range(1,19):
            #For 1-9 (go though rows)
            #For 10-18 (go through columns)
            if num > 9:
                num = num -9
                tmp_units = self.col_units[num - 1]
            else:
                tmp_units = self.row_units[num - 1]    
                
            #array p is used to count the occurrence of each digit
            #init it with 0
            p  = []
            for i in range(10):
                p.append(0)          
        
            #for each digit i increment p[i]
            for square in tmp_units:            
                tmp = pos[square]
                for i in tmp:
                    #If tmp is '-' do nothing. 
                    if tmp != '-' and tmp != ['-']:
                        p[int(i)] = p[int(i)] + 1
                    
            #sg_squares will hold all squares where there are numbers that appear only 
            #twice or thrice in the row/column
            sg_squares = []
            for i in range(10):
                sg_squares = []
                if p[i] == 2 or p[i] == 3:
                    #get all squares where i is possible
                    for square in tmp_units:
                        if str(i) in pos[square]:
                            sg_squares.append(square)   
                            
                    #if squares in same sg remove i from pos of all squares in box
                    if(self.is_same_sg(sg_squares)):
                        #remove i from unit in which squares are
                        for unit in self.box_units:
                            if sg_squares[0] in unit:
                                for sq in unit:
                                    #We don't want to remove from the squares in sg_squares
                                    if sq in sg_squares:
                                        continue
                                    
                                    tmp = pos[sq]
                                    if str(i) in tmp:
                                        tmp.remove(str(i))
                                        #print 'Remove: ',i,sq,tmp
                                break
            
        #Once enough possibilities are eliminated we hope this will leave us with
        #some squares with pos[square] == 1. If so we can assign that digit to the square
        #single pos (assign  values to all squares that have only possible value)
        for sq in self.squares:
            tmp = pos[sq]
                
            if tmp == ['-'] or tmp == '-':
                continue
                
            if len(tmp) == 1:
                #print 'Assign sg: ', tmp[0], 'to', sq
                self.sg_assign(values, pos, sq, tmp[0])
                    
        #Apply the only choice rule as well
        empties = self.empty_squares(values)
        for sq in empties:
            self.only_choice(values, sq)    
    
    #Method: get_all_subgroups
    #Short Desc: Function generates all possible subgroups in a sudoku grid
    #Param1: None
    #Return: Array of all sub groups        
    def get_all_subgroups(self):
        #Each row/col has three sub groups (one in each box)
        sub_groups = []
        
        #Rows will have 'ABC...I'
        #For each alphabet in self.rows the sub group will be [A1,A2,A3],[A4,A5,A5] etc
        for i in self.rows:
            tmp = []
            for j in range(1,4):
                tmp.append(i + str(j))
            sub_groups.append(tmp)
            tmp = []
            for j in range(4,7):
                tmp.append(i + str(j))
            sub_groups.append(tmp)
            tmp = []
            for j in range(7,10):
                tmp.append(i + str(j))
            sub_groups.append(tmp)
        
        #Self.cols will have '123...9'
        #Sub groups will be of the form [A1,B1,C1], [D1,E1,F1] etc
        for i in self.cols:
            tmp = []
            for j in ('ABC'):
                tmp.append(j + str(i))
            sub_groups.append(tmp)
            tmp = []
            for j in ('DEF'):
                tmp.append(j + str(i))
            sub_groups.append(tmp)
            tmp = []
            for j in ('GHI'):
                tmp.append(j + str(i))
            sub_groups.append(tmp)   
            
        return sub_groups
     
    #Method: naked_twin
    #Short Desc: Function that implements the naked_twin rule
    #Param1: Values {dict(square : value)}
    #Return: None  
    def naked_twin(self,values):
        #Get the pos dictionary
        pos = self.generate_pos(values)
        
        #Naked twin rule: If in any row/column there appears a paris like '23', '24' etc which
        #appear in pos value of only two square then this means that those two numbers cannot 
        #appear in any other squares in that unit. So we eliminate them. 
        #Go through all squares in rows/cols and boxes and see if there are 
        #any possible candidates for naked twin
        #Range 1 - 9 for rows. 10-18 for columns and 19-27 for box units
        for num in range(1,28):            
            if(num < 10):
                tmp_unit = self.row_units[num -1]
            elif(num < 19):
                num = num - 9
                tmp_unit = self.col_units[num -1]
            else:
                num = num - 18
                tmp_unit = self.box_units[num -1]
                
            squares = []
            #get all squares in the unit with length = 2                 
            for sq in tmp_unit:
                if(len(pos[sq]) == 2):
                    squares.append(sq)
            
            pairs = []
            #for each square with len(pos) = 2 see if they have common values with
            #any other square in the unit. If they do then they are twins
            for i in range(0,len(squares)):
                for j in range(i+1,len(squares)):
                    if pos[squares[i]] == pos[squares[j]]:
                        pairs.append([squares[i],squares[j]])
            
            #If pair in subgroup -> eliminate in box and unit
            #else eliminate only from unit
            for pair in pairs:
                #If in sub group, eliminate from box
                if(self.is_same_sg(pair)):
                    #remove i from box in which squares are
                    #Remove from corresponding row/column as well
                    for unit in self.box_units:
                        if pair[0] in unit:
                            for sq in unit:
                                if sq in pair:
                                    continue
                                tmp = pos[sq]
                                for i in pos[pair[0]]:
                                    if str(i) in tmp:
                                        #print 'Remove box: ',i,sq,tmp
                                        tmp.remove(str(i))                                        
                            break
                    
                #Pairs are not in a sub group so Eliminate only from row/column
                #First check if the pairs have row in common or a column
                sq1 = pair[0]
                sq2 = pair[1]
                #If first char is same then they are in same row
                if sq1[0] == sq2[0]:
                    row_flag = True
                    rowcol_units = self.row_units
                #if last char is same then they are in same column
                elif sq1[1] == sq2[1]:
                    row_flag = False
                    rowcol_units = self.col_units
                #If nothing common then they are in same box but we have already 
                #handled this previously
                else:
                    continue
                
                #Eliminate                    
                for unit in rowcol_units:
                    if pair[0] in unit:
                        for sq in unit:
                            if sq in pair:
                                continue
                            tmp = pos[sq]
                            for i in pos[pair[0]]:
                                if str(i) in tmp:
                                    #print 'Remove row/col: ',i,sq,tmp
                                    tmp.remove(str(i))
                        break
                    
        #As in sub group rule try to assign values to squares which have narrowed down
        #single pos (assign  values to all squares that have only possible value)
        for sq in self.squares:
            tmp = pos[sq]
                
            if tmp == ['-'] or tmp == '-':
                continue
                
            if len(tmp) == 1:
                #print 'Assign nk: ', tmp[0], 'to', sq
                self.sg_assign(values, pos, sq, tmp[0])
                    
        #only choice
        empties = self.empty_squares(values)
        for sq in empties:
            self.only_choice(values, sq)
                
    def solve(self,values):
        #values = self.grid_values()
        empties = self.empty_squares(values)
        
        for square in empties:
            self.pos_dic[square] = [s for s in self.digits] 
        
        #print emptys
        while len(empties) > 0:
            #print len(empties), "empty squares left"
            tmp = len(empties)
            for square in empties:
                self.only_choice(values, square)
                if values[square] in '0.':
                    self.single_possibility_rule(values, square) 
                if values[square]  in '0.':
                    self.two_out_of_three_rule(values, square)
            self.shared_subgroups_rule(values)
            self.naked_twin(values)
            empties = self.empty_squares(values)
            if tmp == len(empties):
                print len(empties), "empty squares left"
                print "cannot solve this puzzle"
                return False
#        self.two_out_of_three_rule(values, "B2")
if __name__ == '__main__':
    test_grid = "003020600900305001001806400008102900700000008006708200002609500800203009005010300"
    hard_grid = "7.....4...2..7..8...3..8.799..5..3...6..2..9...1.97..6...3..9...3..4..6...9..1.35"
    solver = Solver(test_grid)
    values = solver.grid_values()
    solver.solve(values)
    solver.display(values)
