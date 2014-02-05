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
model.w0 = pyomo.Param(doc='initial real wage', within=pyomo.NonNegativeReals)
model.g = pyomo.Param(doc='growth rate of real wages', within=pyomo.NonNegativeReals)

def wage_schedule(model, t):
    """Defines the path of wages. This should really go in the .dat file!"""
    # extract parameters
    w0 = model.w0
    g = model.g
    
    if t < model.R:
        wage = (1 + g)**t * w0
    else:
        wage = 0.0
    return wage

model.w = pyomo.Param(model.periods, doc='real wages', within=pyomo.NonNegativeReals,
                      initialize=wage_schedule)

# labor endowment
model.l_bar = pyomo.Param(doc='labor endowment', within=pyomo.NonNegativeReals)

# depreciation factor for physical capital
model.delta = pyomo.Param(doc='depreciation factor', within=pyomo.NonNegativeReals)

# define utilty parameters
model.beta = pyomo.Param(doc='discount factor', within=pyomo.NonNegativeReals)
model.sigma = pyomo.Param(doc='inverse of elasticity of substitution for consumption',
                          within=pyomo.NonNegativeReals)

# define borrowing constraint
model.minimum_capital = pyomo.Param(doc='lower bound on capital holdings.')

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

# declare investment variable
def initial_investment(model, t):
    """Rule for initial choice of consumption."""
    return 0.5
    
model.investment = pyomo.Var(model.periods, 
                             name='investment', 
                             doc="agent's investment choice is a flow variable!", 
                             domain=pyomo.Reals, 
                             initialize=initial_investment)

# declare capital variable
def initial_capital(model, t):
    """
    Rule for initializing assets. Ideally this should be feasible given 
    rules for initializing consumption variable.
    
    """
    # extract variables
    i = model.investment
    k = model.capital
    
    # extract parameters
    delta = model.delta
    
    if t == 0:
        capital = 0.0
    else:
        capital = (1 - delta) * k[t-1] + i[t-1]
        
    return capital

model.capital = pyomo.Var(pyomo.RangeSet(0, model.T+1), 
                          name='capital', 
                          doc='agent capital holdings are a stock variable!',
                          initialize=initial_capital)

##### define the objective function #####

def flow_utility(model, c):
    """Flow utility function for the agent."""    
    # extract parameters
    sigma = model.sigma
    
    # agent likes to eat...
    utility_consumption = c**(1 - sigma) / (1 - sigma)
            
    return utility_consumption

def lifetime_utility(model):
    """Abstract representation of our model objective.""" 
    # extract variables
    c = model.consumption
    
    # extract parameters
    beta = model.beta
    T = model.periods
    
    # compute utility
    U = sum(beta**t * flow_utility(model, c[t]) for t in T)
    
    return U 

model.lifetime_utility = pyomo.Objective(rule=lifetime_utility, 
                                         sense=pyomo.maximize)

##### Define the model constraints #####

def flow_budget_constraints(model, t):
    """Agent faces a sequence of flow budget constraints"""
    # extract variables
    k = model.capital
    c = model.consumption
    i = model.investment
    
    # extract parameters
    r = model.r
    w = model.w
    l_bar = model.l_bar
    
    return c[t] + i[t] == w[t] * l_bar + r * k[t]
    
model.budget_constraints = pyomo.Constraint(model.periods, 
                                            rule=flow_budget_constraints,
                                            doc='Agent faces a sequence of flow budget constraints.')

def capital_evolution_rule(model, t):
    """Agent's capital stock evolves depending on current capital stock and investment rate."""
    # extract variables
    k = model.capital
    i = model.investment
    
    # extract parameters
    delta = model.delta
    
    return k[t+1] == (1 - delta) * k[t] + i[t]
    
model.capital_evolution = pyomo.Constraint(model.periods, 
                                           rule=capital_evolution_rule,
                                           doc='Equation of motion for capital stock.')

def borrowing_constraint(model, t):
    """Agent's capital cannot fall below some minimum amount."""
    return model.capital[t] >= model.minimum_capital

model.borrowing_constraint = pyomo.Constraint(model.periods, 
                                              rule=borrowing_constraint,
                                              doc='There is a lower bound on agent capital.')

def endowment(model):
    """Agent has some initial capital."""
    return model.capital[0] == 0.0

model.endowment = pyomo.Constraint(rule=endowment, 
                                   doc='Agent has some initial endowment.')

def no_bequests(model):
    """Agent leaves no bequests."""
    return model.capital[model.T+1] == 0.0

model.no_bequests = pyomo.Constraint(rule=no_bequests,
                                     doc='Agent makes no bequests.')