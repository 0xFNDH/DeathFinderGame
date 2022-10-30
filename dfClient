import socket, time, sys
from binascii import hexlify, unhexlify

Broadcast = ""
Username = ""

ingress = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ingress.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
try:
  ingress.bind((Broadcast, 5002))
except:
  ingress.bind(("", 5002))

def _decompress(comp):
  comp = comp.replace("3","555").replace("4", "."*4).replace("5"," "*5).replace(";"," ").replace("6","#"*6).replace("!n","\n")
  return comp

def colour(visual):
  visual = visual.replace("@","\N{ESC}[46m@\N{ESC}[m").replace("&","\N{ESC}[46m&\N{ESC}[m").replace("g","\N{ESC}[32mg\N{ESC}[m").replace("D","\N{ESC}[41;5mD\N{ESC}[m")
  visual = visual.replace("G","\N{ESC}[32mG\N{ESC}[m").replace("W","\N{ESC}[41;5mW\N{ESC}[m").replace("?","\N{ESC}[1m?\N{ESC}[m").replace("s","\N{ESC}[37;2ms\N{ESC}[m").replace("S","\N{ESC}[33;3mS\N{ESC}[m")
  visual = visual.replace("U","\N{ESC}[95;1mU\N{ESC}[m").replace(":","\N{ESC}[5m:\N{ESC}[m")
  return visual

def unify(visual):
  visual = visual.replace("#", u"\u2588").replace("?",u"\u2370").replace(":", u"\u2f55")
  return visual

Color = False
Unicode = False

assert len(Username) > 3

class GameHandler():

  def __init__(self):
    self.HP = 10.0
    self.XP = 0.0
    self.inventory = ""

  def updateInv(self, inv, action):
    if inv != self.inventory:
      newinv = inv.replace(self.inventory, "")
      if "-w" in newinv:
        print("You pick up a magic barrier scroll.")
      if "-m" in newinv:
        print("You pick up a scroll of magic missile.")
      if "-d" in newinv:
        print("You pick up a scroll of digging.")
      if "-H" in newinv:
        print("You pick up a scroll of healing.")

    if action == "i":
      print(" ---- Inventory ---- ")
      print("(1) - Double Edge Great Sword")
      allinv = inv.replace("-w","(w) - Scroll of magic barrier\n").replace("-m","(m) - Scroll of magic missile\n").replace("-d","(d) - Scroll of digging\n").replace("-h","(H) - Scroll of full health\n")
      print(allinv)

    self.inventory = inv

  def Stats(self, hp, xp):
    if float(hp) < self.HP:
      damage = self.HP-float(hp)
      if float(hp) == 0.0:
        print("Your body grows cold as you fall to the floor. You have died.")
        sys.exit()
      elif damage < 2.0:
        print("The opponent's attack hits you.")
      elif damage < 4.0:
        print("You receive a hard strike from the enemy.")
      elif damage < 6.0:
        print("You feel a sharp pain. You are in danger.")
      elif damage < 10.0:
        print("Your mind goes into shock as you are almost dead.")
      elif damage < 15.0:
        print("All your bones break as the monster lands its attack.")
        print("You are dead.")
        sys.exit()
      elif damage < 25.0:
        print("You're dead but the enemies do not stop attacking you.")
        sys.exit()
      elif damage < 50.0:
        print("Your body is incinerated. Nothing but ash remains.")
        sys.exit()
      else:
        print("All your pain stops. You look to your left, you see god.")
        print("You are extremely dead.")
        sys.exit()

    elif float(hp) > self.HP:
      heal = float(hp)-self.HP
      if heal > 3.0:
        print("Your pain vanishes.")
      else:
        print("Your wounds begin to heal.")
    if float(xp) > self.XP:
      xpgain = xp
      if xpgain > 0.04:
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

while True:
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

  pkt = "USER: %s, %s"%(Username, input("> "))
  s.sendto(pkt.encode(), (Broadcast, 5003))
  data = b"."
  while Username not in data.decode():
    data, addr = ingress.recvfrom(800)

  playerstats = data.decode().split("\n")[0]
  mapdata = _decompress(data.decode().split("\n")[1])
  hander.Stats(float(playerstats.split(", ")[-2]), 0.0)
  if pkt[-1] == "i":
    hander.updateInv("","i")

  if Color == True:
    mapdata = colour(mapdata)
  if Unicode == True:
    mapdata = unify(mapdata)

  print(mapdata)
  print(playerstats)

  s.close()
  del s
