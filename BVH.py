import math
import numpy as np
import ray
import geoprimitive as geo


class Buckets:

  def __init__(self):
    self.count = 0
    self.bounds = geo.Bounds3f()

  def init(self):
    self.count = 0
    self.bounds.init()


class BVHPrimitiveInfo:

  def __init__(self, id, b):
    self.id = id
    self.bounds = b
    self.centroid = (self.bounds.pMax + self.bounds.pMin) * 0.5


class BVHNode:

  def __init__(self):
    self.firstPrimOffset = -1
    self.nPrimitives = 0
    self.bounds = geo.Bounds3f()
    self.splitAxis = -1
    self.children = np.array([None for i in range(2)])

  def InitLeaf(self, first, n, bounds):
    self.firstPrimOffset = first
    self.nPrimitives = n
    self.bounds = bounds

  def InitInterior(self, axis, c0, c1, dim):
    self.children[0] = c0
    self.children[1] = c1
    self.splitAxis = dim
    self.bounds = c0.bounds.UnionBounds(c1.bounds)


class BVHTree:

  def __init__(self, primList):
    self.buckets = [Buckets() for i in range(12)]
    self.bvhCost = [.0 for i in range(len(self.buckets))]
    self.maxPrimsInNode = 4
    self.totalNode = 0
    self.primList = primList
    self.primitiveInfo = []
    self.ordedPrimitive = []
    for i in range(len(primList)):
      self.primitiveInfo.append(BVHPrimitiveInfo(i, primList[i].Bounds()))
    self.root = self.RecursiveBuild(0, len(primList))
    self.primList = self.ordedPrimitive
    print(self.totalNode)

  def RecursiveBuild(self, st, n):
    self.totalNode = self.totalNode + 1
    cur = BVHNode()
    bounds = geo.Bounds3f()
    for i in range(st, st + n):
      bounds = bounds.UnionBounds(self.primitiveInfo[i].bounds)
    for i in range(3):
      if (bounds.pMin[i] > 1e6):
        print("pMin Here")
      if (bounds.pMax[i] < -1e6):
        print("pMax here")
    if (n == 1):
      first = len(self.ordedPrimitive)
      for p in self.primitiveInfo[st:st + n]:
        self.ordedPrimitive.append(self.primList[p.id])
      cur.InitLeaf(first, n, bounds)

    else:
      centroidBounds = geo.Bounds3f()
      for p in self.primitiveInfo[st:st + n]:
        centroidBounds = centroidBounds.UnionPoint(p.centroid)
      dim = centroidBounds.MaximumExtent()

      if (centroidBounds.pMax[dim] == centroidBounds.pMin[dim]):
        first = len(self.ordedPrimitive)
        for p in self.primitiveInfo[st:st + n]:
          self.ordedPrimitive.append(self.primList[p.id])

        cur.InitLeaf(first, n, bounds)

      else:
        isLeaf = False
        num1 = num2 = 0
        if (n <= 4):
          [isLeaf, num1, num2] = self.SplitByCount(centroidBounds, st, n, dim)
        else:
          #[isLeaf, num1, num2] = self.SplitByBVH(centroidBounds, st, n, dim, bounds)
          [isLeaf, num1, num2] = self.SplitByMiddle(centroidBounds, st, n, dim)
          #[isLeaf, num1, num2] = self.SplitByCount(centroidBounds, st, n, dim)
        if (not isLeaf):
          cur.InitInterior(dim, self.RecursiveBuild(st, num1),
                           self.RecursiveBuild(st + num1, num2), dim)
        else:
          first = len(self.ordedPrimitive)
          for p in self.primitiveInfo[st:st + n]:
            self.ordedPrimitive.append(self.primList[p.id])

          cur.InitLeaf(first, n, bounds)

    return cur

  def SplitByMiddle(self, centroidBounds, st, n, dim):
    unpredicate = centroidBounds.centroid[dim]
    unpredicate_st = st
    for i in range(st, st + n):
      if (self.primitiveInfo[i].centroid[dim] < unpredicate):
        self.primitiveInfo[i], self.primitiveInfo[
            unpredicate_st] = self.primitiveInfo[
                unpredicate_st], self.primitiveInfo[i]
        unpredicate_st = unpredicate_st + 1
    mid = unpredicate_st
    if (unpredicate_st == st or unpredicate_st == st + n):
      return self.SplitByCount(centroidBounds, st, n, dim)
    else:
      num1 = mid - st
      num2 = n - num1
      return [False, num1, num2]

  def SplitByCount(self, centroidBounds, st, n, dim):
    self.primitiveInfo[st:st + n] = sorted(self.primitiveInfo[st:st + n],
                                           key=lambda p: p.centroid[dim])
    mid = math.floor((st + st + (n - 1)) / 2) + 1
    num1 = mid - st
    num2 = n - num1
    #print(st, n, num1, num2)
    return [False, num1, num2]

  def SplitByBVH(self, centroidBounds, st, n, dim, nodeBounds):
    for i in range(len(self.buckets)):
      self.buckets[i].bounds.init()
      self.bvhCost[i] = float("inf")
    isStrange = True
    for prim in self.primitiveInfo[st:st + n]:
      index = math.floor(
          len(self.buckets) * centroidBounds.Offset(prim.centroid)[dim])
      if (index == len(self.buckets)):
        index = index - 1
        isStrange = False
      self.buckets[index].count = self.buckets[index].count + 1
      self.buckets[index].bounds = self.buckets[index].bounds.UnionBounds(
          prim.bounds)
    for i in range(1, len(self.buckets)):  # i is the first unpredicated
      leftBounds = geo.Bounds3f()
      rightBounds = geo.Bounds3f()
      leftCount = rightCount = 0
      for j in range(0, i):
        leftBounds = leftBounds.UnionBounds(self.buckets[j].bounds)
        leftCount = leftCount + self.buckets[j].count
      for j in range(i, len(self.buckets)):
        rightBounds = rightBounds.UnionBounds(self.buckets[j].bounds)
        rightCount = rightCount + self.buckets[j].count
      leftArea = leftBounds.SurfaceArea()
      rightArea = rightBounds.SurfaceArea()
      self.bvhCost[i] = .125 + (
          (leftCount * leftArea + rightCount * rightArea) /
          nodeBounds.SurfaceArea())
    minCost = float("inf")
    splitIndex = -1  #first Unpredicate block
    for i in range(len(self.bvhCost)):
      if (minCost > self.bvhCost[i]):
        minCost = self.bvhCost[i]
        splitIndex = i
    leafCost = n
    if (n < self.maxPrimsInNode and minCost > leafCost):
      return [True, -1, -1]
    unpredicate = splitIndex
    unpredicate_st = st
    for i in range(st, st + n):
      index = math.floor(
          len(self.buckets) *
          centroidBounds.Offset(self.primitiveInfo[i].centroid)[dim])
      if (index < unpredicate):
        self.primitiveInfo[i], self.primitiveInfo[
            unpredicate_st] = self.primitiveInfo[
                unpredicate_st], self.primitiveInfo[i]
        unpredicate_st = unpredicate_st + 1
    mid = unpredicate_st
    num1 = mid - st
    num2 = n - num1
    return [False, num1, num2]

  def RayIntersect(self, r):
    ret = ray.HitRecord(r)
    stack = [self.root]
    while (len(stack) > 0):
      cur = stack.pop()
      hitBoundsRecord = cur.bounds.RayIntersect(r)
      if (hitBoundsRecord.isHit):
        if (cur.nPrimitives > 0):
          t = float("inf")
          for i in range(cur.firstPrimOffset,
                         cur.firstPrimOffset + cur.nPrimitives):
            hitTriangleBounds = self.primList[i].RayIntersect(r)
            if (hitTriangleBounds.isHit):
              if (t > hitTriangleBounds.t):
                t = hitTriangleBounds.t
                ret.isHit = True
                ret.t = t
                ret.id = i
          if (ret.isHit):
            break
        else:
          if (r.direction[cur.splitAxis] < 0):
            stack.append(cur.children[0])  #Far
            stack.append(cur.children[1])  #Near
          else:
            stack.append(cur.children[1])  #Far
            stack.append(cur.children[0])  #Near

    return ret
