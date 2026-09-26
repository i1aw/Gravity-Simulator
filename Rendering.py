import pygame
import math

# Projects world space to screen space
class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 1
        self.rotation = 0
    
    def worldToScreenPoint(self,worldPosition: tuple,) -> tuple:
        width = pygame.display.get_window_size()[0]
        height = pygame.display.get_window_size()[1]
        normX = ((worldPosition[0] - self.x) / max(self.z, 0.0001) / 1920)
        normY = ((worldPosition[1] - self.y) / max(self.z, 0.0001) / 1920)
        distance = math.sqrt((normX * normX) + (normY * normY))
        direction = math.atan2(normY,normX)
        direction += self.rotation
        normX = math.cos(direction) * distance
        normY = math.sin(direction) * distance
        normX = normX * width + width / 2
        normY = normY * width + height / 2
        return (normX,normY)
    
    def screenToWorldPoint(self,screenPosition: tuple) -> tuple:
        # may or may not be written by my bf, ChatGPT
        width = pygame.display.get_window_size()[0]
        height = pygame.display.get_window_size()[1]
        normX = (screenPosition[0] - width / 2) / width
        normY = (screenPosition[1] - height / 2) / height
        distance = math.sqrt(normX * normX + normY * normY)
        direction = math.atan2(normY, normX)
        direction -= self.rotation
        x = math.cos(direction) * distance
        y = math.sin(direction) * distance
        x = x * 1920 * max(self.z, 0.0001) + self.x
        y = y * 1920 * max(self.z, 0.0001) + self.y
        return (x, y)
    
    def scaleFactor(self) -> float:
        width = width = pygame.display.get_window_size()[0]
        return 1 / max(self.z, 0.0001) * width / 1920

# Renderable circle
class Circle:
    def __init__(self,radius: float,color: tuple,x: float,y: float):
        self.radius = radius
        self.color = color
        self.x = x
        self.y = y

    def draw(self, window, camera=Camera()):
        location = camera.worldToScreenPoint((self.x,self.y))
        scaledRadius = self.radius * camera.scaleFactor()
        pygame.draw.circle(window, self.color, location, scaledRadius)

# PyGame general rendering wrapper
class Renderer:
    def __init__(self,window):
        self.WINDOW = window
        self.clock = pygame.time.Clock()
        self.screenElements = []
        self.fps = 30
        self.bgColor = (0,0,0)
        self.camera = Camera()
    
    def render(self, camera=None):
        self.WINDOW.fill(self.bgColor)

        for element in self.screenElements:
            if camera:
                element.draw(self.WINDOW,camera)
            else:
                element.draw(self.WINDOW,self.camera)

    def tick(self):
        self.render()
        pygame.display.update()
        self.clock.tick(self.fps)
