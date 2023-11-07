#!/usr/bin/env python3

from pulp import LpMaximize, LpProblem, LpStatus, lpSum, LpVariable, gurobi_api
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams['figure.figsize'] = [12, 6]

fig, ax = plt.subplots()

ORDER = False                    # Maintain order (faster)
W = 9                           # Width of container
M = 100                         # M is a big number > W
vars = [1,2,3,4,5,6,7]

def rect(x, y, w, h, s, color):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=color, edgecolor='white'))
    ax.text(x + w/2, y + h/2, s, fontsize=10, color='white', verticalalignment='center', horizontalalignment='center')    

def plot(model):
    plt.xlim([0, W*4])
    plt.ylim([0, W*2]) 
    ax.add_patch(Rectangle((0, 0), W, W*4, facecolor='#888888'))
    for i in vars:
        rect(x[i].value(), y[i].value(), w[i].value(), h[i].value(), i, '#2394C0')
    plt.show()

model = LpProblem(name="pack-generic")

x = LpVariable.dicts('x', vars, lowBound=0)
y = LpVariable.dicts('y', vars, lowBound=0)
w = LpVariable.dicts('w', vars, lowBound=0)
h = LpVariable.dicts('h', vars, lowBound=0)

d = LpVariable.dicts('d', [(i, j, k) for i in vars for j in vars for k in range(4) if i < j],
                     lowBound = 0, upBound = 1, cat="Integer")

for i in vars:
    # overlap
    for j in vars:
        if i < j:
            model += (x[i] + w[i] <= x[j] + M*d[(i,j,0)])
            model += (x[j] + w[j] <= x[i] + M*d[(i,j,1)])
            model += (y[i] + h[i] <= y[j] + M*d[(i,j,2)])
            model += (y[j] + h[j] <= y[i] + M*d[(i,j,3)])
            model += (d[(i,j,0)] + d[(i,j,1)] + d[(i,j,2)] + d[(i,j,3)] <= 3)
    # sequence
    if ORDER and i != vars[len(vars)-1]:
        model += (W*y[i] + x[i] <= W*y[i+1] + x[i+1] + 2*h[i+1])
    # containment
    model += (x[i] + w[i] <= W)
    # ratios
    if i % 2 != 1:
        model += (w[i] == 3)
        model += (h[i] == 2)
    else:
        model += (w[i] == 3)
        model += (h[i] == 4)
              
#model += (y[7] == 3.8)

# Add the objective function which we want to minimize
# model += lpSum([y[i]+x[i]-w[i] for i in vars])
model += lpSum([y[i] for i in vars])

#print(model)

# Solve the problem
status = model.solve(gurobi_api.GUROBI())
if status != -1:
    plot(model)
else:
    print("Infeasible")

# print(model)
for var in model.variables():
        print(f"{var.name}: {var.value()}")

