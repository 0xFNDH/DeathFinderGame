def MapLoad(mapfile="map_DONOTEDIT.txt", ymin=0, ymax=100):
  mapfile = open(mapfile,"r")
  map_data = mapfile.read().split("\n")[ymin:ymax]
  mapfile.close()

  dfWall = []
  dfDark = []
  dfSpawn = []
  width = 40 # dfGameHost Map Size
  y = ymin # Starting Y-Depth
  x = 0

  for line in map_data:
    for char in line:
      if char == "#":
        dfWall.append((x,y))
      elif char == ".":
        pass
      elif char == ";":
        dfDark.append((x,y))
      elif char == "%":
        dfSpawn.append((x,y))
      x += 1
    y += 1
    x = 0

  return dfWall, dfDark, dfSpawn

def dfMapPreview(dfWall, dfDark, dfSpawn):
  view = ""
  for y in range(30,168):
    for x in range(40):
      if (x,y) in dfWall:
        view += "#"
      elif (x,y) in dfDark:
        view += ";"
      elif (x,y) in dfSpawn:
        view += "%"
      else:
        view += "."
      if x == 39 and (y/5).is_integer():
        view += " %s"%(y)
    view += "\n"

  print(view)
