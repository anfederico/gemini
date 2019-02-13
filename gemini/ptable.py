import sys

def longest(columns, x):      
    l = {}
    for x in range(x):
        try: l[x] = max(len(w) for w in columns[x])
        except: pass
    return l
            
def resize(length, method, z):   
    
    if method == 'cols':
        x = z
        y = length/x
        if length%x != 0:
            y += 1        
    
    elif method == 'rows':
        y = z
        x = length/y
        if length%y != 0:
            x += 1          
    
    return int(x),int(y)
    
def columnify(listy, direction, x, y):
    
    columns = {}
    i, j = 0, 0
    if direction == 'lr':
        for k in range(x):
            columns[k] = []
            j = i
            while(j < len(listy)):
                try: columns[k].append(listy[j])
                except: pass
                j += x
            i += 1
    
    elif direction == 'tb':
        while j < len(listy):
            columns[i] = []
            for k in range(y):
                try: columns[i].append(listy[j])
                except: pass
                j += 1   
            i += 1      

    return columns

class tableize:

    def __init__(self, listy, cols = 0, rows = 0):
        
        if cols == 0 and rows == 0:
            print('Value Error: Set a value for either cols or rows.\n')
            raise ValueError 
            
        if cols != 0 and rows != 0:
            print('Value Error: Set either cols or rows, not both.\n')
            raise ValueError     
            
        if cols < 0 or rows < 0:
            print('Value Error: Positive integers only.\n')
            raise ValueError              
                         
        if cols != 0:
            self.method = 'cols'
            self.direction = 'lr'
            self.x, self.y = resize(len(listy), 'cols', cols)
                    
        elif rows != 0:
            self.method = 'rows'
            self.direction = 'tb'
            self.x, self.y = resize(len(listy), 'rows', rows)    
        
        self.listy = listy
        self.columns = columnify(listy, self.direction, self.x, self.y)
    
    def flip(self):
        if self.direction == 'lr': self.direction = 'tb' 
        elif self.direction == 'tb': self.direction = 'lr'
        self.columns = columnify(self.listy, self.direction, self.x, self.y)    
        
    def switch(self):
        if self.method == 'cols':
            self.method = 'rows'
            self.direction = 'tb'            
            self.x, self.y = resize(len(self.listy), 'rows', self.x)    
        
        elif self.method == 'rows':
            self.method = 'cols'
            self.direction = 'lr'
            self.x, self.y = resize(len(self.listy), 'cols', self.y)    
        
        self.columns = columnify(self.listy, self.direction, self.x, self.y)
    
    def show(self):
        self.text() 

    def write(self, filename, bullet = '', spaces = 1, spacer = ' '):
        temp = sys.stdout
        sys.stdout = open(filename+'.txt', 'w')
        self.text(bullet, spaces, spacer)
        sys.stdout = temp

    def text(self, bullet = '', spaces = 1, spacer = ' '):
        manu = spacer*spaces
        l = longest(self.columns, self.x)  
        for y in range(self.y):
            for x in range(self.x):
                try: 
                    auto = spacer*(l[x]-len(self.columns[x][y]))
                    sys.stdout.write(bullet+self.columns[x][y]+auto+manu)                    
                except: pass    
            sys.stdout.write('\n')