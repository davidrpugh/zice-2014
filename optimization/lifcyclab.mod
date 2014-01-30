# Filename: LifeCycleLabor.mod
# This program solves the life cycle problem of optimal consumption and saving with 
# labor income along the life.
#
# The life cycle problem:
# The utility for period t is util[t] = u(c[t])+v(L[t]), where c[t] is the consumption, 
# L[t] is the labor supply, u is the utility function for consumption, v is the utility 
# function for labor supply.
# If the saving at time t is S[t], then we have the budget constraints:
#    S[t+1] = (1+r)*S[t] + L[t+1]*w[t+1] - c[t+1]
# where w[t] is the wage.
# We do not allow negative consumption of any good. Furthermore, to avoid evaluating functions 
# like the log at 0, we impose a strict positivity condition:
# c[t]>=eps
# for some small positive number eps.
#
# Thus the life cycle problem is 
# maximize sum {t in 1..T} beta^t*(u(c[t])+v(L[t]));
# subject to  S[t+1] = (1+r)*S[t] + L[t+1]*w[t+1] - c[t+1]; c>=eps; L>=0.0; S>=Smin; 


# parameters
param T integer;      # Number of time periods
param R integer;      # Retirement time
param beta;           # discount factor
param r;              # interest rate
param Smin;           # lower bound of savings
param gamma := 2;     # risk-aversion coefficient for consumption
param eta := 1;       # risk-aversion coefficient for labor supply
param S0 := 0;        # initial savings
param ST := 0;        # final savings
param w{1..T};        # wages
param eps := 1e-3;    # lower bound of consumption

# choice for discount factor
let beta := 0.95;

# choice for number of time periods
let T := 60;

# choice for lower bound of savings
let Smin := -10;

# different choices for setting up the interest rate
let r := 0.08;

# scale for the objective function
param scale := 1;

# wages

# R is the peak period for wages, and wages rise linearly until R and then fall linearly.
let R := (T*4) div 5;
let {t in 1..(R-1)} w[t] := t/R;    
let {t in R..T} w[t] := (T-t)/(T-R);    


# variables


# savings
var S{1..(T-1)} >= Smin;

# consumption 

var c{1..T} >= eps;

# labor supply

var L{1..T} >= 0;

# utility function


var util{t in 1..T} = c[t]^(1-gamma)/(1-gamma)-L[t]^(1+eta)/(1+eta);

# model: objective function and constraints


maximize Total_utility: scale * sum {t in 1..T} beta^t*util[t];


subject to budget0: S[1] = (1+r)*S0 + L[1]*w[1] - c[1];
subject to budget {t in 1..(T-2)}: S[t+1] = (1+r)*S[t] + L[t+1]*w[t+1] - c[t+1];
subject to budgetT: ST = (1+r)*S[T-1] + L[T]*w[T] - c[T];

# options for KNITRO
# algorithm/optimizer used: 

# 0: automatic algorithm selection

# 1: Interior/Direct algorithm

# 2: Interior/CG algorithm

# 3: Active algorithm option knitro_options $knitro_options ' alg=0';    



# feasibility termination tolerance (relative)
option knitro_options $knitro_options ' feastol=1.0e-10'; 


# optimality termination tolerance (relative) 
option knitro_options $knitro_options ' opttol=1.0e-10';  


# maximum number of major iterations  
option knitro_options $knitro_options ' maxit=10000'; 


# printing output level: 
# 0: no printing 
# 1: print summary information
# 2: print information every 10 major iterations

# 3: print information at each major iteration

# 4: print information at each major and minor iteration

# 5: also print final (primal) variables

# 6: also print final constraint values and Lagrange multipliers
option knitro_options $knitro_options ' outlev=0';



# initial guess
let {t in 1..T} L[t] := 1;
let {t in 1..(T-1)} c[t] := 0.5;
let S[1] := (1+r)*S0 + L[1]*w[1] - c[1];
let {t in 1..(T-2)} S[t+1] := (1+r)*S[t] + L[t+1]*w[t+1] - c[t+1];
let c[T] := (1+r)*S[T-1] + L[T]*w[T] - ST;

solve;

# display parameters
display beta,T,R,Smin,r;

# display solutions
display w, c, L, S;
#> lifcyclab.out;
#close lifcyclab.out;