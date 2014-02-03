from __future__ import division
from coopr import pyomo

# define an abstract life-cycle savings model
model = pyomo.AbstractModel()

##### Define model parameters #####

# define time horizon
model.T = pyomo.Param(doc="Agent's time horizon", within=pyomo.NonNegativeIntegers)
model.periods = pyomo.RangeSet(0, model.T)

# retirement age
model.R = pyomo.Param(doc="Agent's retirement age", within=pyomo.NonNegativeIntegers)

# define prices
model.r = pyomo.Param(doc='Net interest rate', within=pyomo.NonNegativeReals)

def wage_schedule(model, t):
    """Defines the path of wages. This should really go in the .dat file"""
    if t < model.R:
        wage = t / model.R
    else:
        wage = (model.T - t) / (model.T - model.R)
    return wage

model.w = pyomo.Param(model.periods, doc='Real wages', within=pyomo.NonNegativeReals,
                      initialize=wage_schedule)

# define utilty parameters
model.beta = pyomo.Param(doc='Discount factor', within=pyomo.NonNegativeReals)
model.theta = pyomo.Param(doc='Inverse of inter-temporal elasticity of substitution for consumption',
                          within=pyomo.NonNegativeReals)
model.eta = pyomo.Param(doc='Inverse of inter-temporal elasticity of substitution for labor',
                        within=pyomo.NonNegativeReals)

# define borrowing constraint
model.minimum_assets = pyomo.Param(doc='Lower boundon agent assets.')

##### Define model variables #####

# declare consumption variable
def initial_consumption(model, t):
    """Rule for initial choice of consumption."""
    return 0.5

model.consumption = pyomo.Var(model.periods, domain=pyomo.PositiveReals, 
                              initialize=initial_consumption)

# declare labor supply variable
def initial_labor_supply(model, t):
    """Rule for initial choice of labor supply."""
    return 1.0

model.labor_supply = pyomo.Var(model.periods, domain=pyomo.PositiveReals, 
                               initialize=initial_labor_supply)

# declare assets variable
def initial_assets(model, t):
    """Rule for initializing assets."""
    # extract variables
    c = model.consumption
    l = model.labor_supply
    A = model.assets
    
    # extract parameters
    r = model.r
    w = model.w
    
    #if t == 0:
    #    assets = 0.0
    #else:
    #    assets = w[t] * l[t] + (1 + r) * A[t] - c[t]
    
    return 0.0

model.assets = pyomo.Var(pyomo.RangeSet(0, model.T + 1), initialize=initial_assets)

##### define the objective function #####

def flow_utility(model, c, l):
    """Flow utility function for the agent."""    
    # agent likes to eat...
    utility_consumption = c**(1 - model.theta) / (1 - model.theta)
        
    # ...but hates working
    disutility_labor = -l**(1 + model.eta) / (1 + model.eta)
    
    total_utility = utility_consumption + disutility_labor
    
    return total_utility

def lifetime_utility(model):
    """Abstract representation of our model objective.""" 
    # extract variables
    c = model.consumption
    l = model.labor_supply
        
    # compute utility
    U = sum(model.beta**t * flow_utility(model, c[t], l[t]) for t in model.periods)
    
    return U 

model.lifetime_utility = pyomo.Objective(rule=lifetime_utility, sense=pyomo.maximize)

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
    
model.budget_constraints = pyomo.Constraint(model.periods, rule=flow_budget_constraints)

def borrowing_constraint(model, t):
    """Agent's assets cannot fall below some minimum amount."""
    return model.assets[t] >= model.minimum_assets

model.borrowing_constraint = pyomo.Constraint(model.periods, rule=borrowing_constraint)

def endowment(model):
    """Agent has some initial assets."""
    return model.assets[0] == 0.0

model.endowment = pyomo.Constraint(rule=endowment)

def no_bequests(model):
    """Agent leaves no bequests."""
    return model.assets[model.T + 1] == 0.0

model.no_bequests = pyomo.Constraint(rule=no_bequests)