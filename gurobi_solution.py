'''This file contains the problem definition and the solution in Gurobi'''

import gurobipy as gp
from gurobipy import GRB
model = gp.Model()
x1 = model.addVar(vtype=GRB.BINARY, name="x1", lb = 0, ub = 1)
x2 = model.addVar(vtype=GRB.BINARY, name="x2", lb = 0, ub = 1)
x3 = model.addVar(vtype=GRB.BINARY, name="x3", lb = 0, ub = 1)
x4 = model.addVar(vtype=GRB.BINARY, name="x4", lb = 0, ub = 1)
model.setObjective(9*x1 + 5*x2 + 6*x3 + 4*x4, GRB.MAXIMIZE)
model.addConstr(6*x1 + 3*x2 + 5*x3 + 2*x4 <= 10)
model.addConstr(x3 + x4 <= 1)
model.addConstr(x3 - x1 <= 0)
model.addConstr(-x2 + x4 <= 0)

# test problem 2
#x1 = model.addVar(vtype=GRB.INTEGER, name="x1", lb = 0, ub = GRB.INFINITY)
#x2 = model.addVar(vtype=GRB.INTEGER, name="x2", lb = 0, ub = GRB.INFINITY)
#x3 = model.addVar(vtype=GRB.INTEGER, name="x3", lb = 0, ub = GRB.INFINITY)
#x4 = model.addVar(vtype=GRB.CONTINUOUS, name="x4", lb = 0, ub = GRB.INFINITY)
#model.setObjective(4*x1 - 2*x2 + 7*x3 - x4, GRB.MAXIMIZE)
#model.addConstr(-x1 + 5*x3 <= 10)
#model.addConstr(x1 + x2 - x3 <= 1)
#model.addConstr(1*x1 + 5*x2 <= 10)
#model.addConstr(-x1 + 2*x3 - 2*x4 <= 3)
#model.addConstr(x1 - 2*x2 - 3*x4 <= 4)

model.update()
vars = [var for var in model.getVars()]
var_names = [var.VarName for var in vars]
binary_vars = [var for var in model.getVars() if var.vType == GRB.BINARY or var.vType == GRB.INTEGER]
model_sense = "max"
model.optimize()
solution = model.getAttr(GRB.Attr.X)
print(f"Gurobi Solution: {solution}")
