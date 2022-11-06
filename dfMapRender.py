

def dfMapLoad(mapfile="blight_map.txt", ymin=0, ymax=100, width=40):
  mapfile = open(mapfile,"r")
  map_data = mapfile.read().split("\n")[ymin:ymax]
  mapfile.close()

  dfWall = []
  dfDark = []
  dfSpawn = []
  dfBranch = []
  dfBush = []
  dfMound = []
  dfWater = []
  dfLeaf = []

  width = width # dfGameHost Map Size
  y = ymin # Starting Y-Depth
  x = 0

  for line in map_data:
    for char in line[:width]:
      if char == ".":
        pass

      elif char == "#":
        dfWall.append((x,y))
      elif char == ";":
        dfDark.append((x,y))
      elif char == "%":
        dfSpawn.append((x,y))

      elif char == "*":
        dfBush.append((x,y))
      elif char == "=":
        dfBranch.append((x,y))
      elif char == ",":
        dfLeaf.append((x,y))
      elif char == ":":
        dfMound.append((x,y))
      elif char == "^":
        dfWater.append((x,y))

      x += 1
    y += 1
    x = 0

  return dfWall, dfDark, dfSpawn, [dfBush, dfBranch, dfMound, dfWater, dfLeaf]
