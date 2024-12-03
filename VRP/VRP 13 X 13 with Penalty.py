# Import Pyomo library and Solver
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from collections import defaultdict
import pandas as pd

# Model
model = pyo.ConcreteModel()

# Sets

N = 13
V = 4
M = 1000

model.CUSTOMERS = pyo.Set(initialize = ['A' + str(i) for i in range(1, N+1)])
model.cust = pyo.Set(initialize = ['A' + str(i) for i in range(2, N+1)])
model.VEHICLES = pyo.Set(initialize = ['V' + str(i) for i in range(1, V+1)])

# Parameters

# demdata = [[0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 502, 388],
#   [548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480],
#   [776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164],
#   [696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628],
#   [582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514],
#   [274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662],
#   [502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890],
#   [194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354],
#   [308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696],
#   [194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422],
#   [536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764],
#   [502, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 114],
#   [388, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 114, 0]]

demdata = [[0, 548, 776, 696, 582, 274, 502, 194, 308, 194, 536, 522, 408],
 [548, 0, 684, 308, 194, 502, 730, 354, 696, 742, 1084, 594, 480],
 [776, 684, 0, 992, 878, 502, 274, 810, 468, 742, 400, 1278, 1164],
 [696, 308, 992, 0, 114, 650, 878, 502, 844, 890, 1232, 514, 628],
 [582, 194, 878, 114, 0, 536, 764, 388, 730, 776, 1118, 400, 514],
 [274, 502, 502, 650, 536, 0, 228, 308, 194, 240, 582, 776, 662],
 [502, 730, 274, 878, 764, 228, 0, 536, 194, 468, 354, 1004, 890],
 [194, 354, 810, 502, 388, 308, 536, 0, 342, 388, 730, 468, 354],
 [308, 696, 468, 844, 730, 194, 194, 342, 0, 274, 388, 810, 696],
 [194, 742, 742, 890, 776, 240, 468, 388, 274, 0, 342, 536, 422],
 [536, 1084, 400, 1232, 1118, 582, 354, 730, 388, 342, 0, 878, 764],
 [522, 594, 1278, 514, 400, 776, 1004, 468, 810, 536, 878, 0, 134],
 [408, 480, 1164, 628, 514, 662, 890, 354, 696, 422, 764, 134, 0]]

demdatapd = pd.DataFrame(demdata, index = ['A' + str(i) for i in range(1, N+1)], columns = ['A' + str(i) for i in range(1, N+1)])

model.distance = demdatapd

# demand = pd.read_excel("VRP RP1.xlsx", header = 9, usecols = "A:H", nrows = 2)
cust_dem =  [0, 1, 1, 3, 6, 3, 6, 8, 8, 1, 6, 6, 8]
cust_dem_dict = {}
for i in range(len(cust_dem)):
    cust_dem_dict[model.CUSTOMERS[i+1]] = cust_dem[i]
    
model.demand = pyo.Param(model.CUSTOMERS, initialize = cust_dem_dict)
model.capacity = pyo.Param(model.VEHICLES, initialize = {'V1': 15, 'V2': 15, 'V3' : 15, 'V4' : 30})

dist = defaultdict(int)

for V in model.VEHICLES:
    dist[V] = 0

# Variables
model.x = pyo.Var(model.CUSTOMERS, model.CUSTOMERS, model.VEHICLES, within=pyo.Binary)
model.u = pyo.Var(model.cust, within=pyo.NonNegativeReals)
model.pen = pyo.Var(model.CUSTOMERS, within = pyo.Binary)
pen = model.pen

# Objective function
def objective_rule(model):
    return sum(model.distance[j][i]*model.x[i, j, k] if j != i else 0
               for k in model.VEHICLES 
               for j in model.CUSTOMERS
                for i in model.CUSTOMERS) + sum(model.x[i, j, "V4"]*M - 
                model.distance[j][i]*(model.x[i, j, "V4"]) 
                for j in model.CUSTOMERS
                 for i in model.CUSTOMERS if i != j) - M
model.objective = pyo.Objective(rule=objective_rule, sense = pyo.minimize)

# Constraints


