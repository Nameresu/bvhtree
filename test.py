import numpy as np
import time

import numpyextend as npe
import parserPLY as ply
import camera
import pictureinfo as picture
import ray
import geoprimitive as geo
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
"""
[vertices, face] = ply.parse_PLY()
executor = ThreadPoolExecutor(max_workers=128)


def calc(i, j):
  to = camera.lu + (j / picture.width) * camera.dy + (
      i / picture.height) * camera.dx
  to = to + 0.5 * (1 / picture.width) * camera.dy + 0.5 * (
      1 / picture.height) * camera.dx
  r = ray.Ray(camera.position, to)

  result = []
  for i in range(0, len(T_list)):
    result.append(T_list[i].RayIntersect(r))
  return result


T_list = []
for i in range(len(face)):
  v0 = vertices[face[i]['index1']]
  v1 = vertices[face[i]['index2']]
  v2 = vertices[face[i]['index3']]
  T_list.append(geo.Triangle(v0, v1, v2))
cnt = 0

jobs = []
for i in range(0, picture.height):
  print('i: ', i)
  t = time.time()
  results = executor.map(calc, [i] * picture.width, range(0, picture.width))
  results = list(results)
  print('time: ', time.time() - t)

picture.RGBarray[i*(picture.width*3) + j*3 + 0] = 255
picture.RGBarray[i*(picture.width*3) + j*3 + 1] = 255
picture.RGBarray[i*(picture.width*3) + j*3 + 2] = 255
"""
b = geo.Bounds3f()
b = b.UnionPoint(np.array([0, 1, 2]))
b = b.UnionPoint(np.array([3, 4, 5]))
print(b.SurfaceArea())
