"""ss"""
import numpy as np
import numpyextend as npe
import ray
import os


class Triangle:

  def __init__(self, v0, v1, v2):
    self.v0 = v0
    self.v1 = v1
    self.v2 = v2
    self.ambient = 0.0

  def RayIntersect(self, r):
    ret = ray.HitRecord(r)
    episilon = 1e-10
    e0 = self.v1 - self.v0
    e1 = self.v2 - self.v0
    h = np.cross(r.direction, e1)
    a = np.dot(e0, h)
    if (a > -episilon and a < episilon):
      return ret

    f = 1.0 / a
    s = r.origin - self.v0
    u = f * np.dot(s, h)
    if (u < 0.0 or u > 1.0):
      return ret

    q = np.cross(s, e0)
    v = f * np.dot(r.direction, q)
    if (v < 0.0 or u + v > 1.0):
      return ret

    t = f * np.dot(e1, q)
    if (t > episilon):
      ret.isHit = True
      ret.t = t
      return ret
    else:
      return ret

  def Bounds(self):
    bounds = Bounds3f()
    bounds = bounds.UnionPoint(self.v0)
    bounds = bounds.UnionPoint(self.v1)
    bounds = bounds.UnionPoint(self.v2)
    return bounds

  def GetNormalVector(self, p):
    e0 = self.v1 - self.v0
    e1 = self.v2 - self.v0
    ret = np.cross(e0, e1)
    ret = npe.Normalize3f(ret)
    return ret


class Bounds3f:

  def __init__(self):
    self.count = 0
    self.pMin = np.array([np.inf for i in range(3)])
    self.pMax = np.array([-np.inf for i in range(3)])
    self.centroid = np.zeros((3,))

  def init(self):
    self.count = 0
    for i in range(len(self.pMin)):
      self.pMin[i] = np.inf
    for i in range(len(self.pMax)):
      self.pMax[i] = -np.inf
    self.centroid = np.zeros((3,))

  def IsValid(self):
    for i in range(3):
      if (self.pMin[i] > self.pMax[i]):
        return False
    return True

  def UnionPoint(self, v):
    ret = Bounds3f()
    ret.count = self.count + 1
    ret.pMin[0] = min(self.pMin[0], v[0])
    ret.pMin[1] = min(self.pMin[1], v[1])
    ret.pMin[2] = min(self.pMin[2], v[2])
    ret.pMax[0] = max(self.pMax[0], v[0])
    ret.pMax[1] = max(self.pMax[1], v[1])
    ret.pMax[2] = max(self.pMax[2], v[2])
    ret.centroid = (ret.pMin + ret.pMax) / 2
    return ret

  def UnionBounds(self, b):
    ret = Bounds3f()
    if (not b.IsValid()):
      ret.pMin = self.pMin
      ret.pMax = self.pMax
      ret.count = self.count
      ret.centroid = self.centroid
    else:
      ret.count = self.count + b.count
      ret.pMin[0] = min(self.pMin[0], b.pMin[0])
      ret.pMin[1] = min(self.pMin[1], b.pMin[1])
      ret.pMin[2] = min(self.pMin[2], b.pMin[2])
      ret.pMax[0] = max(self.pMax[0], b.pMax[0])
      ret.pMax[1] = max(self.pMax[1], b.pMax[1])
      ret.pMax[2] = max(self.pMax[2], b.pMax[2])
      ret.centroid = (ret.pMin + ret.pMax) / 2
    """
    flag = False
    for i in range(3):
      if (flag):
        break
      if (ret.pMin[i] > 1e6):
        print("pMin", ret.pMin)
        flag = True
      if (ret.pMax[i] < -1e6):
        print("pMax", ret.pMax)
        flag = True
    """

    return ret

  def MaximumExtent(self):
    dx = self.pMax[0] - self.pMin[0]
    dy = self.pMax[1] - self.pMin[1]
    dz = self.pMax[2] - self.pMin[2]
    if (dx >= dy and dx >= dz):
      return 0
    elif (dy >= dz):
      return 1
    else:
      return 2

  def Offset(self, p):
    ret = p - self.pMin
    ret[0] = ret[0] / (self.pMax[0] - self.pMin[0])
    ret[1] = ret[1] / (self.pMax[1] - self.pMin[1])
    ret[2] = ret[2] / (self.pMax[2] - self.pMin[2])
    return ret

  def SurfaceArea(self):
    [dx, dy, dz] = self.pMax - self.pMin
    return 2 * (dx * dy + dy * dz + dz * dx)

  def RayIntersect(self, r):
    ret = ray.HitRecord(r)
    tMin = 0.0
    tMax = float("inf")
    for i in range(3):
      if (r.direction[i] == 0.0):
        if (r.origin[i] < self.pMin[i] or r.origin[i] > self.pMax[i]):
          return ret
      else:
        invRayDir = 1 / r.direction[i]
        curMin = (self.pMin[i] - r.origin[i]) * invRayDir
        curMax = (self.pMax[i] - r.origin[i]) * invRayDir
        if (curMin > curMax):
          curMin, curMax = curMax, curMin

        tMin = max(tMin, curMin)
        tMax = min(tMax, curMax)
    if (tMin > tMax):
      return ret
    ret.t = tMin
    ret.isHit = True
    return ret
