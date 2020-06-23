import os
import numpy as np


def parse_vertex(s):
  tokens = s.split()
  return np.array([
      float(tokens[0]),
      float(tokens[1]),
      float(tokens[2]),
      float(tokens[3]),
      float(tokens[4])
  ])


def parse_face(s):
  ret = {}
  tokens = s.split()
  ret['index1'] = int(tokens[1])
  ret['index2'] = int(tokens[2])
  ret['index3'] = int(tokens[3])

  return ret


def parse_PLY():
  vertices = []
  face = []
  #path = os.path.join(".", "Sphere.ply", "Sphere.ply")
  path = os.path.join(".", "bunny.ply", "bunny.ply")
  with open(path, "r") as f:
    for i in range(13):  #13 10
      line = f.readline().strip(chr(10))

    lx = ly = lz = 100.0
    rx = ry = rz = -100.0
    for i in range(35947):  #35947 642
      line = f.readline().strip(chr(10))
      vertex = parse_vertex(line)
      vertices.append(vertex)
      lx = min(lx, vertex[0])
      rx = max(rx, vertex[0])
      ly = min(ly, vertex[1])
      ry = max(ry, vertex[1])
      lz = min(lz, vertex[2])
      rz = max(rz, vertex[2])

    for i in range(69451):  #69451 1280
      line = f.readline().strip(chr(10))
      index = parse_face(line)
      face.append(index)

  print(lx, ", ", rx)
  print(ly, ", ", ry)
  print(lz, ", ", rz)
  print("center x  : ", (lx + rx) / 2)
  print("center y  : ", (ly + ry) / 2)
  print("center z  : ", (lz + rz) / 2)
  return [vertices, face]
