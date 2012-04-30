#These exceptions will probably be replaced by flags at some point.
class StackOverflowError(Exception):
    pass
class StackUnderflowError(Exception):
    pass

class Cell(object):
    """Cell Class for Forth VM
        
       - cells are memory sub-units, (a.k.a. words)
       - these cells are initiated with a specified size in bits
       - the cell stores a value as a signed integer and uses
         2's complement to determine how it overflows
       - if the value is too big for the number of bits, will overflow
         by looping round, currently without throwing an exception
       - write(int) can take any integer and will deal with overflows if
         they happen"""
    
    def __init__(self,bit_count):
        self.bits = bit_count
        self._val = 0
        self._max_val = pow(2,self.bits-1) - 1
        self._overflow_offset = pow(2,self.bits)

    def write(self,integer):
        while integer > self._max_val:
            integer -= self._overflow_offset
        self._val = integer

    def read(self):
        return self._val

class Stack(object):
    """Stack of Cells

        - depth and cell size are specified at initialisation
        - stack pointer (SP) is -1 for an empty stack, 0 for a stack depth
          of 1 etc. and grows up the stack-depth limit max_depth
        - pushes increment SP and then store a value in the
          new top of stack (TOS)
        - pops read out the value at SP and then decrement SP
        - a few convenience functions allow clearing the stack and displaying
          its contents but these are just for in-Python debugging"""
    
    def __init__(self,max_depth,cell_size):
        self.cells = []
        self.SP = -1
        for c in range(max_depth):
            self.cells.append(Cell(cell_size))
            
    def push(self, integer):
        if self.SP > len(self.cells):
            raise StackOverflowError
        else:
            self.SP += 1
            self.cells[self.SP].write(integer)
            
    def pop(self):
        if self.SP < 0:
            raise StackUnderflowError
        else:
            val = self.cells[self.SP].read()
            self.cells[self.SP].write(0)
            self.SP -= 1
            return val
        
    def _flush(self):
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
        
class AddressableMemory(object):
    """This is a list of cells.

       Currently only list-style access and assignment are implemented.
       Indices are equivalent to addresses.

       See http://docs.python.org/reference/datamodel.html for more
       information on what perhaps ought to be implemented."""
    
    def __init__(self,max_cells,cell_size):
        self.cells = []
        for c in range(max_cells):
            self.cells.append(Cell(cell_size))

    def __setitem__(self,addr,val):
        self.cells[addr].write(val)

    def __getitem__(self,addr):
        return self.cells[addr].read()

    def _dump(self,start_addr,cell_count):
        print
        for i in range(start_addr,start_addr + cell_count):
            print str(i) + " : " + str(self[i])
        print

class HexDict(dict):
    """Overrides dict key formatting for instruction set.

        - supply a 32-bit hex key like: 0xDEADBEEF
        - converts string to integer: 3735928559
        - can supply op-code as hex string but store integer in memory cell"""
    
    def __setitem__(self, key, val):
        key = int(key,0)
        dict.__setitem__(self, key, val)

class VirtualMachine(object):
    def __init__(self):
        #Parameters to define VM
        self.bits_per_cell = 32
        self.stack_depth = 10
        self.memory_size = 150

        #Pseudo-registers
        self.tib_offset = 50
        self.program_offset = 100
        self.program_counter = 100
    
        self.instr = HexDict()

        #Initialise stacks and memory
        self.data_stack = Stack(self.stack_depth,self.bits_per_cell)
        self.return_stack = Stack(self.stack_depth,self.bits_per_cell)
        self.memory = AddressableMemory(self.memory_size,
                         self.bits_per_cell)
        
    def start(self):
        self._setup_instruction_set()
        self._init_dictionary()
        self._setup_tib()
        self._enter_execution()

    def _setup_instruction_set(self):
        ds = self.data_stack
        rs = self.return_stack
        mem = self.memory
        instr = self.instr
        pc = self.program_counter
        
        #Memory Instructions
        instr["0x01"] = [lambda: ds.push(mem[ds.pop()]),"DS_FETCH"]             
        instr["0x02"] = [lambda: mem.__setitem__(ds.pop(),ds.pop()),"DS_STORE"]            
        instr["0x11"] = [lambda: rs.push(mem[rs.pop()]),"RS_FETCH"]
        instr["0x12"] = [lambda: mem.__setitem__(rs.pop(),rs.pop()),"RS_STORE"]
        
        #Arithmetic Instructions
        instr["0x03"] = [lambda: ds.push(ds.pop() + ds.pop()),"DS_ADD"]
        instr["0x04"] = [lambda: ds.push(ds.pop() - ds.pop()),"DS_SUB"]
        instr["0x05"] = [lambda: ds.push(ds.pop() * ds.pop()),"DS_MUL"]
        instr["0x06"] = [lambda: ds.push(int(pow(ds.pop(),-1) *
                                             ds.pop())),"DS_DIV"]

        #Execution Instructions
        instr["0x07"] = [lambda: self.pc.__add__(1),"SKIP"]
        
    def _init_dictionary(self):
        pass

    def _setup_tib(self):
        pass

    def _enter_execution(self):
        while 1:
            if self.memory[self.program_counter] in self.instr:
                self.instr[self.memory[self.program_counter]][0]()
                self.program_counter += 1
            else:
                print "\n\n\tINSTRUCTION NOT FOUND\n\n"
                break
            if self.program_counter > self.memory_size:
                print "\n\n\tEND OF PROGRAM\n\n"
                break
