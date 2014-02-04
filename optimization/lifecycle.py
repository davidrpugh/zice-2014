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
    """Defines the path of wages. This should really go in the .dat file?"""
    if t < model.R:
        wage = t / model.R
    else:
        wage = 0.0
    return wage

model.w = pyomo.Param(model.periods, doc='Real wages', within=pyomo.NonNegativeReals,
                      initialize=wage_schedule)

# define utilty parameters
model.beta = pyomo.Param(doc='discount factor', within=pyomo.NonNegativeReals)
model.theta = pyomo.Param(doc='inverse of elasticity of substitution for consumption',
                          within=pyomo.NonNegativeReals)

# define borrowing constraint
model.minimum_assets = pyomo.Param(doc='lower bound on assets.')

##### Define model variables #####

# declare consumption variable
def initial_consumption(model, t):
    """Rule for initial choice of consumption."""
    return 0.5

model.consumption = pyomo.Var(model.periods, domain=pyomo.PositiveReals, 
                              initialize=initial_consumption)

# declare assets variable
def initial_assets(model, t):
    """
    Rule for initializing assets. Ideally this should be feasible given 
    rules for initializing consumption variable.
    
    """          
    return 0.0

model.assets = pyomo.Var(pyomo.RangeSet(0, model.T+1), initialize=initial_assets)

##### define the objective function #####

def flow_utility(model, c):
    """Flow utility function for the agent."""    
    # agent likes to eat...
    utility_consumption = c**(1 - model.theta) / (1 - model.theta)
            
    return utility_consumption

def lifetime_utility(model):
    """Abstract representation of our model objective.""" 
    # extract variables
    c = model.consumption
        
    # compute utility
    U = sum(model.beta**t * flow_utility(model, c[t]) for t in model.periods)
    
    return U 

model.lifetime_utility = pyomo.Objective(rule=lifetime_utility, sense=pyomo.maximize)

##### Define the model constraints #####

def flow_budget_constraints(model, t):
    """Agent faces a sequence of flow budget constraints"""
    # extract variables
    c = model.consumption
    A = model.assets
    
    # extract parameters
    r = model.r
    w = model.w
    
    return c[t] + A[t+1] == w[t] + (1 + r) * A[t]
    
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
    return model.assets[model.T+1] == 0.0

model.no_bequests = pyomo.Constraint(rule=no_bequests)