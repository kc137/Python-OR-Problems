# -*- coding: utf-8 -*-
"""S7-Problem2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1u81HuyN06PP9YyGt2BMALn_NgWxS9ie_
"""

import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import pandas as pd
import math

model = pyo.ConcreteModel()

#Sets
model.i = pyo.RangeSet(1,15)

#Parameters
W = pd.read_excel('S7P2_Data.xlsx',sheet_name='Sheet1',header=0,index_col=0,usecols='A:B')
#W['D'][2]

model.Pload = pyo.Param(initialize = 300)
Pload = model.Pload
model.Pmax = pyo.Param(initialize = 1000)
Pmax = model.Pmax
model.defml = pyo.Param(initialize = 6)
defml = model.defml
model.deflpm = pyo.Param(initialize = 1.25)
deflpm = model.deflpm
model.Lmax = pyo.Param(initialize = 14)
Lmax = model.Lmax
model.Dcm = pyo.Param(initialize = 3)
Dcm = model.Dcm
model.dWm = pyo.Param(initialize = 0.2)
dWm = model.dWm
model.S = pyo.Param(initialize = 234440)
S = model.S
model.G = pyo.Param(initialize = 11600000)
G = model.G

#Decision Variables
#Positive Reals
model.Dc = pyo.Var(domain = pyo.NonNegativeReals, bounds=(0.4,3))
Dc = model.Dc
model.dW = pyo.Var(domain = pyo.NonNegativeReals, bounds=(0.2,None))
dW = model.dW
model.defl = pyo.Var(domain = pyo.NonNegativeReals, bounds=(0.0018,6))
defl = model.defl
model.C = pyo.Var(domain = pyo.NonNegativeReals, bounds=(3,None))
C = model.C
model.K = pyo.Var(domain = pyo.NonNegativeReals, bounds=(None,560))
K = model.K

#Integer
model.N = pyo.Var(domain = pyo.NonNegativeIntegers,bounds=(1,None))
N = model.N

#Binary
model.x = pyo.Var(model.i,domain=pyo.Binary)
x = model.x

#Objective Function
def Objective_rule(model):
  return math.pi*Dc*(dW**2)*(N+2)/4
model.Objf = pyo.Objective(rule=Objective_rule,sense=pyo.minimize)

#Constraints
def Constraint1(model):
  return Dc/dW == C
model.Const1 = pyo.Constraint(rule=Constraint1)

def Constraint2(model):
  return ((4*C-1)/(4*C-4))+0.615/C == K
model.Const2 = pyo.Constraint(rule=Constraint2)

def Constraint3(model):
  return (8*K*Pmax*Dc/(math.pi*dW**3)) <= S
model.Const3 = pyo.Constraint(rule=Constraint3)

def Constraint4(model):
  return 8*(Dc**3)*N/(G*(dW**2)) == defl
model.Const4 = pyo.Constraint(rule=Constraint4)

def Constraint5(model):
  return Pmax*defl+1.05*(N+2)*dW <= Lmax
model.Const5 = pyo.Constraint(rule=Constraint5)

def Constraint6(model,i):
  return sum(W['D'][i]*x[i] for i in model.i) == dW
model.Const6 = pyo.Constraint(rule=Constraint6)

def Constraint7(model,i):
  return sum(x[i] for i in model.i) == 1
model.Const7 = pyo.Constraint(rule=Constraint7)

Solver = SolverFactory("mindtpy")
results = Solver.solve(model, mip_solver = "glpk", nlp_solver = "ipopt")

print('Objective Function = ', model.Objf())
print('Number of Coils = ', N())
print('Coil Spring Diameter is= ',Dc())
print('Wire Diameter is= ', dW())
for i in model.i:
    if x[i]():
        print('Wire Type',i,'is selected')