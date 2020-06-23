import numpy as np


def Normalize3f(v):
  norm = np.linalg.norm(v)
  if norm == 0:
    return v
  else:
    return v / norm