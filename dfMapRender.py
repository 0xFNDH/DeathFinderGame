
def dfMapLoad(mapfile="blight_map.txt", ymin=0, ymax=100, width=40):
  """
  Elements added here will spawn into the map upon launch\
  """
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
  dfDoor = []
  dfLoot = []

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

      elif char == "+":
        dfDoor.append((x,y))
        dfDark.append((x,y))
      elif char == "?":
        dfDark.append((x,y))
        dfLoot.append((x,y))

      x += 1
    y += 1
    x = 0

  return dfWall, dfDark, dfSpawn, dfDoor, dfLoot, [dfBush, dfBranch, dfMound, dfWater, dfLeaf]
