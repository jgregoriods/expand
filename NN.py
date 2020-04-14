
import numpy as np

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def activation(theta, X):
    a = [X]
    for i in range(len(theta)): 
        a.append(sigmoid(np.dot(np.concatenate(([1], a[i])), theta[i])))
    return a



