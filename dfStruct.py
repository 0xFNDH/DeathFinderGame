import math
from random import randint, choice

def building_pog(x,y,w,l,d="left",inside=True):
  build = [(x,y)]
  if inside == True:
    inside = square_pog(x+1,y+1,w-1,l-1)
  else:
    inside = []

  for X in range(w):
    build.append((X+x,y))
    build.append((X+x,y+l))
  for Y in range(l):
    build.append((x,Y+y))
    build.append((x+w,Y+y))
  build.append((x+w,y+l))
  
  door = []
  if d != None:
    if d == "left":
      door = (x, int(y+(l/2)))
    elif d == "right":
      door = (x+w, int(y+(l/2)))
    elif d == "top":
      door = (int(x+(w/2)), y)
    elif d == "bottom":
      door = (int(x+(w/2)), y+l)
    elif d == "random":
     door = choice(build)
    build.remove(door)
    inside.append(door)
  
  newbuild = []
  for b in build:
    if b not in newbuild:
      newbuild.append(b)
  
  return newbuild, door, inside

def circle_pog(x,y,r):
  circle = []
  for locx in range(x-(r*2),x+(r*2)):
    for locy in range(y-(r*2),y+(r*2)):
      radi = math.sqrt(((x-locx)**2) + ((y-locy)**2))
      if radi < r:
        circle.append((locx,locy))
  for locx in range(x-(r*2),x+(r*2)):
    for locy in range(y-(r*2),y+(r*2)):
      radi = math.sqrt(((x-locx)**2) + ((y-locy)**2))
      if radi < r-1:
        circle.remove((locx,locy))
  return circle

def magicwall_pog(y,w):
  magicwall = []
  for x in range(0,w+1):
    magicwall.append((x,y))
  return magicwall

def square_pog(x,y,w,l):
  block = []
  for X in range(w):
    for Y in range(l):
      block.append((x+X,y+Y))
  return block
