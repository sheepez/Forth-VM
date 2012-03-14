class cell(object):
    """Cell Class for Forth VM:
       - cells are memory units, the cell size is generally fixed
         so these cells are initiated with a specified size in bits
       - the cell stores a value as a 2's complement signed integer
       - if the value is too big for the number of bits, will overflow
         by looping round, currently without throwing an exception
       - write(int) can take any integer and will deal with overflows if
         they happen

       Changes:
       - changed overflow handler to while loop in case it needs to loop back
         more than once, this is still pretty crude and needs more work
       """
    
    def __init__(self,bit_count):
        self.bits = bit_count
        self._val = 0
        # The biggest number for n bits using 2's complement is 2^(n-1) - 1
        self._max_val = pow(2,self.bits-1) - 1
        self._overflow_offset = pow(2,self.bits)

    def write(self,integer):
        # Check for overflow
        while integer > self._max_val:
            # Loop back
            integer -= self._overflow_offset

        self._val = integer

    def read(self):
        return self._val

class stack(object):
    def __init__(self,max_cells,cell_size):
        self.cells = []
        self.SP = -1             # Stack Pointer
        for c in range(max_cells):
            self.cells.append(cell(cell_size))
            
    def push(self, integer):

        if self.SP > len(self.cells):
            #raise StackOverflow
            print "Overflow"
        else:
            self.SP += 1
            self.cells[self.SP].write(integer)
            
    def pop(self):

        if self.SP <= 0:
            #raise StackUnderflow
            print "Underflow"
            return None
        else:

            val = self.cells[self.SP].read()
            self.cells[self.SP].write(0)
            self.SP -= 1
            return val
    def _flush(self):
        # Reset the stack
        for c in cells:
            c.write(0)
        self.SP = -1

    def __repr__(self):
        return "<Stack object with %d cells>" % len(self.cells)

    def __str__(self):
        s = ""
        for i in range(len(self.cells)):
            
            if i == self.SP:
                s += (" " + str(self.cells[i].read()) + " <-TOS ")
            else:
                s += (" " + str(self.cells[i].read()))
                
        return s
        
class memory(object):
    """This is a list of cells.
       Currently only list-style access and assignment are implemented.
       Indices are equivalent to addresses.

       See http://docs.python.org/reference/datamodel.html for more
       information on what perhaps ought to be implemented."""
    
    def __init__(self,max_cells,cell_size):
        self.cells = []
        for c in range(max_cells):
            self.cells.append(cell(cell_size))

    # List-style behaviour
    def __setitem__(self,addr,val):
        self.cells[addr].write(val)
    def __getitem__(self,addr):
        return self.cells[addr].read()

    def _dump(self,start_addr,cell_count):
        print
        for i in range(start_addr,start_addr + cell_count):
            print str(i) + " : " + str(self[i])
        print
