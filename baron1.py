from redbaron import RedBaron
red = RedBaron("some_value = 42")
#print(red.dumps())  # get code back

s1 = """
def do(n):
    x = 100
    y = x + 100
    return y

def do_again(n):
    do()

"""

red = RedBaron(s1)
#print(red.dumps())  # get code back
res = red.find_all('def', recursive=False)
print(res.help())
for r in res:
    print(f'def found: {r.name}')
