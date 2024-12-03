# -*- coding: utf-8 -*-
"""S7-Problem3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uLjWYgqdJZZb3Fer0MFni7GkO7hVIRO8
"""

import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import pandas as pd

model = pyo.ConcreteModel()

#Sets
model.i = pyo.RangeSet(1,3)

#Parameters
D = pd.read_excel('S7P3_Data.xlsx',sheet_name='Sheet1',header=0,index_col=0,usecols='A:J',nrows=3)
#D['Co'][1]

model.Vt = pyo.Param(initialize = 350)
Vt = model.Vt
model.DPt = pyo.Param(initialize = 400)
DPt = model.DPt
model.Wmax = pyo.Param(initialize = 2950)
Wmax = model.Wmax
model.Npmax = pyo.Param(initialize = 3)
Npmax = model.Npmax
model.Nsmax = pyo.Param(initialize = 3)
Nsmax = model.Nsmax

#Decision Variables
#Positive Reals
model.x = pyo.Var(model.i,domain=pyo.NonNegativeReals,bounds = (0,1))
x = model.x
model.v = pyo.Var(model.i,domain=pyo.NonNegativeReals,bounds = (0,Vt))
v = model.v
model.w = pyo.Var(model.i,domain=pyo.NonNegativeReals,bounds = (0,Wmax))
w = model.w
model.DP = pyo.Var(model.i,domain=pyo.NonNegativeReals,bounds = (0,DPt))
DP = model.DP

def Power_max(model, i):
    return (0, D["Pmax"][i])

model.P = pyo.Var(model.i, domain = pyo.NonNegativeReals, bounds = Power_max)
P = model.P

#Integer Variables
model.Np = pyo.Var(model.i,domain = pyo.NonNegativeIntegers, bounds=(0,3))
Np = model.Np
model.Ns = pyo.Var(model.i,domain = pyo.NonNegativeIntegers, bounds=(0,3))
Ns = model.Ns

#Binary Variable
model.z = pyo.Var(model.i,domain=pyo.Binary)
z = model.z

#Objective Function
def Objective_rule(model):
  return sum((D['Co'][i]+(D['Cp'][i]*P[i]))*Np[i]*Ns[i]*z[i] for i in model.i)
model.Objf = pyo.Objective(rule=Objective_rule,sense=pyo.minimize)

#Constraints
def Constraint1(model,i):
  return sum(x[i] for i in model.i) == 1
model.Const1 = pyo.Constraint(model.i,rule=Constraint1)

def Constraint2(model,i):
  return P[i] - D['alpha'][i]*(w[i]/Wmax)**3 - D['beta'][i]*(w[i]/Wmax)**2*v[i] - D['gamma'][i]*(w[i]/Wmax)*(v[i]**2) == 0
model.Const2 = pyo.Constraint(model.i,rule=Constraint2)

def Constraint3(model,i):
  return DP[i] - D['a'][i]*(w[i]/Wmax)**2 - D['b'][i]*(w[i]/Wmax)*v[i] - D['c'][i]*(v[i]**2) == 0
model.Const3 = pyo.Constraint(model.i,rule=Constraint3)

def Constraint4(model,i):
  return v[i]*Np[i] - x[i]*Vt == 0
model.Const4 = pyo.Constraint(model.i,rule=Constraint4)

def Constraint5(model,i):
  return DPt*z[i] - DP[i]*Ns[i] == 0
model.Const5 = pyo.Constraint(model.i,rule=Constraint5)

def Constraint6(model,i):
  return P[i] - z[i]*D['Pmax'][i] <= 0
model.Const6 = pyo.Constraint(model.i, rule=Constraint6)

def Constraint7(model,i):
  return DP[i] <= z[i]*DPt
model.Const7 = pyo.Constraint(model.i, rule=Constraint7)

def Constraint8(model,i):
  return v[i] <= z[i]*Vt
model.Const8 = pyo.Constraint(model.i, rule=Constraint8)

def Constraint9(model,i):
  return w[i] <= z[i]*Wmax
model.Const9 = pyo.Constraint(model.i, rule=Constraint9)

def Constraint10(model,i):
  return Np[i] <= z[i]*Npmax
model.Const10 = pyo.Constraint(model.i, rule=Constraint10)

def Constraint11(model,i):
  return Ns[i] <= z[i]*Nsmax
model.Const11 = pyo.Constraint(model.i, rule=Constraint11)

def Constraint12(model,i):
  return x[i]<=z[i]
model.Const12 = pyo.Constraint(model.i, rule=Constraint12)

# sol = SolverFactory("mindtpy")
# res = sol.solve(model, mip_solver = "glpk", nlp_solver = "ipopt")

sol = SolverFactory("couenne")
res = sol.solve(model)

model.pprint()
print('Objective Function= ',model.Objf())
for i in model.i:
  print('Number of Parallel Lines at Level ',i,'is = ',Np[i]())
  print('Number of Pumps in Each Line at Level ',i,'is = ',Ns[i]())

"""![S7P3-R.png](data:image/png;base64,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)"""