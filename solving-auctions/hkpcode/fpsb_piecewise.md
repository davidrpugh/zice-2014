# © Timothy P. Hubbard
# timothy.hubbard@colby.edu

# model file to approximate bid functions at a FPSB auction 
# with Chebyshev polynomials

# this file is for the case in which bidders draw valuations 
# from a uniform distribution or a piecewise distribution

# note:
# player 1 has the uniform distribution
# player 2 has the piecewise distribution

# parameters of model
param d > 0, integer;               # degree of Chebyshev polynomials
param p > 0, integer;               # number of players
param npts > 0, integer;            # number of points in bid grid space (for residuals)
param nconpts > 0, integer;         # number of points in constraints (for shape constraints)
param pi > 3.14;                    # approximate value for pi
param vlow >= 0;                    # lower bound on valuation support
param vhigh >= vlow;                # upper bound on valuation support
param nparts > 0, integer;          # number of piecewise intervals
param breaks {1..(nparts+1)};       # piecewise distribution breaks
param coefs {1..nparts,1..4};       # piecewise distribution coefficients

# degree of each piecewise polynomial
param pd := 3;

# unknowns: the polynomial coefficients and the highest bid
var a {0..d,1..p};
var bhigh >= vlow, <= vhigh, := (vhigh + vlow)/2;

# find Chebyshev nodes
param z {i in 1..npts} :=
    -cos((2*i - 1)/(2*npts)*pi);
# adjust these to [vlow,bhigh]
var b {i in 1..npts} =
    (z[i] + 1)*(bhigh - vlow)/2 + vlow;
# uniform grid from [vlow,bhigh] for points used in shape constraints
param zcon {i in 1..nconpts} :=
    (i - 1)/nconpts - 1;
# adjust these to [vlow,bhigh]
var bcon {i in 1..nconpts} =
    (zcon[i] + 1)*(bhigh - vlow)/2 + vlow;

# evaluate first d degrees of Chebyshev polynomials at each point
var T {k in 0..d, i in 1..npts} =
    if k = 0
        then 1
    else if k = 1
        then z[i]
    else 
        2*z[i]*T[k-1,i] - T[k-2,i];
# evaluate first d degrees of derivative of Chebyshev polynomials at each point
var dT {k in 0..d, i in 1..npts} =
    if k = 0
        then 0
    else if k = 1
        then 1
    else
        2*T[k-1,i] + 2*z[i]*dT[k-1,i] - dT[k-2,i];
param Tcon {k in 0..d, i in 1..nconpts} :=
        if k = 0
        then 1
    else if k = 1
        then zcon[i]
    else 
        2*zcon[i]*Tcon[k-1,i] - Tcon[k-2,i];
        
# inverse bid function and derivative of ibf at each "bid"
var ibf {i in 1..npts,j in 1..p} =
    sum {k in 0..d} a[k,j]*T[k,i];
var dibf {i in 1..npts,j in 1..p} =
    2/(bhigh - vlow)*sum {k in 0..d} a[k,j]*dT[k,i];
var ibfcon {i in 1..nconpts,j in 1..p} =
    sum {k in 0..d} a[k,j]*Tcon[k,i];
    
# each piecewise polynomial evaluated at each ibf for player 2
var piececdf {i in 1..npts,k in 1..nparts} =
    sum {h in 0..pd} coefs[k,h+1]*(ibf[i,2] - breaks[k])^(pd - h);
var piecepdf {i in 1..npts,k in 1..nparts} =
    sum {h in 0..pd} (pd - h)*coefs[k,h+1]*(ibf[i,2] - breaks[k])^(pd - h - 1);
    
# cdf of players
var cdf {i in 1..npts,j in 1..p} =
    if j = 1 then ibf[i,j]
    else if (breaks[1] <= ibf[i,j] <= breaks[2])
            then piececdf[i,1]
    else if (breaks[2] <= ibf[i,j] <= breaks[3])
            then piececdf[i,2]
    else if (breaks[3] <= ibf[i,j] <= breaks[4])
            then piececdf[i,3]
    else if (breaks[4] <= ibf[i,j] <= breaks[5])
            then piececdf[i,4]
    else if (breaks[5] <= ibf[i,j] <= breaks[6])
            then piececdf[i,5]
    else if (breaks[6] <= ibf[i,j] <= breaks[7])
            then piececdf[i,6];
