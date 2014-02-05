from __future__ import division
from coopr import pyomo

# define an abstract life-cycle savings model
model = pyomo.AbstractModel()

##### Define model parameters #####

# time horizon
model.T = pyomo.Param(doc="time horizon", 
                      within=pyomo.NonNegativeIntegers)
model.periods = pyomo.RangeSet(0, model.T)

# retirement age
model.R = pyomo.Param(doc="retirement age", 
                      within=pyomo.NonNegativeIntegers)

# net interest rate
model.r = pyomo.Param(doc='interest rate', 
                      within=pyomo.NonNegativeReals)

# wages
model.w0 = pyomo.Param(doc='initial real wage', 
                       within=pyomo.NonNegativeReals)
model.g = pyomo.Param(doc='growth rate of real wages', 
                      within=pyomo.NonNegativeReals)

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

model.w = pyomo.Param(model.periods, doc='real wages', 
                      within=pyomo.NonNegativeReals,
                      initialize=wage_schedule)

# labor endowment
model.l_bar = pyomo.Param(doc='labor endowment', 
                          within=pyomo.NonNegativeReals)

# capital endowment
model.initial_capital = pyomo.Param(doc='capital endowment',
                                    within=pyomo.NonNegativeReals)

# asset prices
def asset_price(model, t):
    """Defines the path of asset prices"""
    return 0.25

model.q = pyomo.Param(pyomo.RangeSet(0, model.T+1), 
                      doc='asset price', 
                      within=pyomo.NonNegativeReals,
                      initialize=asset_price)

model.theta = pyomo.Param(doc='fraction of discounted value of capital that can be collateralized', 
                          within=pyomo.NonNegativeReals)

# define utilty parameters
model.beta = pyomo.Param(doc='discount factor', 
                         within=pyomo.NonNegativeReals)
model.sigma = pyomo.Param(doc='inverse of elasticity of substitution for consumption',
                          within=pyomo.NonNegativeReals)

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

# declare debt variable
def initial_debt(model, t):
    """Rule for initial choice of debt."""
    return 0.0
    
model.debt= pyomo.Var(pyomo.RangeSet(0, model.T+1), 
                      name='borrowing', 
                      doc="agent's debt is a stock variable!", 
                      domain=pyomo.Reals, 
                      initialize=initial_debt)

# declare capital variable
def capital_rule(model, t):
    """
    Rule for initializing assets. Ideally this should be feasible given rules 
    for initializing consumption variable.
    
    """
    # extract variables
    k = model.capital
    b = model.debt
    c = model.consumption
    
    # extract parameters
    w = model.w
    r = model.r
    q = model.q
    l_bar = model.l_bar
    k0 = model.initial_capital
    
    if t == 0:
        capital = k0
    else:
        capital = (1 / q[t-1]) * (w[t-1] * l_bar + (r + q[t-1]) * k[t-1] + b[t] - (1 + r) * b[t-1] - c[t-1])
        
    return capital

model.capital = pyomo.Var(pyomo.RangeSet(0, model.T+1), 
                          name='capital', 
                          doc='agent capital holdings are a stock variable!',
                          domain=pyomo.Reals,
                          initialize=capital_rule)

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
    
    # compute utility
    U = sum(beta**t * flow_utility(model, c[t]) for t in model.periods)
    
    return U 

model.lifetime_utility = pyomo.Objective(rule=lifetime_utility, 
                                         sense=pyomo.maximize)

##### Define the model constraints #####

def flow_budget_constraints(model, t):
    """Agent faces a sequence of flow budget constraints"""
    # extract variables
    k = model.capital
    c = model.consumption
    b = model.debt
    
    # extract parameters
    r = model.r
    w = model.w
    q = model.q
    l_bar = model.l_bar
    
    return c[t] + q[t] * k[t+1] + (1 + r) * b[t] == w[t] * l_bar + (r + q[t]) * k[t] + b[t+1]
    
model.budget_constraints = pyomo.Constraint(model.periods, 
                                            rule=flow_budget_constraints,
                                            doc='Agent faces a sequence of flow budget constraints.')

def borrowing_constraint(model, t):
    """Agent's borrowing capacity depends on collateral."""
    # extract variables
    k = model.capital
    b = model.debt
    
    # extract parameters
    theta = model.theta
    r = model.r
    q = model.q
    
    return  (1 + r) * b[t] <= theta * q[t+1] * k[t] 

model.borrowing_constraint = pyomo.Constraint(model.periods, 
                                              rule=borrowing_constraint,
                                              doc='Endogenous borrowing constraint.')

def capital_endowment_rule(model):
    """Agent has some initial capital endowment."""
    return model.capital[0] == model.initial_capital

model.capital_endowment = pyomo.Constraint(rule=capital_endowment_rule, 
                                           doc='Agent has some initial endowment.')

def no_bequests(model):
    """Agent leaves no bequests."""
    T = model.T
    return model.capital[T+1] == 0.0

model.no_bequests = pyomo.Constraint(rule=no_bequests,
                                     doc='Agent makes no bequests.')