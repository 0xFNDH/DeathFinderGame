"""
Objective: Downgrade for simplicity

Client only sends after recieving
Server only sends after recieving
Syncronious

Process:
        1.) Server listen
        2.) Client sends
        3.) Server processes
        4.) Client listen
        5.) Server sends
        6.) Client processs
        ^^  Repeat

"""

import sys, math, time, socket, traceback, string
from dfNPCEngine import DeathFinderNPC
from dfMapRender import MapLoad
from random import randint, choice

def building_pog(x,y,w,l,d="left",i=True):
  build = [(x,y)]
  if i is True:
    inside = square_pog(x+1,y+1,w-1,l-1)
  else:
    inside = []
  door = None

  for X in range(w):
    build.append((X+x,y))
    build.append((X+x,y+l))
  for Y in range(l):
    build.append((x,Y+y))
    build.append((x+w,Y+y))
  build.append((x+w,y+l))

  if d is "left":
    door = (x, int(y+(l/2)))
  elif d is "right":
    door = (x+w, int(y+(l/2)))
  elif d is "top":
    door = (int(x+(w/2)), y)
  elif d is "bottom":
    door = (int(x+(w/2)), y+l)
  elif d is "random":
    door = choice(build)
  if door:
    build.remove(door)
    if i is True:
      inside.append(door)
  return build, door, inside

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

def _decompress(comp):
  comp = comp.replace("3","555").replace("4", "."*4).replace("5"," "*5).replace(";"," ").replace("6","#"*6).replace("!n","\n")
  return comp

def distance(p1, p2):
  return math.sqrt(((p2[0]-p1[0])**2) + ((p2[1]-p1[1])**2))

