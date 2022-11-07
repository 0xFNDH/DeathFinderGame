"""
Death Finder
"""

import sys, math, time, socket, traceback, string
from dfNPCEngine import DeathFinderNPC
from dfMapRender import dfMapLoad
from dfStruct import *
from random import randint, choice

def _decompress(comp):
  """
  Map data is compressed before being sent out of the network to save space.
  This function decompresses compressed data back to the display state (NOT the original state).
  """
  comp = comp.replace("3","555").replace("4", "."*4).replace("5"," "*5).replace(";"," ").replace("6","#"*6).replace("!n","\n")
  return comp

def distance(p1, p2):
  """
  Remember that stuff you forgot in high school math class? That's what this is.
  """
  return math.sqrt(((p2[0]-p1[0])**2) + ((p2[1]-p1[1])**2))

def IV(data, true_false=False, limit=600):
  """
  IV sanitizes strings from client inputs.
  Enableing 'true_false' will return True if the string clean.
  """
  assert type(true_false) == bool
  data = str(data)[:limit]
  _cleaned = ""
  for char in data:
    if char not in string.ascii_letters + string.digits + "!":
      if true_false:
        return False
    else:
      _cleaned += char
  if true_false:
    return True
  else:
    return _cleaned

class DeathFinder():

  def __init__(self, width, height, multicast, address, wait=5.0):

    assert type(width) == int
    assert type(height) == int
    assert len(multicast) == 3
    assert type(wait) in [int,float]

    self.width = width
    self.height = height
    self.player_que = []
    self.player_que_data = []
    self.player_ips = {}
    self.epoch = 0
    self.visible = 9
    self.players = {
      "DeathFinder": {
        "pos":  (1,2),
        "status": 10,
        "action": " ",
        "xp": 0.0},
      "Admin": {
        "pos":  (4,4),
        "status": 10,
        "action": " ",
        "xp": 0.0}
    }
    self.walls = []
    self.doors = []
    self.bricks = []
    self.magicwalls = []
    self.MAGICWALL = []
    self.dark = []
    self.dfBranch = []
    self.dfBush = []
    self.dfMound = []
    self.dfWater = []
    self.dfLeaf = []
    
    self.paralysis = []
    self.waterlogged = []
    self.loot = [(2,82),(33,4),(34,4),(5,5),(5,6),(5,7),(5,8)]

    self.ESP = ["Admin"]
    self.SPELLWALL = []
    self.REFLECTION = [] # todo: chance 50%
    self.HEALING = []
    self.JUMPBOOT = []

    self.yminrender = None
    self.ymaxrender = None
    self.wait = wait
    self.address = address
    self.multicast = multicast[0]
    self.mport_out = multicast[1]
    self.mport_in = multicast[2]
    self.manager = BroadcastServer((self.multicast, self.mport_in), self.address, wait_time=wait)
    self.npc_manager = DeathFinderNPC()

  def everyone_but(self, username):
    """
    Returns all the player locations except the specified player.
    """
    everyspot = []
    for user in self.players:
      if user != username:
        everyspot.append(self.players[user].get("pos"))
    return everyspot

  def mapload_optimizer(self, depth):
    """
    This function loads the map in chunks to save/optimize memory.
    """
    rerender = False
    chunks = [40,80,120,160,200,240,280,320]

    if self.ymaxrender == None:
      self.ymaxrender = 40
      self.yminrender = 0
      rerender = True
    elif (depth + self.visible + 5) >= self.ymaxrender:
      self.yminrender = self.ymaxrender
      self.ymaxrender = chunks[chunks.index(self.ymaxrender)+1]
      rerender = True
    
    if rerender == True:
      print("[M] Rendering Map from File %s:%s\n"%(self.yminrender, self.ymaxrender), file=sys.stderr)
      _rwall, _rdark, _rspawn, _rdoor, _rloot, _rmix = dfMapLoad(ymin=self.yminrender, ymax=self.ymaxrender)
      
      for solid in _rwall:
        if solid not in self.bricks:
          self.bricks.append(solid)
      
      for dark in _rdark:
        if dark not in self.dark:
          self.dark.append(dark)
      
      for spawn in _rspawn:
        monster = self.npc_manager.randomMonster(spawn[1])
        self.npc_manager.spawnMonster(monster[0], monster[1], monster[2], spawn)
      
      self.dfBush += _rmix[0]
      self.dfBranch += _rmix[1]
      self.dfMound += _rmix[2]
      self.dfWater += _rmix[3]
      self.dfLeaf += _rmix[4]
      self.loot += _rloot
      
      del _rwall
      del _rdark
      del _rspawn

  def all_solids(self, allow="___"):
    """
    Lists all the solid objects that regular characters cannot walk through.
    """
    objects = []
    objects.append(self.everyone_but(allow))
    objects.append(self.bricks)
    objects.append(self.magicwalls)
    objects.append(self.npc_manager.allnpc_but(allow))
    return objects
  
  def getAfflictions(self, user):
    """
    Returns the negative status effects that are applied to specific players.
    """
    afflicted = ""
    if user in list(self.players.keys()):
      if user in self.paralysis:
        afflicted += "P"
      elif user in self.waterlogged:
        afflicted += "W"
      
    return afflicted
  
  def ObtainLoot(self, user):
    """
    Players that find loot will be given a random skill/ability/magic item.
    Three items will be given at max and finding a loot has a 1/15 chance to spawn a mimic.
    """
    if user in list(self.players.keys()):
      # E : Amulet of ESP
      # S : Book of Magic Shield
      # R : Amulet of Reflection
      # J : Jumping Boots
      # H : Book of Healing
      loot = choice("".join(set("ESRJH").difference(self.inventoryPlayer(user))))

      if loot == "E":
        self.ESP.append(user)
        print("[?] %s obtained an Amulet of ESP"%(user), file=sys.stderr)
      elif loot == "S":
        self.SPELLWALL.append(user)
        print("[?] %s obtained a Book of Magic Shield"%(user), file=sys.stderr)
      elif loot == "R":
        self.REFLECTION.append(user)
        print("[?] %s obtained an Amulet of Reflection"%(user), file=sys.stderr)
      elif loot == "J":
        self.JUMPBOOT.append(user)
        print("[?] %s obtained Jumping Boots"%(user), file=sys.stderr)
      elif loot == "H":
        self.HEALING.append(user)
        print("[?] %s obtained a Book of Healing"%(user), file=sys.stderr)

      if randint(1,15) == 1 and len(loot) > 0:
        self.npc_manager.spawnMonster("?MimicO", 15, 1, self.players[user].get("pos"), moveset="wasd")

  def EventUpdate(self):
    """
    This creates the sequence of events that occur each epoch.
    Loot is limited to three items and map optimization is checked.
    Depth is the most important aspect of EventUpdate as the Y-Axis determines when events occur.
    """
    depth = 0
    playerlocations = self.everyone_but("___")
    for dep in playerlocations:
      if dep[1] > depth:
        depth = dep[1]
      
      if dep in self.loot:
        for user in self.players:
          if self.players[user].get("pos") == dep and len(self.inventoryPlayer(user)) < 3:
            self.ObtainLoot(user)
            self.loot.remove(dep)
            break

    if len(self.MAGICWALL) > 0:
      rmt = []
      for magicw in self.MAGICWALL:
        if magicw[0] < self.epoch:
          for pos in magicw[1]:
            self.magicwalls.remove(pos)
          rmt.append(magicw)
      if len(rmt) > 0:
        for holder in rmt:
          self.MAGICWALL.remove(holder)

    self.mapload_optimizer(depth)

    dead = []
    for user in list(self.players.keys()):
      if self.players[user]["status"] < 0:
        dead.append(user)
    if len(dead) > 0:
      for user in dead:
        if user in list(self.players.keys()):
          self.players.pop(user)
          if self.ESP.count(user) > 0:
            self.ESP.remove(user)
          if self.HEALING.count(user) > 0:
            self.HEALING.remove(user)
          if self.JUMPBOOT.count(user) > 0:
            self.JUMPBOOT.remove(user)
          if self.SPELLWALL.count(user) > 0:
            self.SPELLWALL.remove(user)
          if self.REFLECTION.count(user) > 0:
            self.REFLECTION.remove(user)

  def Render(self, user):
    """
    Too much to explain here. This fucntion renders all the visual content for each player.
    This function could use more optimization.
    """

    if user in list(self.players.keys()):
      userx = self.players[user]["pos"][0]
      usery = self.players[user]["pos"][1]
      pos = self.players[user]["pos"]
      lit = pos in self.dark
      _players = self.everyone_but(user)
      _NPC = self.npc_manager.showNPCs()
      visability = self.visible
      if 155 > usery > 35:
        visability = 6
      view = ""
      omni_view = ""
      min_y, max_y = 0,0
      if usery-(visability+2) >= 0:
        min_y = usery-(visability+2)
      if usery+(visability+2) > self.height:
        max_y = self.height
      else:
        max_y = usery+(visability+2)

      for y in range(min_y, max_y):
        for x in range(0, self.width):
          if math.sqrt(((x-userx)**2) + ((y-usery)**2)) < visability:
            if (x,y) == pos:
              view += "@"
            else:
              if (x,y) in self.doors:
                view += "+"
              elif (x,y) in self.dark and lit == False:
                view += ";"
              elif (x,y) in _players:
                view += "&"
              elif (x,y) in list(_NPC.keys()):
                view += _NPC.get((x,y))
              elif (x,y) in self.magicwalls:
                view += ":"
              elif (x,y) in self.loot:
                view += "?"
              elif (x,y) in self.paralysis:
                view += ","
              elif (x,y) in self.walls:
                view += "#"
              else:
                view += "."
        view = view.rstrip() + "\n"
        omni_view += view
        view = ""

      omni_view = omni_view.replace(" "*5, "5").replace("\n\n\n","\n").replace("."*4, "4").replace("5"*3,"3").replace("#"*6, "6").replace("\n","!n")
      return omni_view
    else:
      return "User not in list of players"

  def que_data(self, user, data):
    """
    Client data recieved over the network is put into a list to be accessed when the next epoch occurs.
    """
    if user in list(self.players.keys()):
      if user not in self.player_que:
        temp = self.players[user]
        temp.update(data)
        self.player_que_data.append({user:temp})
        self.player_que.append(user)
        del temp

    elif (len(self.players.keys()) < 15) and IV(user, True):
      spawnpoint = (randint(2, self.width-2), randint(2, 5))
      while spawnpoint in self.all_solids():
        spawnpoint = (randint(2, self.width-2), randint(2, 5))
      self.players.update({user:{
        "pos":  spawnpoint,
        "status": 10,
        "action": " ",
        "xp": 0.0}})
      self.player_que.append(user)
    else:
      print("[!] Max Player Limit", file=sys.stderr)

  def UpdatePlayers(self):
    for user in self.player_que_data:
      self.players.update(user)

  def inventoryPlayer(self, user):
    """
    Returns the inventory of any given player.
    """
    inv = ""
    if user in (self.HEALING + self.JUMPBOOT + self.ESP + self.REFLECTION + self.SPELLWALL):
      if user in self.HEALING:
        inv += "H"
      if user in self.JUMPBOOT:
        inv += "J"
      if user in self.ESP:
        inv += "E"
      if user in self.REFLECTION:
        inv += "R"
      if user in self.SPELLWALL:
        inv += "S"
    return inv

  def BroadcastUpdate(self):
    """
    Multicast socket for pushing out player data over the network.
    USER: Username (x,y) HP:10 XP:0.0 IV:None E:1 A:None
    ..###..#!n....@....!n........!n
    """
    becon = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    becon.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
    becon_addr = (self.multicast, self.mport_out)
    for username in self.player_que:
      hp = self.players[username].get("status")
      xp = round(self.players[username].get("xp"),2)
      pos = str(self.players[username].get("pos")).replace(" ","")
      inv = self.inventoryPlayer(username)
      afflict = self.getAfflictions(username)
      packet = "USER: %s %s HP:%s XP:%s IV:%s E:%s A:%s\n"%(username, pos, hp, xp, inv, self.epoch, afflict)
      packet += self.Render(username)
      becon.sendto(packet.encode(), becon_addr)
    becon.close()

  def NextEpoch(self):
    """
    Everything.
    """
    self.UpdatePlayers()
    self.epoch += 1

    for user in self.players:
      allsolids = self.all_solids(user)
      x,y = self.players[user]["pos"]
      status = self.players[user]["status"]
      action = self.players[user]["action"][:1]
      
      if (x,y) in self.paralysis:
        action = " "
      
      # E : Amulet of ESP
      # S : Book of Magic Shield
      # R : Amulet of Reflection
      # J : Jumping Boots
      # H : Book of Healing
      if action == "!":
        action = self.players[user]["action"][:3]

        if user in self.SPELLWALL and action[:2].upper() == "!S":
          barrier = circle_pog(x,y,3)
          self.magicwalls += barrier
          self.walls += barrier
          self.MAGICWALL.append([self.epoch+5, barrier])
          print("[*] %s reads the Book of Magic Shield"%(user), file=sys.stderr)

        elif user in self.JUMPBOOT and action.upper().startswith("!J"):
          moveopt = {
            "!JW":(x,y-2),
            "!JS":(x,y+2),
            "!JD":(x+2,y),
            "!JA":(x-2,y),
            "!JE":(x+2,y-2),
            "!JQ":(x-2,y-2),
            "!JZ":(x-2,y+2),
            "!JC":(x+2,y+2)
          }
          if action.upper() in list(moveopt.keys()):
            if moveopt[action.upper()] not in (self.walls + _rlwalls):
              self.players[user]["pos"] = moveopt[action.upper()]

        elif user in self.HEALING and action[:2].upper() == "!H":
          # todo: trade xp for hp
          for _pl in self.players:
            if self.players[_pl]["status"] <= 15:
              self.players[_pl]["status"] += choice([0,1,1,1.5,2])
              self.players[user]["xp"] -= 0.04

      elif action in "wasd":
        if action == "w":
          if (y-1 < 0) or ((x, y-1) in allsolids):
            pass
          else:
            y -= 1
        elif action == "s":
          if (y+1 >= self.height) or ((x, y+1) in allsolids):
            pass
          else:
            y += 1
        elif action == "d":
          if (x + 1 >= self.width) or ((x+1, y) in allsolids):
            pass
          else:
            x += 1
        elif action == "a":
          if (x - 1 < 0) or ((x-1, y) in allsolids):
            pass
          else:
            x -= 1

        self.players[user]["pos"] = (x,y)

    for monster in self.npc_manager.ENEMY:
      allsolids = self.all_solids(monster)
      x,y = self.npc_manager.ENEMY[monster]["pos"]
      size = self.npc_manager.ENEMY[monster]["size"]
      actionopt = self.npc_manager.ENEMY[monster]["moveset"]
      actionopt += "."*size
      if actionopt.count(".") >= 10:
        action = " "
      else:
        action = choice(actionopt)

      if action in "wasd":
        if action == "w":
          if (y-1 < 0) or ((x, y-1) in allsolids):
            pass
          else:
            y -= 1
        elif action == "s":
          if (y+1 >= self.height) or ((x, y+1) in allsolids):
            pass
          else:
            y += 1
        elif action == "d":
          if (x + 1 >= self.width) or ((x+1, y) in allsolids):
            pass
          else:
            x += 1
        elif action == "a":
          if (x - 1 < 0) or ((x-1, y) in allsolids):
            pass
          else:
            x -= 1

        self.npc_manager.ENEMY[monster]["pos"] = (x,y)

    for npc in self.npc_manager.NPC:
      allsolids = self.all_solids(monster)
      x,y = self.npc_manager.NPC[npc]["pos"]
      size = self.npc_manager.NPC[npc]["size"]
      actionopt = self.npc_manager.NPC[npc]["moveset"]
      actionopt += "."*size
      action = choice(actionopt)
      
      if npc == "!JaviHydor" and action != ".":
        _old_ = building_pog(x-1,y-1,2,2,None,False)[0]
        for o in _old_:
          if o in self.paralysis:
            self.paralysis.remove(o)

      if action in "wasd":
        if action == "w":
          if (y-1 < 0) or ((x, y-1) in allsolids):
            pass
          else:
            y -= 1
        elif action == "s":
          if (y+1 >= self.height) or ((x, y+1) in allsolids):
            pass
          else:
            y += 1
        elif action == "d":
          if (x + 1 >= self.width) or ((x+1, y) in allsolids):
            pass
          else:
            x += 1
        elif action == "a":
          if (x - 1 < 0) or ((x-1, y) in allsolids):
            pass
          else:
            x -= 1
        
        if npc == "!JaviHydor":
          self.paralysis += building_pog(x-1,y-1,2,2,None,False)[0]
        
        self.npc_manager.NPC[npc]["pos"] = (x,y)

    for user in self.players:
      position = self.players[user]["pos"]
      damage = 2
      damage += int(self.players[user]["xp"])
      hplost, xpgain = self.npc_manager.inflict(position,damage)
      _hp = self.players[user]["status"]
      if self.players[user]["status"] <= 15.0:
        hplost -= choice(([0]*10)+[0.5])
        if user in self.REFLECTION and randint(0,1) == 1:
          self.npc_manager.inflict(position,damage)
        else:
          self.players[user]["status"] -= hplost
      self.players[user]["xp"] += xpgain
      if xpgain > 0.01:
        print("[%s] Hp(%s)-%s XP+%s "%(user, round(_hp,3), hplost, xpgain), file=sys.stderr)

    self.BroadcastUpdate()
    self.player_que = []
    self.player_que_data = []
    self.manager.epoch = self.epoch
    self.EventUpdate()
    self.BroadcastListen()

  def BroadcastListen(self):
    qued = []
    while len(str(qued)) < 5:
      qued = self.manager.listen()
      time.sleep(0.1)
    for diction in qued:
      user = list(diction.keys())[0]
      self.que_data(user, diction[user])

