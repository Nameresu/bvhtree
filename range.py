import os
import test as test

print(test.a)


def parse_vertex(s):
  ret = {}
  tokens = s.split()
  ret['x'] = float(tokens[0])
  ret['y'] = float(tokens[1])
  ret['z'] = float(tokens[2])

  return ret


def parse_face(s):
  ret = {}
  tokens = s.split()
  ret['index1'] = int(tokens[1])
  ret['index2'] = int(tokens[2])
  ret['index3'] = int(tokens[3])

  return ret


vertices = []
face = []
path = os.path.join(".", "bunny.ply", "bunny.ply")
with open(path, "r") as f:
  for i in range(13):
    line = f.readline().strip(chr(10))

  lx = ly = lz = 100.0
  rx = ry = rz = -100.0
  for i in range(35947):
    line = f.readline().strip(chr(10))
    vertex = parse_vertex(line)
    vertices.append(vertex)
    lx = min(lx, vertex['x'])
    rx = max(rx, vertex['x'])
    ly = min(ly, vertex['y'])
    ry = max(ry, vertex['y'])
    lz = min(lz, vertex['z'])
    rz = max(rz, vertex['z'])

  for i in range(69451):
    line = f.readline().strip(chr(10))
    index = parse_face(line)
    face.append(index)

with open("input.txt", "w") as f:
  for i in range(69451):
    v1 = vertices[face[i]['index1']]
    v2 = vertices[face[i]['index2']]
    v3 = vertices[face[i]['index3']]
    strv1 = str(v1['x']) + " " + str(v1['y']) + " " + str(v1['z'])
    strv2 = str(v2['x']) + " " + str(v2['y']) + " " + str(v2['z'])
    strv3 = str(v3['x']) + " " + str(v3['y']) + " " + str(v3['z'])
    res = "T " + strv1 + " " + strv2 + " " + strv3 + "\n"
    f.write(res)

print(lx, ", ", rx)
print(ly, ", ", ry)
print(lz, ", ", rz)
print(len(face))