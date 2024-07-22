from gurobipy import GRB
import heapq
from typing import List
import math
import graphviz
from gurobi_solution import model, var_names, binary_vars, model_sense

class Node:
    
    def __init__(self, model, depth, name):
        self.model = model
        self.depth = depth
        self.solution = None
        self.obj_val = None
        self.name = name
        print("depth =",self.depth)  #sanity check

    def is_integer(self, int_vars) -> bool:
        int_vars = [var.varName for var in int_vars]
        for var in int_vars:
            val = self.model.getVarByName(var).x
            if val != int(val):
                return False
        return True

    def __lt__(self, other):
        return self.obj_val > other.obj_val  # For heap implementation. The heapq.heapify() will heapify the list based on this criteria.

    def relaxed_LP(self) -> int:
        self.model= self.model.relax() #Create the relaxation of a MIP model. Transforms integer variables into continuous variables, and removes SOS and general constraints.
        self.model.update()
        self.model.optimize()
        if self.model.status == GRB.OPTIMAL:
            self.solution = self.model.getAttr(GRB.Attr.X)
            self.obj_val =  self.model.getAttr(GRB.Attr.ObjVal)
            #return self.solution, self.obj_val, relaxed_model.status
            return self.model.status
        else: return 0
        
def branch_and_bound(model, var_names, binary_vars, model_sense = "max"):
    # Create the root node
    root_node = Node(model, 0, "root_node")
    
    # Solve the root node's LP relaxation
    status = root_node.relaxed_LP()
    if status!= GRB.OPTIMAL:
        print("No feasible solution found.")
        return
    
    #initialize best node and the stack
    best_node = None
    best_obj = -GRB.INFINITY
    stack = [root_node]
    heapq.heapify(stack)  #we are going to traverse in best first manner

    #draw the branch and bound tree, start with root
    dot = graphviz.Digraph('Branch and bound tree', comment='Branch and bound tree', node_attr={'color': 'lightblue', 'style': 'filled'})
    dot.node('root_node', root_node.name)

    #loop through the stack
    while stack:
        node = heapq.heappop(stack)
        if model_sense=="min":
            best_obj=best_obj*-1    #if the objective is to minimize
        if (model_sense=="max" and node.obj_val > best_obj) or (model_sense=="min" and node.obj_val < best_obj):
            if node.is_integer(binary_vars):
                best_node = node
                best_obj = node.obj_val
            else:
                fractional_var = None
                for var in var_names:
                    val = node.model.getVarByName(var).x
                    if val != int(val):
                        fractional_var = var #extract the first fractional variable among the binary variables
                        break
                
                if fractional_var:
                    val = node.model.getVarByName(fractional_var).x
                    
                    # Create left branch node
                    left_node = Node(node.model.copy(), node.depth + 1, f'{fractional_var}={math.floor(val)}')
                    for var in left_node.model.getVars():
                        if var.VarName == fractional_var:
                            var.LB = math.floor(val)
                            var.UB = math.floor(val)
                            left_node.model.update()

                    status = left_node.relaxed_LP()
                    if status!= GRB.OPTIMAL:
                        dot.node(f'{fractional_var}={math.floor(val)}', f'{fractional_var}={math.floor(val)}' + '\n' + 'infeasible', {'fontcolor':'red'})
                        dot.edge(node.name, left_node.name)
                        continue    #Prune
                    elif status == GRB.OPTIMAL:
                        dot.node(f'{fractional_var}={math.floor(val)}', f'{fractional_var}={math.floor(val)}')
                        dot.edge(node.name, left_node.name)
                        heapq.heappush(stack, left_node)
                    
                    # Create right branch nodes
                    right_node = Node(node.model.copy(), node.depth + 1, f'{fractional_var}={math.ceil(val)}')
                    for var in right_node.model.getVars():
                        if var.VarName == fractional_var:
                            var.LB = math.ceil(val)
                            var.UB = math.ceil(val)
                            right_node.model.update()

                    status = right_node.relaxed_LP()
                    if status!= GRB.OPTIMAL:
                        dot.node(f'{fractional_var}={math.ceil(val)}', f'{fractional_var}={math.ceil(val)}' + '\n' + 'infeasible', {'fontcolor':'red'})
                        dot.edge(node.name, right_node.name)
                        continue    #Prune
                    elif status == GRB.OPTIMAL:
                        dot.node(f'{fractional_var}={math.ceil(val)}', f'{fractional_var}={math.ceil(val)}')
                        dot.edge(node.name, right_node.name) 
                        heapq.heappush(stack, right_node)
        else:
            dot.node(node.name, node.name + '\n' + 'feasible but worse') #Prune

    if best_node:
        print("Optimal solution found:")
        for var in var_names:
            print(f"{var}: {best_node.model.getVarByName(var).x}")
        print(f"Objective value: {best_node.obj_val}")
    else:
        print("No optimal solution found.")
    dot.render(filename='branch and bound', view=True, format = 'png')

def main():
    branch_and_bound(model, var_names, binary_vars, model_sense)

if __name__ == "__main__":
    main()