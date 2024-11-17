from codeokey.vec3 import Vec3
from codeokey.connection import Connection
#from setuptools.package_index import entity_sub


class World:
    def __init__(self, connection):
        self.conn = connection

    def setBlock(self, x, y, z, block, data=0):
        """Установить блок (x,y,z,block,data)"""
        self.conn.sendReceive(b"world.setBlock", x, y, z, block, data)

    def setBlocks(self, *args):
        """Заполнить (x0,y0,z0,x1,y1,z1,id,[data])"""
        self.conn.sendReceive(b"world.setBlocks", args)

    def buildColumn(self, *args):
        """Построить столб (x,y,z,h,[data])"""
        self.conn.sendReceive(b"world.buildColumn", args)

    def buildSphere(self, *args):
        """Построить сферу (x,y,z,r,Block,isFilled)"""
        self.conn.sendReceive(b"world.buildSphere", args)

    def buildHome(self, x,y,z,w,l,h,block,floorBlock = "oak_planks",orientation = "south"):
        """Построить дом (x,y,z,w,l,h,Block,FloorBlock,orientation)"""
        self.conn.sendReceive(b"world.buildHome", x,y,z,w,l,h,block,floorBlock,orientation)

    #def setSign(self, *args):
        """Set a sign (x,y,z,id,data,[line1,line2,line3,line4])
        
        Wall signs (id=68) require data for facing direction 2=north, 3=south, 4=west, 5=east
        Standing signs (id=63) require data for facing rotation (0-15) 0=south, 4=west, 8=north, 12=east"""        
        #lines = []
        #flatargs = []
        #for arg in flatten(args):
        #    flatargs.append(arg)
        #for flatarg in flatargs[5:]:
        #    lines.append(flatarg.replace(",",";").replace(")","]").replace("(","["))
        #self.conn.send(b"world.setSign",flatargs[0:5]) + lines

    def getBlock(self, *args):
        """Получить блок на (x,y,z)"""
        return self.conn.sendReceive(b"world.getBlock", args)

    def getBlockWithData(self, *args):
        """Получить блок с доп аргументом (x,y,z)"""
        ans = self.conn.sendReceive(b"world.getBlockWithData", args)
        return Block(*list(map(int, ans.split(","))))

    def getBlocks(self, *args):
        """Получить массив блоков (x0,y0,z0,x1,y1,z1)"""
        s = self.conn.sendReceive(b"world.getBlocks", args)
        return list(s.split(","))
#работает
    def getHeight(self, *args):
        """Получить высочайшую точку (x,z)"""
        s = self.conn.sendReceive(b"world.getHeight", (args))
        y = int(float(s[s.find("y=")+2:s.find("z=")-1]))
        return y

class Player:
    def __init__(self, connection, playerId):
        self.conn = connection
        self.player = playerId
    #добавить округление
    def getPos(self):
        """Получить координаты игрока в формате Vec3"""
        s = self.conn.sendReceive(b"player.getPos")
        coords = Vec3(*list(map(float, s.split(","))))
        coords.x = round(coords.x - 0.5)
        coords.y = round(coords.y)
        coords.z = round(coords.z - 0.5)
        return coords
    #работает
    def setPos(self, x,y,z):
        """Установить координаты игроку (x,y,z)"""
        self.conn.sendReceive(b"player.setPos", x,y,z)
    #???
    def setDirection(self, *args):
        """Set entity direction (entityId:int, x,y,z)"""
        self.conn.sendReceive(b"player.setDirection", self.player, args)
    #работает
    def getDirection(self):
        """Получить направление взгляда игрока в формате Vec3"""
        s = self.conn.sendReceive(b"player.getDirection")
        return Vec3(*map(float, s.split(",")))
    #работает
    def setRotation(self, yaw):
        """Установить угол поворота камеры игрока (yaw)"""
        self.conn.send(b"player.setRotation", yaw)
    #работает
    def getRotation(self):
        """Получить угол поворота камеры игрока (yaw)"""
        return float(self.conn.sendReceive(b"player.getRotation"))
    #работает
    def setPitch(self, pitch):
        """Set entity pitch (entityId:int, pitch)"""
        self.conn.sendReceive(b"player.setPitch", pitch)
    #работает
    def getPitch(self):
        """get entity pitch (entityId:int) => float"""
        return float(self.conn.sendReceive(b"player.getPitch"))
    def addEffect(self, effectType, duration = 5, amplifier = 3 ):
        """Добавляет на игрока эффект (Эффект: str, Длительность: int, Уровень эффекта: int)"""
        self.conn.sendReceive(b"player.addEffect", effectType, duration * 20, amplifier - 1)

