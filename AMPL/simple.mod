# Define variables
var x;
var y;

# Define the objective function
maximize utility: (x + y) - 0.1 * (x + y)^2 - 0.02 * (x - y)^2;

# Constraints
subject to BudgetConstraint: 2 * x + 3 * y <= 10;

# Set initial guess (a good initial guess should be feasible!)
let x := 1;
let y := 1;

solve; 

# output
display x,y;