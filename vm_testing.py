# Some VM tests

from virtual_memory import *

c1 = cell(32)

c1.write(12456)
print c1.read()

s1 = stack(10,32)

print repr(s1)
print s1

for i in range(1,5):
    s1.push(i)

print s1

for i in range(1,3):
    print s1.pop()

print s1

m1 = memory(10,32)

m1._dump(0,5)

m1[0] = 123
m1[4] = 123123

m1._dump(0,5)
