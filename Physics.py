import math
import Rendering
import time
AVERAGE_DELTA_TIME_WINDOW_SIZE = 2
def sign(number: float):
    if number == 0:
        return 0
    return number / abs(number)

# PhysicsSystem handles physical constants and prevents spikes in deltaTime
class PhysicsSystem:
    def __init__(self):
        self.timeScale = 1
        self.gravitationalConstant = 1
        self.elasticity = 0.5
        self.deltaTime = 0
        self.averageDeltaTime = 0
        self.__deltaTimes = []
        self.__lastTick = time.perf_counter()


    def tick(self):

        # prevent deltaTime from spiking when a window is dragged or paused
        currentTime = time.perf_counter()
        self.deltaTime = currentTime - self.__lastTick
        self.__deltaTimes.append(self.deltaTime)
        length = len(self.__deltaTimes)
        if length > AVERAGE_DELTA_TIME_WINDOW_SIZE:
            self.__deltaTimes.pop(0)
        elif length != 1:
            self.averageDeltaTime = (sum(self.__deltaTimes) - max(self.__deltaTimes)) / (length - 1) # remove max value (spikes from moving window)
        else:
            self.averageDeltaTime = self.deltaTime
        self.__lastTick = currentTime

class PhysicsObject:
    def __init__(self, x: float, y: float, mass: float) -> None:
        self.mass = mass
        self.x = x
        self.y = y
        self._newX = x
        self._newY = y
        self.xv = 0
        self.yv = 0
        self._newXV = 0
        self._newYV = 0
        self.appliesGravity = True
        self.affectedByGravity = True
        self.physicsSystem = PhysicsSystem()

    # Calculates the effect of gravity on this physics object from another
    def applyGravity(self, body):
        if not self.affectedByGravity:
            return
        if not body.appliesGravity:
            return
        if self == body:
            return
        dx = body.x - self.x
        dy = body.y - self.y
        distanceSquared = (dx * dx) + (dy * dy)
        if distanceSquared == 0:
            return
        distance = math.sqrt(distanceSquared)
        normX = dx / distance
        normY = dy / distance
        f = self.physicsSystem.gravitationalConstant * (self.mass * body.mass) / distanceSquared
        self._newXV += normX * f * self.physicsSystem.timeScale * self.physicsSystem.averageDeltaTime * 60
        self._newYV += normY * f * self.physicsSystem.timeScale * self.physicsSystem.averageDeltaTime * 60

    # Updates properties to new values. Used so gravity and other forces can all be calculated before any changes are made
    def updateProperties(self):
        self.xv = self._newXV
        self.yv = self._newYV
        self.x = self._newX
        self.y = self._newY
        self.x += (self.xv / self.mass) * self.physicsSystem.timeScale * self.physicsSystem.averageDeltaTime * 60
        self.y += (self.yv / self.mass) * self.physicsSystem.timeScale * self.physicsSystem.averageDeltaTime * 60
        self._newX = self.x
        self._newY = self.y

    # velocity mutator
    def setVelocity(self,x: float,y: float):
        self._newXV = x
        self.xv = x
        self._newYV = y
        self.yv = y

    def addVelocity(self,x: float, y: float):
        self._newXV += x
        self.xv += x
        self._newYV += y
        self.yv += y

# Physical circle with rendering
class Circle(PhysicsObject, Rendering.Circle):
    def __init__(self, x: float, y: float, radius: float, color: tuple, mass: float, renderer: Rendering.Renderer, physics=PhysicsSystem(),xv=0,yv=0):
        self.x = x
        self.y = y
        self._newX = x
        self._newY = y
        self.xv = xv
        self.yv = yv
        self._newXV = xv
        self._newYV = yv
        self.mass = mass
        self.color = color
        self.radius = radius
        self.appliesGravity = True
        self.affectedByGravity = True
        renderer.screenElements.append(self)
        self.physicsSystem = physics

    def isTouching(self,circle):
        if self == circle:
            return False
        
        totalRadius = self.radius + circle.radius
        dx = circle.x - self.x
        dy = circle.y - self.y
        
        distanceSquared = (dx * dx) + (dy * dy)
        return distanceSquared <= totalRadius ** 2

    # handle collisions with other physics circles
    def collideWith(self,planet):
        if self.isTouching(planet):
            # print("hit")
            dx = planet.x - self.x
            dy = planet.y - self.y
            distance = math.sqrt((dx ** 2) + (dy ** 2))
            normX = dx / distance
            normY = dy / distance
            combindRadius = self.radius + planet.radius
            relXVelocity = planet.xv - self.xv
            relYVelocity = planet.yv - self.yv
            f = math.sqrt((relXVelocity * relXVelocity) + (relYVelocity * relYVelocity))
            self._newXV -= normX * f * self.physicsSystem.elasticity * sign(self.physicsSystem.timeScale)
            self._newYV -= normY * f * self.physicsSystem.elasticity * sign(self.physicsSystem.timeScale)
            self._newX -= (normX * (combindRadius - distance)) / 2
            self._newY -= (normY * (combindRadius - distance)) / 2
