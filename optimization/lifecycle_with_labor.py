from __future__ import division
from coopr import pyomo

# define an abstract life-cycle savings model
model = pyomo.AbstractModel()

##### Define model parameters #####

# time horizon
model.T = pyomo.Param(doc="time horizon", within=pyomo.NonNegativeIntegers)
model.periods = pyomo.RangeSet(0, model.T)

# retirement age
model.R = pyomo.Param(doc="retirement age", within=pyomo.NonNegativeIntegers)

# net interest rate
model.r = pyomo.Param(doc='interest rate', within=pyomo.NonNegativeReals)

# wages
def wage_schedule(model, t):
    """Defines the path of wages. This should really go in the .dat file!"""
    if t < model.R:
        wage = t / model.R
    else:
        wage = 0.0
    return wage

model.w = pyomo.Param(model.periods, doc='real wages', within=pyomo.NonNegativeReals,
                      initialize=wage_schedule)

# define utilty parameters
model.beta = pyomo.Param(doc='discount factor', within=pyomo.NonNegativeReals)
model.theta = pyomo.Param(doc='inverse of elasticity of substitution for consumption',
                          within=pyomo.NonNegativeReals)
model.eta = pyomo.Param(doc='Frisch elasticity of substitution for labor',
                        within=pyomo.NonNegativeReals)

# define borrowing constraint
model.minimum_assets = pyomo.Param(doc='lower bound on assets.')

##### Define model variables #####

# declare consumption variable
def initial_consumption(model, t):
    """Rule for initial choice of consumption."""
    return 0.5
    
model.consumption = pyomo.Var(model.periods, 
                              name='consumption', 
                              doc="agent's consumption choice is a flow variable!", 
                              domain=pyomo.PositiveReals, 
                              initialize=initial_consumption)

# declare labor supply variable
def initial_labor_supply(model, t):
    """Rule for initial choice of labor supply."""
    return 1.0
    
model.labor_supply = pyomo.Var(model.periods, 
                               name='labor supply', 
                               doc="agent's labor supply choice is a flow variable!", 
                               domain=pyomo.PositiveReals, 
                               initialize=initial_labor_supply)

# declare assets variable
def initial_assets(model, t):
    """
    Rule for initializing assets. Ideally this should be feasible given 
    rules for initializing consumption variable.
    
    """
    # extract variables
    c = model.consumption
    A = model.assets
    l = model.labor_supply
    
    # extract parameters
    w = model.w
    r = model.r
    
    if t == 0:
        assets = 0.0
    else:
        assets = w[t-1] * l[t-1] + (1 + r) * A[t-1] - c[t-1]
        
    return assets

model.assets = pyomo.Var(pyomo.RangeSet(0, model.T+1), 
                         name='assets', 
                         doc='agent assets are a stock variable!',
                         initialize=initial_assets)

##### define the objective function #####

def flow_utility(model, c, l):
    """Flow utility function for the agent."""    
    # extract parameters
    theta = model.theta
    eta = model.eta
    
    # agent likes to eat...
    utility_consumption = c**(1 - theta) / (1 - theta)
    
    # ...but doesn't like to work!
    disutility_labor = l**(1 + eta) / (1 + eta)
    
    total_utility = utility_consumption - disutility_labor
    
    return total_utility

def lifetime_utility(model):
    """Abstract representation of our model objective.""" 
    # extract variables
    c = model.consumption
    l = model.labor_supply
    
    # extract parameters
    beta = model.beta
    T = model.periods
    
    # compute utility
    U = sum(beta**t * flow_utility(model, c[t], l[t]) for t in T)
    
    return U 

model.lifetime_utility = pyomo.Objective(rule=lifetime_utility, 
                                         sense=pyomo.maximize)

##### Define the model constraints #####

def flow_budget_constraints(model, t):
    """Agent faces a sequence of flow budget constraints"""
    # extract variables
    c = model.consumption
    l = model.labor_supply
    A = model.assets
    
    # extract parameters
    r = model.r
    w = model.w
    
    return c[t] + A[t+1] == w[t] * l[t] + (1 + r) * A[t]
    
model.budget_constraints = pyomo.Constraint(model.periods, 
                                            rule=flow_budget_constraints,
                                            doc='Agent faces a sequence of flow budget constraints.')

def borrowing_constraint(model, t):
    """Agent's assets cannot fall below some minimum amount."""
    return model.assets[t] >= model.minimum_assets

model.borrowing_constraint = pyomo.Constraint(model.periods, 
                                              rule=borrowing_constraint,
                                              doc='There is a lower bound on agent assets.')

def endowment(model):
    """Agent has some initial assets."""
    return model.assets[0] == 0.0

model.endowment = pyomo.Constraint(rule=endowment, 
                                   doc='Agent has some initial endowment.')

def no_bequests(model):
    """Agent leaves no bequests."""
    return model.assets[model.T+1] == 0.0

model.no_bequests = pyomo.Constraint(rule=no_bequests,
                                     doc='Agent makes no bequests.')