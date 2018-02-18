var = 99
xx = 98

"""
Accessing a global var from inside a function is OK and doesn't need
'global' until that def starts to mess with the value of that var.
As soon as that happens, the previous REFERENCES to var that used to work
no longer work - because Python reckons you are trying to refer to the local
version of that var before you have assigned to it.

In python, assignment in a def, assumes local var, unless 'global' added to make it global and access the outer scope.
In python, assignment in a nested def, assumes local var, unless 'nonlocal' added to make it access the outer scope.

In both cases, simply accessing variables is OK and scopes are travered without any problem or any need for declaration.

Its only on assignment that Python freaks out and by default assumes local - you have to declare to break out.  And you have to put up with 'referenced before assignment' warnings if you refer to a 'local' variable before assigning to it (fair enough when you think about it) - adding the global or nonlocal keyword solves those warnings because you are then referring to something earlier in an outer scope, so its not a problem.
"""

def level1():
    x = 100
    def level2():
        nonlocal x # need this
        print('x', x)  # same error as global situation, referenced before assignment
        x = 200
        print('x', x)
    level2()
    print('level1 x', x)
level1()

exit(0)

def do():
    print(var)
    print(xx)
    var = 234567  # this is local
    print(var)

do()

# def do():
#     print(f'var is {var}')  # FAILS! var referenced before assignment
#     var = 1234567  # this is local
#     print(f'do - var is {var}')
 
# def do2():
#     #global var
#     print(f'do2 - var is {var}')
#     var = 98  # this is now global
#     print(f'do2 - var is {var}')

def do3():
    print(xx)
    print(f'do3 - var is {var}')  # FAILS! var referenced before assignment
    z = 2000
    def inner():
        print(f'do3 - inner - z is {z}') # yes can get to outer scope without global keyword
                                    # which makes sense since its not global, just outer
        print(f'do3 - inner - var is {var}') # FAILS
    
    def inner2():
        print(f'inner2 - var is {var}') # yes can get to outer scope without global keyword
                                    # outer scope has already declared global, so we borrow that

    inner()
    inner2()

#do()
#print(f'GS var is {var}')

#do2()
#print(f'GS var is {var}')

do3()
print(f'GS var is {var}')
