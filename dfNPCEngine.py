from random import choice
import sys, time, string

class DeathFinderNPC():

  def __init__(self):
    self.NPC = {
      "Jacob":{
        "pos":(11,65),
        "moveset":".",
        "size":2
        },
      "!JaviHydor":{
        "pos":(11,75),
        "moveset":"wasd",
        "size":5
      },
      "JimJim":{
        "pos":(8,82),
        "moveset":"wasd",
        "size":6
      }
    }
    self.ENEMY = {
      "goblin":{
         "pos":(5,35),
         "moveset":"ad",
         "size":1,
         "hp":5
         },
    }

  def damagefield(self, mran=None):
    """
    Setting mran will return the enemy that owns that damage zone.
    If mran is not set it will just return all the spots that deal damage.
    """
    if mran == None:
      zones = []
      for enemy in self.ENEMY:
        x,y = self.ENEMY[enemy]["pos"]
        zones.append((x,y))
        zones.append((x,y+1))
        zones.append((x,y-1))
        zones.append((x+1,y))
        zones.append((x-1,y))
      return zones
    
    mon = []
    if type(mran) == tuple:
      for enemy in self.ENEMY:
        x,y = self.ENEMY[enemy]["pos"]
        zones = []
        zones.append((x,y))
        zones.append((x,y+1))
        zones.append((x,y-1))
        zones.append((x+1,y))
        zones.append((x-1,y))
        if mran in zones and enemy not in mon:
          mon.append(enemy)
      return mon

  def enemypositions(self):
    pos = []
    for enemy in self.ENEMY:
      pos.append(self.ENEMY[enemy].get("pos"))
    return pos

  def allnpc_but(self, name):
    everyspot = []
    for mobname in self.ENEMY:
      if mobname != name:
        everyspot.append(self.ENEMY[mobname].get("pos"))
    for npcname in self.NPC:
      if npcname != name:
        everyspot.append(self.NPC[npcname].get("pos"))
    return everyspot

  def getenemyfrompos(self, pos):
    for enemy in self.ENEMY:
      if self.ENEMY[enemy].get("pos") == pos:
        return enemy
    return None

  def randomMonster(self, depth):
    easy   = ["goblin", "goblin", "goblin", "goblin", "spider", "orc", "orc", "rat", "blobTar", "nymph"]
    medium = ["Snake", "GoblinHog", "Kobold", "GoblinHog", "qsucubus", "?mimic", "Pudding"]
    hard   = ["#StoneGolumn", "?Mimic", "Basilisk", "Lich", "ArchAngel", "Naga"]
    ohio   = ["Wyvern", "Dragon", "demonPrince"]
    if depth < 80:
      monster = choice(easy)
    elif depth < 100:
      monster = choice(easy+medium)
    elif depth < 130:
      monster = choice(easy+medium+hard)
    elif depth < 160:
      monster = choice(medium+hard)
    elif depth == 999:
      monster = choice(("Unicorn","Imp"))
    else:
      monster = choice(easy+medium+hard+ohio)

    if monster in easy:
      health = choice((4,5,5,6))
      size = 1
    elif monster in medium:
      health = choice((7,8,8,10,11))
      size = choice((2,3,3,4))
      if monster in ["Kobold", "qsucubus"]:
        size = -1 * size
    elif monster in hard:
      health = choice((14,15,16,18))
      size = choice((4,5,6))
      if monster in ["ArchAngel", "Basilisk", "Naga"]:
        size = -1 * size
    elif monster in ohio:
      health = choice((20,25))
      size = choice((-5,-6,-7))
    else:
      health = choice((6,8,10,12,14))
      size = choice((3,4,5))

    return monster, health, size

  def spawnNPC(self, npcname, position, size, moveset="ad"):
    if npcname not in list(self.NPC.keys()):
      npc_stats = {
        "pos":position,
        "moveset":moveset,
        "size":size
      }
      self.NPC.update({npcname:npc_stats})

  def spawnMonster(self, entityname, health, size, position, moveset="wasd"):
    tempname = entityname
    for entnum in range(1,25):
      if tempname not in list(self.ENEMY.keys()):
        entity_stats = {
          "pos":position,
          "moveset":moveset,
          "size":size,
          "hp":health
        }
        self.ENEMY.update({tempname: entity_stats})
        break
      else:
        tempname = entityname + str(entnum)

  def showNPCs(self):
    """
    todo: return symbol + position
    run this after players move and after enemies move
    """
    entitylist = {}
    for monster in self.ENEMY:
      if len(monster) > 2:
        entitylist.update({self.ENEMY[monster].get("pos"):monster[0]})

    for npc in self.NPC:
      if len(npc) > 2:
        entitylist.update({self.NPC[npc].get("pos"):npc[0]})
    return entitylist

  def inflict(self, position, atk=2):
    """
    inflict(player_position, player_attack)
    """
    taken = 0
    itemdrop = ""
    xp = 0
    delt = atk
    if position in self.damagefield():
      mon = self.damagefield(position)
      for monster in mon:
        delt = atk * choice(([1]*5)+[1.3]) # 16% Critical Attack Rate for +30% Damage
        if self.ENEMY[monster]["hp"] < delt:
          delt = self.ENEMY[monster]["hp"] + 0.5
        self.ENEMY[monster]["hp"] -= delt
        if self.ENEMY[monster]["hp"] <= 0:
          print("[-] %s was killed."%(monster), file=sys.stderr)
          if "Basilisk" in monster:
            if choice("0001") == "0":
              itemdrop = "b"
          self.ENEMY.pop(monster)
          xp += 0.02
        else:
          monsize = self.ENEMY[monster]["size"]
          taken += ((monsize/delt)*monsize)*choice(([1]*5)+[0.7]) # 16% Block Rate for -30% Damage Taken
          # Damage recieved = (Monster Size / Player Attack) * Monster Size
          # No Leeroy Jenkins
          xp += 0.02
    return round(taken,2), round(xp*delt,2), itemdrop
