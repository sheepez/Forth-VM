class cell(object):
    """For Forth's purposes memory is divided into cells.
       This cell can store a signed number of a variable bit length."""

    ### Assuming that the integer is always signed is probably
    ### limiting. Might want to change things so that write()
    ### takes a binary string, and sort out signs and stuff at
    ### a higher level.
    def __init__(self,bit_count):
        self.bits = bit_count
        self._val = 0
        self._max_val = pow(2,self.bits-1) - 1
        self._overflow_offset = pow(2,self.bits)

    def write(self,integer):
        if integer > self._max_val:
            #raise OverflowError
            integer -= self._overflow_offset
        self._val = integer

    def read(self):
        return self._val
        
class stack(object):
    def __init__(self,max_cells,cell_size):
        self.cells = []
        self.SP = 0             #stack pointer
        for c in range(max_cells):
            self.cells.append(cell(cell_size))
            
    def push(self, integer):
        if self.SP > len(self.cells):
            #raise StackOverflow
            print "Overflow"
        else:
            self.cells[self.SP].write(integer)
            self.SP += 1
    def pop(self):
        if self.SP == 0:
            #raise StackUnderflow
            print "Underflow"
            return None
        else:
            self.SP -= 1
            val = self.cells[self.SP].read()
            self.cells[self.SP].write(0)
            return val
    def flush(self):
        for c in cells:
            c.write(0)
        self.SP = 0

    def __repr__(self):
        return str([x.read() for x in self.cells])
        
