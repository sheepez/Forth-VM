import virtual_machine2 as v_m2

testing_internals = False

if testing_internals:
    #Cell tests
    c1 = v_m2.Cell(32)
    c1.write(12456)
    print c1.read()

    #Stack tests
    s1 = v_m2.Stack(10,32)
    print s1
    for i in range(5):
        s1.push(i+3)
    print s1
    for i in range(3):
        print s1.pop()
    print s1

    #Memory Tests
    m1 = v_m2.AddressableMemory(10,32)
    m1._dump(0,5)
    m1[0] = 123
    m1[4] = 123123
    m1._dump(0,5)

    del c1
    del s1
    del m1

# Actual VM tests

vm1 = v_m2.VirtualMachine()

#Manually load some numbers into the stack and a two instruction program
vm1.data_stack.push(1)
vm1.data_stack.push(123)
vm1.data_stack.push(127)
vm1.data_stack.push(1)
vm1.data_stack.push(2)
vm1.memory[vm1.program_counter] = int("0x03",0)
vm1.memory[vm1.program_counter + 1] = int("0x05",0)
vm1.memory[vm1.program_counter + 2] = int("0x05",0)
vm1.memory[vm1.program_counter + 3] = int("0x05",0)
vm1.memory._dump(100,10)

print vm1.data_stack
vm1.start()
print vm1.data_stack
