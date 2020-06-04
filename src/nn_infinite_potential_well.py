import argparse

import autograd.numpy as np 
from scipy.integrate import simps
from scipy.constants import h, hbar, m_e 
import matplotlib.pyplot as plt

from neural_schroedinger.solver import NN

parser = argparse.ArgumentParser('Infinite potential well demo')
parser.add_argument('-x', '--training_points', type=int, default=50,
    help='Number of grid points over the x-axis that will serve\
         as training points.')
parser.add_argument('-l', '--hidden_layers', type=int, default=1,
    help='Number of hidden layers.')
parser.add_argument('-n', '--hidden_units', type=int, default=10,
    help='Number of hidden units per hidden layer.')
parser.add_argument('-a', '--activation', type=str, default='tanh',
    choices=['tanh', 'sigmoid', 'relu', 'elu', 'softplus'], 
    help='Activation function for both input and hidden layers.')
parser.add_argument('-o', '--optimizer', type=str, default='bfgs',
    choices=['lbfgs', 'bfgs'], 
    help='Algorithm for the minimization of loss function.')
parser.add_argument('-i', '--iteration', type=int, default=2000,
    help='Number of training iterations for optimizer.')
parser.add_argument('-q', '--quantum_state', type=int, default=1,
    help='Principal quantum number - 1, 2, 3, ...')
args = parser.parse_args()

L = 1
n = args.quantum_state

def psi(x, n):
    A = np.sqrt(2/L)
    return A * np.sin(n * np.pi / L * x)

def pdf(x, n):
    return psi(x, n)**2

def f(x, y):
    return -(n**2 * h**2 / (8 * m_e))*2*m_e/hbar**2*y

# generate data 
x = np.linspace(0, 1, args.training_points).reshape(-1, 1)
bcs = (0.0, 0.0)
psi_anal = psi(x, n) 
pdf_anal = pdf(x, n) 
I_anal = simps(pdf_anal.ravel(), x.ravel())

sizes = [1] + args.hidden_layers * [args.hidden_units] + [1]
activation = args.activation
model = NN(f, x, bcs, sizes=sizes, activation=activation)
print(model)

model.fit(method=args.optimizer, maxiter=args.iteration)

psi, _ = model.predict() 
pdf = psi**2 
I = simps(pdf.ravel(), x.ravel())

# integrals
print(f'Integral of analytic solution is {I_anal}')
print(f'Integral of neural solution is {I}')

# plotting 
fig, ax = plt.subplots(nrows=2, ncols=1, sharex=True, squeeze=True)

# analytical
#ax[0].plot(x, psi_anal, 'k--', label=r'$\psi(x)$')
ax[0].plot(x, pdf_anal, 'k-', label=r'$|\psi(x)|^2$')
ax[0].grid()
ax[0].legend()

# neural network
#ax[1].plot(x, psi, 'k--', label=r'$\hat\psi(x)$')
ax[1].plot(x, pdf, 'k-', label=r'$|\hat\psi(x)|^2$')
ax[1].grid()
ax[1].legend()

plt.xlabel(r'$x$')
plt.show()