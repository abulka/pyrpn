def demo():
    total = 0
    for i in range(10):
        result = calc_something(i, 5)
        print('Counter', i, 'result=', total)
        total += result
    print('Final total was:', total)

def calc_something(a,b):
    # adds two numbers then squares them
    return (a + b)**2
