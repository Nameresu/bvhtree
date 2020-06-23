import numpy as np

position = np.array([-0.0168404, 0.1101542, 5.0])
light = np.array([-0.0168404, 200.0, 100.0])
#direction = np.array([0,0,1])

lu = np.array([-0.1446899, 0.237321, 2.0])
ll = np.array([-0.1446899, -0.00170126, 2.0])
ru = np.array([0.1110091, 0.237321, 2.0])
rl = np.array([0.1110091, -0.00170126, 2.0])

dy = ru - lu
dx = ll - lu

print(dy)
print(dx)