def IV(data, true_false=False, limit=600):
  """
  Input Validation - Returns sanitized data.
  true_false - Instead of returning data, this returns True or False depending on if the data is clean.
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

    assert type(width) is int
    assert type(height) is int
    assert len(multicast) is 3
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
    self.tempwalls = []
    self.dark = []
    self.loot = [(2,83),(5,5),(5,6),(5,7),(5,8)]
    self.ascii = ".&+@#:;?"

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
    everyspot = []
    for user in self.players:
      if user != username:
        everyspot.append(self.players[user].get("pos"))
    return everyspot

  def mapload_optimizer(self, depth):
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
      _rwall, _rdark, _rspawn = MapLoad(ymin=self.yminrender, ymax=self.ymaxrender)

      for solid in _rwall:
        if solid not in self.bricks:
          self.bricks.append(solid)

      for dark in _rdark:
        if dark not in self.dark:
          self.dark.append(dark)

      for spawn in _rspawn:
        monster = self.npc_manager.randomMonster(spawn[1])
        self.npc_manager.spawnMonster(monster[0], monster[1], monster[2], spawn)

      del _rwall
      del _rdark
      del _rspawn

  def all_solids(self):
    objects = []
    objects.append(self.everyone_but("___"))
    objects.append(self.bricks)
    objects.append(self.magicwalls)
    objects.append(self.npc_manager.allnpc_but("___"))
    return objects

  def ObtainLoot(self, user):
    if user in list(self.players.keys()):
      # E : Amulet of ESP
      # S : Book of Magic Shield
      # R : Amulet of Reflection
      # J : Jumping Boots
      # H : Book of Healing
      loot = choice("ESRJH")

      if loot is "E":
        self.ESP.append(user)
        print("[?] %s obtained an Amulet of ESP"%(user), file=sys.stderr)
      elif loot is "S":
        self.SPELLWALL.append(user)
        print("[?] %s obtained a Book of Magic Shield"%(user), file=sys.stderr)
      elif loot is "R":
        self.REFLECTION.append(user)
        print("[?] %s obtained an Amulet of Reflection"%(user), file=sys.stderr)
      elif loot is "J":
        self.JUMPBOOT.append(user)
        print("[?] %s obtained Jumping Boots"%(user), file=sys.stderr)
      elif loot is "H":
        self.HEALING.append(user)
        print("[?] %s obtained a Book of Healing"%(user), file=sys.stderr)

      # Random chance to spawn a mimic
      if randint(1,15) == 9:
        self.npc_manager.spawnMonster("?MimicO", 15, 1, self.players[user].get("pos"), moveset="wasd")

  def EventUpdate(self):
    """
    depth and entity events
    """
    depth = 0
    playerlocations = self.everyone_but("___")
    for dep in playerlocations:
      if dep[1] > depth:
        depth = dep[1]
      if dep in self.loot:
        for user in self.players:
          if self.players[user].get("pos") == dep:
            self.ObtainLoot(user)
            self.loot.remove(dep)
            break

    if len(self.tempwalls) > 0:
      rmt = []
      for magicw in self.tempwalls:
        if magicw[0] < self.epoch:
          for pos in magicw[1]:
            self.magicwalls.remove(pos)
          rmt.append(magicw)
      if len(rmt) > 0:
        for holder in rmt:
          self.tempwalls.remove(holder)

    self.mapload_optimizer(depth)

    dead = []
    for user in list(self.players.keys()):
      if self.players[user]["status"] < 0:
        dead.append(user)
    if len(dead) > 0:
      for user in dead:
        if user in list(self.players.keys()):
          self.players.pop(user)

  def Render(self, user):

    if user in list(self.players.keys()):
      userx = self.players[user]["pos"][0]
      usery = self.players[user]["pos"][1]
      pos = self.players[user]["pos"]
      lit = pos in self.dark
      _players = self.everyone_but(user)
      _NPC = self.npc_manager.showNPCs()
      visability = self.visible
      if usery > 35:
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
              elif (x,y) in self.dark and lit is False:
                view += ";"
              elif (x,y) in _players:
                view += "&"
              elif (x,y) in list(_NPC.keys()):
                view += _NPC.get((x,y))
                __character = _NPC.get((x,y))
                if __character != None and __character not in self.ascii:
                  self.ascii += __character
              elif (x,y) in self.magicwalls:
                view += ":"
              elif (x,y) in self.loot:
                view += "?"
              elif (x,y) in self.walls:
                view += "#"
              else:
                view += "."
          elif user in self.ESP and (x,y) in list(_NPC.keys()):
            view += _NPC.get((x,y))
            __character = _NPC.get((x,y))
            if __character != None and __character not in self.ascii:
              self.ascii += __character
          else:
            view += " "

        view += "\n"
        if any(sst in view for sst in self.ascii) == False:
          view = "\n"
        elif view.startswith(" ") == False:
          view = view.replace("  ", "").replace(". ", ".")
        omni_view += view
        view = ""

      omni_view = omni_view.replace(" "*5, "5").replace("\n\n\n","\n").replace("."*4, "4").replace("5"*3,"3").replace("#"*6, "6").replace("\n","!n")
      return omni_view
    else:
      return "User not in list of players"

  def que_data(self, user, data):
    """
    This function ques the player data
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
    USER: name, (x,y), status, epoch\n
    ....@....!n
    """
    becon = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    becon.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
    becon_addr = (self.multicast, self.mport_out)
    for username in self.player_que:
      hp = self.players[username].get("status")
      xp = round(self.players[username].get("xp"),2)
      pos = str(self.players[username].get("pos")).replace(" ","")
      inv = self.inventoryPlayer(username)
      packet = "USER: %s %s HP:%s XP:%s IV:%s E:%s\n"%(username, pos, hp, xp, inv, self.epoch)
      packet += self.Render(username)
      becon.sendto(packet.encode(), becon_addr)
    becon.close()

  def NextEpoch(self):
    """
    If you dont iterate through players twice the first player cant see the last player's move
    """
    self.UpdatePlayers()
    self.epoch += 1
    self.walls = self.bricks + self.magicwalls

    for user in self.players:
      _rlwalls = self.everyone_but(user)
      _rlwalls += self.npc_manager.allnpc_but("___")
      x,y = self.players[user]["pos"]
      status = self.players[user]["status"]
      action = self.players[user]["action"][:1]

      # E : Amulet of ESP
      # S : Book of Magic Shield
      # R : Amulet of Reflection
      # J : Jumping Boots
      # H : Book of Healing
      if action == "!":
        action = self.players[user]["action"][:3]

        if user in self.SPELLWALL and action.upper() == "!S":
          barrier = circle_pog(x,y,3)
          self.magicwalls += barrier
          self.walls += barrier
          self.tempwalls.append([self.epoch+5, barrier])
          print("[*] %s read the Book of Magic Shield"%(user), file=sys.stderr)

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
              print("[*] %s jumped very far"%(user), file=sys.stderr)

        elif user in self.HEALING and action.upper() == "!H":
          # todo: trade xp for hp
          for _pl in self.players:
            self.players[_pl]["status"] += choice([0,0.5,0.5,1])

      elif action in "wasd":
        if action == "w":
          if (y-1 < 0) or ((x, y-1) in self.walls+_rlwalls):
            pass
          else:
            y -= 1
        elif action == "s":
          if (y+1 >= self.height) or ((x, y+1) in self.walls+_rlwalls):
            pass
          else:
            y += 1
        elif action == "d":
          if (x + 1 >= self.width) or ((x+1, y) in self.walls+_rlwalls):
            pass
          else:
            x += 1
        elif action == "a":
          if (x - 1 < 0) or ((x-1, y) in self.walls+_rlwalls):
            pass
          else:
            x -= 1

        self.players[user]["pos"] = (x,y)
        # if player casts, send data to class 3
        # set action to " " and loop back again to unionize the visual field. the first player doesn't see the last players movment
        # list(players.keys) + list(players.keys)[:-1]

    for monster in self.npc_manager.ENEMY:
      _rlwalls = self.npc_manager.allnpc_but(monster)
      _rlwalls += self.everyone_but("___")
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
          if (y-1 < 0) or ((x, y-1) in self.walls+_rlwalls):
            pass
          else:
            y -= 1
        elif action == "s":
          if (y+1 >= self.height) or ((x, y+1) in self.walls+_rlwalls):
            pass
          else:
            y += 1
        elif action == "d":
          if (x + 1 >= self.width) or ((x+1, y) in self.walls+_rlwalls):
            pass
          else:
            x += 1
        elif action == "a":
          if (x - 1 < 0) or ((x-1, y) in self.walls+_rlwalls):
            pass
          else:
            x -= 1

        self.npc_manager.ENEMY[monster]["pos"] = (x,y)

    for npc in self.npc_manager.NPC:
      _rlwalls = self.npc_manager.allnpc_but(npc)
      _rlwalls += self.everyone_but("___")
      x,y = self.npc_manager.NPC[npc]["pos"]
      size = self.npc_manager.NPC[npc]["size"]
      actionopt = self.npc_manager.NPC[npc]["moveset"]
      actionopt += "."*size
      action = choice(actionopt)

      if action in "wasd":
        if action == "w":
          if (y-1 < 0) or ((x, y-1) in self.walls+_rlwalls):
            pass
          else:
            y -= 1
        elif action == "s":
          if (y+1 >= self.height) or ((x, y+1) in self.walls+_rlwalls):
            pass
          else:
            y += 1
        elif action == "d":
          if (x + 1 >= self.width) or ((x+1, y) in self.walls+_rlwalls):
            pass
          else:
            x += 1
        elif action == "a":
          if (x - 1 < 0) or ((x-1, y) in self.walls+_rlwalls):
            pass
          else:
            x -= 1

        self.npc_manager.NPC[npc]["pos"] = (x,y)

    for user in self.players:
      position = self.players[user]["pos"]
      damage = 2
      damage += int(self.players[user]["xp"])
      hplost, xpgain = self.npc_manager.inflict(position,damage)
      _hp = self.players[user]["status"]
      hplost -= choice(([0]*6)+[0.5])
      self.players[user]["status"] -= hplost
      self.players[user]["xp"] += xpgain
      if xpgain > 0.01:
        print("[%s] Hp(%s)-%s XP+%s "%(user, _hp, hplost, xpgain), file=sys.stderr)

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

    assert len(multicast) is 2

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
  MCAST_GRP = "224.0.0.251"

  recieving = 15003
  sending   = 15002
  Game = DeathFinder(40,200, (MCAST_GRP, sending, recieving), address, wait=0.5)

  build = building_pog(30,2,6,4,"left")
  Game.bricks += build[0]
  Game.doors.append(build[1])
  Game.dark += build[2]

  while True:
    sys.stdout.write("[+] Epoch %s\n"%str(Game.epoch+1))
    Game.NextEpoch()

  Game.manager.ingress.close()
