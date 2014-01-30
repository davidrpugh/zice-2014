##### Declare parameters #####

# Age at death 
param T := 100;

# Age at retirement
param retire := 65;

# discount factor
param beta := 0.95;

# Gross returns on assets 
param R := 1.05;

# real wage
param w{1..T};

let {t in 1..(retire - 1)} w[t] := t / retire;    
let {t in retire..T} w[t] := (T - t) / (T - retire);

# lower bound on consumption
param eps := 1e-3;

# inverse elasticity of substitution for consumption
param gamma := 2.5;   

# inverse elasticity of substitution for labor supply  
param eta := 1.0;       

# initial assets
param A0 := 0.0; 

# terminal assets       
param AT := 0.0;        

# borrowing constraint
param Amin := -10.0;     

# tax on consumption
param tau_c := 0.15;

# tax on labor supply
param tau_l := 0.05;

# tax on capital
param tau_A := -0.5;

##### Declare variables #####

# consumption
var c{1..T} >= eps;

 # labor supply
var l{1..T} >= 0.0; 

# assets
var A{1..(T-1)} >= Amin;

##### Define flow utility #####

# utility function
var util{t in 1..T} = (c[t]^(1-gamma) / (1 - gamma)) - (l[t]^(1 + eta) / (1 + eta));

##### Define the objective function and constraints #####

maximize total_utility: sum {t in 1..T} beta^t * util[t];

subject to budget0: A[1] = ((1 - tau_A) * R + tau_A) * A0 + (1 - tau_l) * l[1] * w[1] - (1 + tau_c) * c[1];
subject to budget {t in 1..(T-2)}: A[t+1] = ((1 - tau_A) * R + tau_A) * A[t] + (1 - tau_l) * l[t+1] * w[t+1] - (1 + tau_c) * c[t+1];
subject to budgetT: AT = ((1 - tau_A) * R + tau_A) * A[T-1] + (1 - tau_l) * l[T] * w[T] - (1 + tau_c) * c[T];

##### Specify an initial guess #####
let {t in 1..T} l[t] := 1;
let {t in 1..(T-1)} c[t] := 0.5;
let A[1] := ((1 - tau_A) * R + tau_A) * A0 + l[1] * w[1] - c[1];
let {t in 1..(T-2)} A[t+1] := ((1 - tau_A) * R + tau_A) * A[t] + l[t+1] * w[t+1] - c[t+1];
let c[T] := ((1 - tau_A) * R + tau_A) * A[T-1] + l[T] * w[T] - AT;

solve;

# display solutions
display w, c, l, A > life_cycle_HW.out;
close life_cycle_HW.out;