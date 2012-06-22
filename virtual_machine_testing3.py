import virtual_machine3 as v_m

testing_internals = False

if testing_internals:
    #Cell tests
    c1 = v_m.Cell(32)
    c1.write(12456)
    print c1.read()

    #Stack tests
    s1 = v_m.Stack(10,32)
    print s1
    for i in range(5):
        s1.push(i+3)
    print s1
    for i in range(3):
        print s1.pop()
    print s1

    #Memory Tests
    m1 = v_m.AddressableMemory(10,32)
    m1._dump(0,5)
    m1[0] = 123
    m1[4] = 123123
    m1._dump(0,5)

    del c1
    del s1
    del m1

# Actual VM tests

vm1 = v_m.VirtualMachine() #Use default arguments

def load_program():
    with open("test1.fasm") as fasm:
        for line in fasm:
            #Lookup the dictionary key given the value
            try:
                code = [code for code, instr in vm1.instr.iteritems()
                    if instr.func_name == line.strip()][0]
            #If the instruction is not found interpret it as a literal
            except IndexError:
                    code = int(line)
            vm1.memory[vm1.program_counter] = int(code)
            vm1.program_counter += 1
        vm1.program_counter = vm1.program_offset
            
load_program()

vm1.memory._dump(100,50)
print vm1.data_stack
vm1.start()
print vm1.data_stack
