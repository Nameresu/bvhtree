import numpy as np
import numpyextend as npe


class Ray:

  def __init__(self, fr, to):
    self.origin = fr
    self.direction = npe.Normalize3f(to - fr)


class HitRecord:

  def __init__(self, r):
    self.isHit = False
    self.t = -1
    self.ray = r
    self.id = -1