class BroadcastServer():

  def __init__(self, multicast, address, wait_time=5.0, _epoch=0, log_buffer=sys.stderr, logging=True):

    assert len(multicast) == 2

    self.multicast = multicast
    self.address = address
    self._epoch = _epoch
    self.logging = logging
    self.wait_time = wait_time
    self.logs = {}
    self.player_data = []
    self.MCAST_GRP = multicast[0]
    self.MCAST_PORT = multicast[1]

    self.ingress = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    try:
      self.ingress.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except AttributeError:
      pass
    self.ingress.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
    self.ingress.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

    self.ingress.bind((self.MCAST_GRP, self.MCAST_PORT))
    self.ingress.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.address))
    self.ingress.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP,
    socket.inet_aton(self.MCAST_GRP) + socket.inet_aton(self.address))
    self.ingress.settimeout(self.wait_time)

    print("Death Finder Server Listening %s:%s"%(multicast[0], multicast[1]), file=log_buffer)

  @property
  def epoch(self):
    return self._epoch

  @epoch.setter
  def epoch(self, value):
    self.player_data = []
    self._epoch = value

  def listen(self):

    wait_time = self.wait_time
    wait_time = round(wait_time/.95,4) # 5% lag
    wait_time = time.time()+wait_time

    all_addr = []

    if True: #try:
      while time.time() < wait_time:
        try:
          clientdata, addr = self.ingress.recvfrom(50)
          clientdata = clientdata.decode()
          if addr[0] not in all_addr and clientdata.startswith("USER:"):
            self.player_data.append([addr[0], clientdata])
            all_addr.append(addr[0])
            print("[%s] %s"%(addr[0] ,clientdata[:20]), file=sys.stderr)
        except Exception as e:
          pass
    return self.process()

  def process(self):
    """
    USER: name, action
    """
    processed_data = []
    for data in self.player_data:
      packet = data[1].replace(",","")
      username = IV(packet.split(" ")[1], limit=12)
      if 13 > len(username) > 3:
        action = IV(packet.split(" ")[-1])
        processed_data.append({username:{"action":action}})
    return processed_data

def getLANIP():
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  try:
    s.connect(("255.255.255.255", 1))
    IP = s.getsockname()[0]
  except Exception:
    IP = "127.0.0.1"
  finally:
    s.close()
  return IP

if __name__ == "__main__":
  address = getLANIP()
  MCAST_GRP = "224.0.0.1"

  recieving = 15003
  sending   = 15002
  Game = DeathFinder(40,305, (MCAST_GRP, sending, recieving), address, wait=0.5)

  build = building_pog(30,2,6,4,"left")
  Game.bricks += build[0]
  Game.doors.append(build[1])
  Game.dark += build[2]

  while True:
    sys.stdout.write("[+] Epoch %s\n"%str(Game.epoch+1))
    Game.NextEpoch()

  Game.manager.ingress.close()
