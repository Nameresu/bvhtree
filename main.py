import os
import random
import math
import numpy as np

import numpyextend as npe
import parserPLY as ply
import camera
import pictureinfo as picture
import ray
import geoprimitive as geo
import BVH
from PIL import Image
import time


def getColor(r, accelerator, dep):
  dep = dep + 1
  if (dep > 3):
    return np.array([.0, .0, .0])
  prim_hit = accelerator.RayIntersect(r)
  #print("Hit__getColor__", prim_hit.id)
  if (prim_hit.isHit):
    eyeToPrimRay = r
    primToLightRay = (ray.Ray(r.origin + prim_hit.t * r.direction,
                              camera.light))
    primNormal = accelerator.primList[prim_hit.id].GetNormalVector(r.origin +
                                                                   prim_hit.t *
                                                                   r.direction)
    if (np.dot(r.direction, primNormal) > 0):
      primNormal = primNormal * -1
    biSector = npe.Normalize3f(eyeToPrimRay.direction * -1 +
                               primToLightRay.direction)

    reflect = npe.Normalize3f(
        eyeToPrimRay.direction +
        2 * abs(np.dot(eyeToPrimRay.direction, primNormal)) * primNormal)
    ka = 0.25
    kd = 0.9
    ks = 0.3
    kr = 0.2
    if (dep == 1):
      kr = 1.0
    exp = 20
    shadow_hit = accelerator.RayIntersect(primToLightRay)

    ambient = ka * accelerator.primList[prim_hit.id].ambient
    #(np.dot(eyeToPrimRay.direction, primNormal) * np.dot(primToLightRay.direction, primNormal) > 0)
    diffuse = specular = .0
    if (not shadow_hit.isHit):
      diffuse = abs(kd * np.dot(primToLightRay.direction, primNormal))
      specular = abs(ks * math.pow(np.dot(biSector, primNormal), 20))
    Iad = ambient + diffuse
    R = 255 * Iad + 255 * specular
    G = 255 * Iad + 255 * specular
    B = 255 * Iad + 255 * specular
    hitPoint = r.origin + prim_hit.t * r.direction
    nxt = ray.Ray(hitPoint, hitPoint + reflect)
    return (np.array([R, G, B]) + getColor(nxt, accelerator, dep + 1)) * kr
  else:
    return np.array([.0, .0, .0])


def main():
  rnd = []
  for i in range(1):
    rnd.append(random.uniform(0, 1))
  rnd[0] = 0.5
  [vertices, face] = ply.parse_PLY()
  T_list = []
  for i in range(len(face)):
    v0 = vertices[face[i]['index1']]
    v1 = vertices[face[i]['index2']]
    v2 = vertices[face[i]['index3']]
    ambient = (v0[4] + v1[4] + v2[4]) / 3
    t = geo.Triangle(v0[0:3], v1[0:3], v2[0:3])
    t.ambient = ambient
    T_list.append(t)
  t = time.time()
  bvhAccelerator = BVH.BVHTree(T_list)
  print("Construct time", time.time() - t)
  t = time.time()
  for i in range(picture.height):
    for j in range(picture.width):
      color = np.zeros((3,))
      for k in range(len(rnd)):
        #rnd = 0.5
        to = camera.lu + (j / picture.width) * camera.dy + (
            i / picture.height) * camera.dx
        to = to + rnd[k] * (1 / picture.width) * camera.dy + rnd[k] * (
            1 / picture.height) * camera.dx
        r = ray.Ray(camera.position, to)
        color = color + getColor(r, bvhAccelerator, 0)

      for k in range(len(color)):
        color[k] = min(math.floor(color[k] / len(rnd)), 255)

      picture.RGBarray[i * (picture.width * 3) + j * 3 + 0] = color[0]
      picture.RGBarray[i * (picture.width * 3) + j * 3 + 1] = color[1]
      picture.RGBarray[i * (picture.width * 3) + j * 3 + 2] = color[2]

  print("Render time", time.time() - t)
  img_bytes = bytes(picture.RGBarray)
  img = Image.frombytes("RGB", (picture.width, picture.height), img_bytes)
  img.save('output.png')


if __name__ == "__main__":
  main()