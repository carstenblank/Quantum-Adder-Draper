
import matplotlib.pyplot as plt
import math
import numpy as np

X = np.arange(0, 2*math.pi, 0.1)
Y = np.cos(X) - np.sin(X)

plt.plot(X,Y)
plt.show()


