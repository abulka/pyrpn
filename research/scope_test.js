let v = 99
let z = 98

/*
So in node, the default is that you ARE accessing global scope if local var not found.
For assignment as well as access 
In python this is only true for access.

In python assignment assumes local var, unless 'global' added to make it global.
In node assignment assumes global, unless 'let' is added to make it local.
*/

function do1() {
    console.log(v)
    v = 1234  // aha this does access the global scope, no 'global' declaration needed
    let z = 555  // the 'let' makes 'z' local
    console.log(v)
}

do1()

console.log('global', v)
console.log('global', z)
