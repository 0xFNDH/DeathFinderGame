import socket, time, sys
from binascii import hexlify, unhexlify

Multicast = "224.0.0.251"
Username = ""

Color = True
Unicode = False

assert len(Username) > 3

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

ingress = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
try:
  ingress.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
except AttributeError:
  pass
ingress.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
ingress.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

ingress.bind((Multicast, 15002))
host = getLANIP()
ingress.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
ingress.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP,
socket.inet_aton(Multicast) + socket.inet_aton(host))
ingress.settimeout(2)

def _decompress(comp):
  comp = comp.replace("3","555").replace("4", "."*4).replace("5"," "*5).replace(";"," ").replace("6","#"*6).replace("!n","\n")
  return comp
  
def colour(visual):
  visual = visual.replace("@","\N{ESC}[46m@\N{ESC}[m").replace("&","\N{ESC}[46m&\N{ESC}[m").replace("g","\N{ESC}[32mg\N{ESC}[m").replace("D","\N{ESC}[41;5mD\N{ESC}[m")
  visual = visual.replace("G","\N{ESC}[32mG\N{ESC}[m").replace("W","\N{ESC}[41;5mW\N{ESC}[m").replace("?","\N{ESC}[1m?\N{ESC}[m").replace("s","\N{ESC}[37;2ms\N{ESC}[m").replace("S","\N{ESC}[33;3mS\N{ESC}[m")
  visual = visual.replace("U","\N{ESC}[95;1mU\N{ESC}[m").replace(":","\N{ESC}[106;5m:\N{ESC}[m")
  return visual
  
def unify(visual):
  visual = visual.replace("#", u"\u2588").replace("?",u"\u2370")
  return visual

class GameHandler():

  def __init__(self):
    
    self.health = 10.0
    self.experience = 0.0
    self.inventory = ""
    
    self.HP = 10.0
    self.XP = 0.0
    self.INV = ""
    
  def parse(self, inbound):
    data = inbound.decode()
    playerinfo = data.split("\n")[0].split(" ")
    position = playerinfo[2]
    health = float(playerinfo[3].split(":")[-1])
    experience = float(playerinfo[4].split(":")[-1])
    inventory = playerinfo[5].split(":")[-1]
    epoch = playerinfo[6].split(":")[-1]
    self.health = health
    self.experience = experience
    self.inventory = inventory
    print(self.infobar(health, self.HP, experience, self.XP, inventory, position, epoch))
    self.hpxp_dialog(health, experience)
    self.item_dialog(inventory)
  
  def infobar(self, health, hp, experience, xp, inventory, position, epoch):
    bar = "(%s)"%Username
    bar += " HP[%s%s%s] "%("#"*int(health),":"*abs(int(health-hp))," "*(15-int(health)))
    if health < hp:
      bar += str(round(health-hp,1)) + " "
    elif health > hp:
      bar += "+"+str(round(health-hp,1)) + " "
    bar += "\n"
    bar += "XY:%s "%position
    if len(inventory) > 0:
      bar += "Bag:"+inventory
    else:
      bar += "Bag: None"
    bar += " ATK:%s XP:%s"%(2+int(experience), round(experience,2))
    if experience < xp:
      bar += "(%s)"%str(round(experience-xp,2))
    elif experience > xp:
      bar += "(+%s)"%str(round(experience-xp,2))
    bar += " EPOCH:"+epoch
    return bar
  
  def item_dialog(self, inv):
    if inv != self.INV:
      if len(inv) < len(self.INV):
        diff = set(self.INV).difference(inv).pop()
        print("[?] You have lost items: %s"%(diff), file=sys.stderr)
      else:
        diff = set(inv).difference(self.INV).pop()
        print("[?] You have gained items: %s"%(diff))
      self.INV = inv
        
  def hpxp_dialog(self, hp, xp):
    if float(hp) < 0.0:
      print("You died.")
    
    elif float(hp) < self.HP:
      damage = self.HP-float(hp)
      if damage < 2.0:
        print("The opponent's attack hits you.")
      elif damage < 4.0:
        print("You receive a hard strike from the enemy.")
      elif damage < 6.0:
        print("You feel a sharp pain. You are in danger.")
      elif damage < 10.0:
        print("Your mind goes into shock as you are almost dead.")
      elif damage < 15.0:
        print("All your bones break as the monster lands its attack.")
      elif damage < 25.0:
        print("Your body is incinerated.")
        
    elif float(hp) > self.HP:
      heal = float(hp)-self.HP
      if heal > 3.0:
        print("Your pain vanishes.")
      else:
        print("Your wounds begin to heal.")
    
    if float(xp) > self.XP:
      xpgain = xp
      if xpgain > 0.08:
        print("You sword cuts with little resistance.")
      else:
        print("You land a hit on the opponent.")
      if int(xp) > int(self.XP):
        print("Your body feels light. Your level has increased.")
    elif float(xp) < self.XP:
      if float(xp) == 0.0:
        print("You feel drained as your strength flees your body.")
      else:
        print("You feel weak and as if they stole your energy.")
        
    self.HP = float(hp)
    self.XP = float(xp)
    
hander = GameHandler()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
s.settimeout(3)

while True:

  pkt = "USER: %s, %s"%(Username, input("> "))
  s.sendto(pkt.encode(), (Multicast, 15003))
  data = b"."
  try:
    while Username not in data.decode():
      data, addr = ingress.recvfrom(800)
    mapdata = _decompress(data.decode().split("\n")[1])
    
    if Color == True:
      mapdata = colour(mapdata)
    if Unicode == True:
      mapdata = unify(mapdata)
    print(mapdata)
      
    hander.parse(data)
  except KeyboardInterrupt:
    break
  except Exception as e:
    print(e)
    pass