class Entity:
    def __init__(self, connection, playerId):
        self.conn = connection
        self.playerId = playerId

    def spawnEntity(self, *args):
        """Создать сущность (x,y,z,entity:str)"""
        return str(self.conn.sendReceive(b"world.spawnEntity", *args))

    def setPos(self, x,y,z,entityId):
        """Установить координаты для энтити (x,y,z)"""
        self.conn.sendReceive(b"entity.setPos", entityId,x,y,z)
    def getPos(self, entityId):
        """Узнать координаты энитити"""
        s = self.conn.sendReceive(b"entity.getPos", entityId)
        coords = Vec3(*list(map(float, s.split(","))))
        coords.x = round(coords.x - 0.5)
        coords.y = round(coords.y)
        coords.z = round(coords.z - 0.5)
        return coords

    def getName(self, id):
        """Get the list name of the player with entity id => [name:str]

        Also can be used to find name of entity if entity is not a player."""
        return self.conn.sendReceive(b"entity.getName", id)

    def getEntities(self, id, distance=10, typeId=-1):
        """Return a list of entities near entity (playerEntityId:int, distanceFromPlayerInBlocks:int, typeId:int) => [[entityId:int,entityTypeId:int,entityTypeName:str,posX:float,posY:float,posZ:float]]"""
        """If distanceFromPlayerInBlocks:int is not specified then default 10 blocks will be used"""
        s = self.conn.sendReceive(b"entity.getEntities", id, distance, typeId)
        entities = [e for e in s.split("|") if e]
        return [[int(n.split(",")[0]), int(n.split(",")[1]), n.split(",")[2], float(n.split(",")[3]),
                 float(n.split(",")[4]), float(n.split(",")[5])] for n in entities]

    def removeEntities(self, typeId, distance=10):
        """Remove entities all entities near entity (playerEntityId:int, distanceFromPlayerInBlocks:int, typeId:int, ) => (removedEntitiesCount:int)"""
        """If distanceFromPlayerInBlocks:int is not specified then default 10 blocks will be used"""
        return int(self.conn.sendReceive(b"entity.removeEntities", self.playerId, distance, typeId))

class Chat:
    def __init__(self, connection, playerId):
        self.conn = connection
        self.playerId = playerId

    def postToChat(self, msg):
        self.conn.sendReceive(b"chat.post", msg)
# Переменные для хранения объектов
_connection = None
world = None
player = None
entity = None
chat = None

def connect(address="localhost", playerName=""):
    """
    Подключение к серверу и инициализация глобальных объектов.
    """
    global _connection, world, player, entity, chat
    port=4711
    # Инициализация соединения
    _connection = Connection(address, port)
    
    # Проверка и получение ID игрока, если задано имя
    if playerName:
        playerId = int(_connection.sendReceive(b"world.getPlayerId", playerName))
        # log(f"Получен ID игрока {playerName} = {playerId}")

    # Инициализация объектов для взаимодействия с миром и игроком
    world = World(_connection)
    player = Player(_connection, playerId)
    entity = Entity(_connection, playerId)
    chat = Chat(_connection, playerId)

# Поддержка автоподключения
__all__ = ['connect', 'world', 'player']