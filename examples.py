from textwrap import dedent

example_01 = {
    'source': dedent("""
        def demo():
            total = 0
            for i in range(10):
                result = calc_something(i, 5)
                aview('Counter ', i, ' result= ', total)
                total += result
            aview('Final total was: ', total)
            
        def calc_something(a,b):
            # adds two numbers then squares them
            return (a + b)**2
    """).strip(),
    'title': 'Demo 1',
    'description': dedent("""
        This example shows off for loops, variable assignments and function calls incl. the passing of parameters. 
        
        I'm especially proud of the text functionality I just implemented, which takes long strings and breaks them up for 
        you, making it easier to create messages in the alpha register.  
        
        It also allows you to build up message strings by referring to variable names mixed in with descriptive text.  e.g. <pre>aview('Counter ', i, ' result= ', total)</pre> Time saver!
    """).strip(),
    'public': 'y',
}

