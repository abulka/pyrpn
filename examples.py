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
        <p>This example shows off for loops, variable assignments and function calls 
        incl. the passing of parameters.</p> 
        
        <p>I'm especially proud of the text functionality I just implemented, which 
        takes long strings and <b>breaks them up for 
        you</b>, making it easier to create messages in the alpha register.</p>  
        
        <p>It also allows you to build up message strings by <b>referring to variable names</b>
         mixed in with descriptive text.
          e.g. <pre>aview('Counter ', i, ' result= ', total)</pre> Time saver!</p>
    """).strip(),
    'public': 'y',
    'fingerprint': '00101demo1234',
}