# - (sum(pen[i]*model.demand[i] for i in model.cust))

def capacity(model, k):
    return sum(model.x[i, j, k]*model.demand[j] 
               for i in model.CUSTOMERS 
               for j in model.cust if j != i) <= model.capacity[k]
model.capacity_constraint = pyo.Constraint(model.VEHICLES, rule=capacity)

def enter(model, j, k):
    return sum(model.x[i, j, k] for i in model.CUSTOMERS if i != j) == (
        (sum(model.x[j, i, k] for i in model.CUSTOMERS)))
model.enter_go = pyo.Constraint(model.CUSTOMERS, model.VEHICLES, rule=enter)

def flow_rule(model, j):
    return sum(model.x[i, j, k]
               for i in model.CUSTOMERS
               for k in model.VEHICLES) == 1
model.flow_constraint = pyo.Constraint(model.cust, rule=flow_rule)

model.depot = pyo.ConstraintList()
for k in model.VEHICLES:
    model.depot.add(sum(model.x["A1", j, k] for j in model.cust) == 1)
    model.depot.add(sum(model.x[i, "A1", k] for i in model.cust) == 1)

def subtour(model, i, j, k):
    if i != j:
        return model.u[i] - model.u[j] >= model.demand[j] - model.capacity[k]*(1 - model.x[i, j, k])
    else:
        return model.u[i] - model.u[i] == 0
model.sub_tour = pyo.Constraint(model.cust, model.cust, model.VEHICLES, rule = subtour)

model.subtour = pyo.ConstraintList()
for i in model.cust:
    for k in model.VEHICLES:
        model.subtour.add(model.demand[i] <= model.u[i])
        model.subtour.add(model.capacity[k] >= model.u[i])

model.x_and_pen = pyo.ConstraintList()

# for k in model.VEHICLES:
#     for i in model.CUSTOMERS:
            # model.x_and_pen.add(sum(model.x[i, j, k] if j != i else 0 for j in model.cust) + pen[j] == 1)
# model.x_and_pen.add(sum(model.x[i, "A12", k] for i in model.CUSTOMERS for k in model.VEHICLES) == 0)
# model.x_and_pen.add(sum(model.x[i, "A13", k] for i in model.CUSTOMERS for k in model.VEHICLES) == 0)
# model.x_and_pen.add(pen["A12"] == 1)
# model.x_and_pen.add(pen["A13"] == 1)

# model.x_and_pen.add(sum(model.x[i, j, k] for k in model.VEHICLES for i in model.CUSTOMERS for j in model.CUSTOMERS if i != j) == len(cust_dem) - 2)

# Solution
solver = SolverFactory('cplex')
results = solver.solve(model)

# Print the results
# print('Objective value:', model.objective())
total_load = 0
for k in model.VEHICLES:
    tload = 0
    print(f'Route for vehicle-{k}:')
    route = [f"{(i, j)} -> {model.demand[j]}" for i in model.CUSTOMERS
              for j in model.CUSTOMERS
              if (model.x[i, j, k].value == 1) if i != j]
    for i in model.CUSTOMERS:
        for j in model.CUSTOMERS:
            if model.x[i, j, k]() == 1:
                dist[k] += model.distance[j][i]
                tload += model.demand[j]
    total_load += tload
    print(route)
    print(f"\nVehicle-{k} travelled {dist[k]} m with a total load of {tload} tons\n")
print(f"Total load after all routes = {total_load} tons")

# for i in model.CUSTOMERS:
#     for j in model.CUSTOMERS:
#         for k in model.VEHICLES:
#             if model.x[i, j, k]():
#                 print(f"{model.x[i, j, k]} = {model.x[i, j, k]()}")

# for i in model.cust:
#     print(f"{pen[i]} = {pen[i]()}")
dropped = {"pts" : set()}
# for i in model.CUSTOMERS:
#     for j in model.CUSTOMERS:
#         if model.x[i, j, "V4"]() and model.x[i, j, "V4"]() > 0.9 and (i != "A1" or j != "A1"):
#             dropped["pts"].add(i) if i != "A1" else dropped["pts"].add(j)
# print(f"Dropped customers: {dropped['pts']}")