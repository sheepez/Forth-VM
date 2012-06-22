#These exceptions will probably be replaced by flags at some point.
class StackOverflowError(Exception):
    pass
class StackUnderflowError(Exception):
    pass

import sys

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
    def __init__(self,bits_per_cell=32,stack_depth=20):
        #Parameters to define VM
        self.bits_per_cell = bits_per_cell
        self.stack_depth = stack_depth
        self.memory_size = 350

        #Pseudo-registers
        self.tib_offset = 50
        self.dictionary_offset = 100
        self.program_offset = 200
        self.program_counter = 200
    
        self.instr = HexDict()

        #Initialise stacks and memory
        self.data_stack = Stack(self.stack_depth,self.bits_per_cell)
        self.return_stack = Stack(self.stack_depth,self.bits_per_cell)
        self.memory = AddressableMemory(self.memory_size,
                         self.bits_per_cell)

        self._setup_instruction_set()
        
    def start(self):
        
        self._init_dictionary()
        self._setup_tib()
        self._enter_execution()

    def _setup_instruction_set(self):
        
        #Alias a few things to make the lambdas a bit easier to read
        ds = self.data_stack
        rs = self.return_stack
        mem = self.memory
        instr = self.instr

        #Current instructions use the methods provided by Stack
        #and AddressableMemory. A better model might be to use
        #a virtual ALU that can access the top few stack items as
        #this is closer the conceptual harware implementation.

        def pc_offset(offset):
            self.program_counter += offset

        def NOOP():
            pc_offset(1)
        
        #Memory Instructions
        def DS_FETCH():
            address = ds.pop()
            ds.push(mem[address])
            pc_offset(1)
        def DS_STORE():
            address = ds.pop()
            value = ds.pop()
            mem[address] = value
            pc_offset(1)
        def RS_FETCH():
            address = rs.pop()
            rs.push(mem[address])
            pc_offset(1)
        def RS_STORE():
            address = rs.pop()
            value = rs.pop()
            mem[address] = value
            pc_offset(1)
        #LITERAL interprets the next cell of the program memory
        #as a number and pushes it to the data stack.
        def LITERAL():
            pc_offset(1)
            ds.push(mem[self.program_counter])
            pc_offset(1)
        #Arithmetic Instructions
        def DS_ADD():
            a = ds.pop()
            b = ds.pop()
            ds.push(b+a)
            pc_offset(1)
        def DS_SUB():
            a = ds.pop()
            b = ds.pop()
            ds.push(b-a)
            pc_offset(1)
        def DS_MUL():
            a = ds.pop()
            b = ds.pop()
            ds.push(b*a)
            pc_offset(1)
        def DS_DIV():
            a = ds.pop()
            b = ds.pop()
            ds.push(int(b/a))
            pc_offset(1)
        def DS_EQ():
            a = ds.pop()
            b = ds.pop()
            ds.push(1) if a == b else ds.push(0)
            pc_offset(1)
        def DS_AND():
            pass
        def DS_NOT():
            pass

        
        #Flow Control Instructions
        def IF():
            if ds.pop() == 0:
                while mem[self.program_counter] != int("0x22",0):
                    pc_offset(1)
            else:
                 pc_offset(1)
        def THEN():
            pc_offset(1)
        def JUMP():
            pc_offset(ds.pop())

        #Compile Instructions into a dictionary
        instr["0x00000000"] = NOOP
        instr["0x00000001"] = DS_FETCH
        instr["0x00000002"] = DS_STORE
        instr["0x00000003"] = RS_FETCH
        instr["0x00000004"] = RS_STORE
        instr["0x00000005"] = LITERAL
        instr["0x00000011"] = DS_ADD
        instr["0x00000012"] = DS_SUB
        instr["0x00000013"] = DS_MUL
        instr["0x00000014"] = DS_DIV
        instr["0x00000015"] = DS_EQ
        instr["0x00000021"] = IF
        instr["0x00000022"] = THEN
        instr["0x00000023"] = JUMP
        
    def _init_dictionary(self):
        #Dictionary exists in addressable memory
        #Implemented as a singly-linked list
        #Structure:
        #   1  cell  : word name length
        #   15 cells : word name
        #   1  cell  : address of previous word
        #   1  cell  : address of word's code
        #   n  cells : space for data/code etc
        pass

    def _setup_tib(self):
        pass

    def _enter_execution(self):
        while 1:
            current_instr = self.memory[self.program_counter]
            if current_instr in self.instr:
                self.instr[current_instr]() #Execute instruction             
            else:
                print "\n\n\tINSTRUCTION NOT FOUND"
                print "\t at address: " + str(self.program_counter) + "\n\n"
                break
            if self.program_counter >= self.memory_size:
                print "\n\n\tEND OF PROGRAM\n\n"
                break
