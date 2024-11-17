import codeokey
import random
from codeokey import mc
mc.connect("localhost","AnimePridyrok")

x = random.randint(-63,63)
z = random.randint(-63,63)
y = mc.world.getHeight(x,z) + 1
mc.world.setBlock(x,y,z,"fire")

c = 0

while True:
    xP, yP, zP = mc.player.getPos()
    if xP == x and yP == y and zP == z:
        mc.world.setBlock(x,y,z,"water")
        mc.chat.postToChat("Win!!!")
        break