# pdf of players
var pdf {i in 1..npts,j in 1..p} =
    if j = 1 then 1
    else if (breaks[1] <= ibf[i,j] <= breaks[2])
            then piecepdf[i,1]
    else if (breaks[2] <= ibf[i,j] <= breaks[3])
            then piecepdf[i,2]
    else if (breaks[3] <= ibf[i,j] <= breaks[4])
            then piecepdf[i,3]
    else if (breaks[4] <= ibf[i,j] <= breaks[5])
            then piecepdf[i,4]
    else if (breaks[5] <= ibf[i,j] <= breaks[6])
            then piecepdf[i,5]
    else if (breaks[6] <= ibf[i,j] <= breaks[7])
            then piecepdf[i,6];

# pdf divided by cdf for each player at each bid
var ratio {i in 1..npts,j in 1..p} = 
    pdf[i,j]/cdf[i,j];

# first-order conditions for each player
var FOC {i in 1..npts,j in 1..p} =
    -1 + (ibf[i,j] - b[i])*(-ratio[i,j]*dibf[i,j] + sum {l in 1..p} ratio[i,l]*dibf[i,l]);
    
# polynomial needs to be evaluated at specific points for
# conditions on (inverse) bid functions
param zlow := -1;
param Tlow {i in 0..d} =
    if i = 0
        then 1
    else if i = 1
        then zlow
    else 
        2*zlow*Tlow[i-1] - Tlow[i-2];
param dTlow {k in 0..d} =
    if k = 0
        then 0
    else if k = 1
        then 1
    else
        2*Tlow[k-1] + 2*zlow*dTlow[k-1] - dTlow[k-2];
param zhigh := 1;
param Thigh {i in 0..d} =
    if i = 0
        then 1
    else if i = 1
        then zhigh
    else 
        2*zhigh*Thigh[i-1] - Thigh[i-2];
param dThigh {k in 0..d} =
    if k = 0
        then 0
    else if k = 1
        then 1
    else
        2*Thigh[k-1] + 2*zhigh*dThigh[k-1] - dThigh[k-2];
param pdfhigh {j in 1..p} =
    if j = 1 then 1
    else sum {h in 0..pd} (pd - h)*coefs[nparts,h+1]*(vhigh - breaks[nparts])^(pd - h - 1);
var dibfhigh {j in 1..p} =
    2/(bhigh - vlow)*sum {k in 0..d} a[k,j]*dThigh[k];
var dibflow {j in 1..p} =
    2/(bhigh - vlow)*sum {k in 0..d} a[k,j]*dTlow[k];

        
# minimize FOCs choosing polynomial coefficients
minimize sumofsquares:
    (sum {i in 1..npts,j in 1..p} FOC[i,j]^2)/(p*npts);

# require players to bid vlow if they draw the low valuation
subject to LowCond {j in 1..p}:
    sum {k in 0..d} a[k,j]*Tlow[k] = vlow;
# require players to bid bhigh if they have high valuation
subject to HighCond {j in 1..p}: 
    sum {k in 0..d} a[k,j]*Thigh[k] = vhigh;
# require monotonicity; to make higher bids you need higher valuations
subject to Monotone {i in 2..nconpts,j in 1..p}: 
        ibfcon[i,j] >= ibfcon[i-1,j];
# players must bid less than their valuations
subject to Rational {i in 1..nconpts,j in 1..p}:
        bcon[i] <= ibfcon[i,p];
# impose condition 2a from HKP paper
subject to Cond2a {j in 1..p}:
    -pdfhigh[j]*dibfhigh[j] + sum{l in 1..p} pdfhigh[l]*dibfhigh[l] = 1/(vhigh - bhigh);
# impose condition 2b from HKP paper
subject to Cond2b {j in 1..p}:
    dibflow[j] = p/(p - 1);
