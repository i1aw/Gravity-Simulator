import pygame
import Rendering
import Physics
import random

pygame.init()
SCREENWIDTH = pygame.display.Info().current_w
WINDOW = pygame.display.set_mode((600,400), pygame.RESIZABLE)

renderer = Rendering.Renderer(WINDOW)
renderer.fps = 60
physicsSystem = Physics.PhysicsSystem()
physicsSystem.gravitationalConstant = 10
timeScale = 0
physicsSystem.timeScale = timeScale
physicsSystem.elasticity = 0.7
PLANET_AMOUNT = 40
planets = []
mouseButtonDown = False
mouseStartX = 0
mouseStartY = 0
spacePressed = False
running = True

# create plannets
for __ in range(PLANET_AMOUNT):
    x = random.randint(-1500,1500)
    y = random.randint(-1500,1500)
    radius = 50
    color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
    mass = 50
    planets.append(Physics.Circle(x,y,radius,color,mass, renderer,physicsSystem))

# Runs gravity and collision logic on all planets
def calculatePhysics(planets: list[Physics.Circle]):
    for planet in planets:
        for planet2 in planets:
            planet.applyGravity(planet2)
            planet.collideWith(planet2)

# updates planets after velocity and other values are updated
def movePlanets(planets: list[Physics.Circle]):
    for planet in planets:
        planet.updateProperties()


def tick():
    calculatePhysics(planets)
    movePlanets(planets)
    renderer.tick()
    physicsSystem.tick()

###### Main loop ######
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouseButtonDown = True
            mouseStartX = event.pos[0]
            mouseStartY = event.pos[1]

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouseButtonDown = False

        elif event.type == pygame.MOUSEMOTION:
            # handle panning
            if mouseButtonDown:
                widthScale = pygame.display.get_window_size()[0] / SCREENWIDTH
                worldStart = renderer.camera.screenToWorldPoint((mouseStartX,mouseStartY))
                worldChange = renderer.camera.screenToWorldPoint((event.pos[0],event.pos[1]))
                worldChange = ((worldChange[0] - worldStart[0]) / widthScale, (worldChange[1] - worldStart[1]) / widthScale)
                renderer.camera.x -= worldChange[0] * widthScale
                renderer.camera.y -= worldChange[1] * widthScale
                mouseStartX,mouseStartY = event.pos

        elif event.type == pygame.MOUSEWHEEL:
            # handle zooming
            renderer.camera.z = renderer.camera.z * (0.9 ** event.y)

        # handle spacePressed variable
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                spacePressed = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                spacePressed = False
    
    if spacePressed:
        physicsSystem.timeScale = 1
    tick()

