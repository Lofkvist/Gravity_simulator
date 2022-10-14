from time import clock_gettime
import pygame, sys
from pygame.locals import *
import math
import numpy as np

pygame.init()
pygame.font.init()
 
# Game Setup
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
 
WIN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
WHITE = (255, 255, 255)
BLACK = (0, 0, 0) 
RED = (255,0,0)
BLUE = (65,105,225)
PINK = (226, 99, 149)
GREEN = (124,252,0)
PURPLE = (163, 22, 250)
ORANGE = (252, 140, 45)
TRAIL_COLORS = [PINK, GREEN, PURPLE, ORANGE, RED]

FPS = 40
G = 80 #Arbitrary gravitational constant
VEL_CONST = 0.02

def inflate(x, y, time):
  pygame.draw.circle(WIN, WHITE, (x, y), 10*time, 0)

class Body():

  def __init__(self, x, y, radius, mass, x_vel, y_vel, trail_color):
    self.x = x
    self.y = y
    self.radius = radius
    self.mass = mass
    self.x_vel = x_vel
    self.y_vel = y_vel

    self.trail_color = trail_color
    self.trail = []

  def drawBody(self):
    pygame.draw.circle(WIN, WHITE, (self.x, self.y), self.radius, 0)
  
  def drawVelVector(self):
    pygame.draw.line(WIN, RED, (self.x, self.y), (self.x + 10*self.x_vel, self.y + 10*self.y_vel))

  def addTrailpoint(self):
    self.trail.append((self.x, self.y))

    if len(self.trail) > 40:
      self.trail = self.trail[-40:-1]

  def drawTrail(self):
    for p in self.trail:
      pygame.draw.circle(WIN, self.trail_color, (p[0], p[1]), 1, 0)

  # def collision(self, other, bodies):
  #   v_1 = np.array([self.x_vel, self.y_vel])
  #   x_1 = np.array([self.x, self.y])

  #   v_2 = np.array([other.x_vel, self.y_vel])
  #   x_2 = np.array([other.x, other.y])

  #   if np.round(v_1[0]-v_1[1], decimals=3) < 0.02 and np.round(v_2[0]-v_2[1], decimals=3) < 0.02:
  #     if self.mass > other.mass:
  #       self.mass += other.mass
  #       bodies.remove(other)
  #     else:
  #       other.mass += self.mass
  #       bodies.remove(self)

  #   dX1 = x_1 - x_2
  #   dX2 = x_2 - x_1

  #   v_1_new = v_1 - (dX1)*(2 * other.mass/(other.mass + self.mass)) * np.dot(v_1 - v_2, dX1)/(np.linalg.norm(dX1)**2)
  #   v_2_new = v_2 - (dX2)*(2 * self.mass/(other.mass + self.mass)) * np.dot(v_2 - v_1, dX2)/(np.linalg.norm(dX2)**2)

  #   print(v_1_new)
  #   print(v_2_new)

  #   self.x_vel, self.y_vel = v_1_new
  #   other.x_vel, other.y_vel = v_2_new

  def updatePosition(self):
    self.x += self.x_vel
    self.y += self.y_vel

  def updateVelocity(self, bodies):
    for other in bodies:
      if other == self:
        continue

      else:
        # Gravitational force from other bodies
        dX = self.x - other.x
        dY = self.y - other.y
        r = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        
        # Check for collision
        if r < self.radius + other.radius:
          #self.collision(other, bodies)
          pass

        else:
          F = -G * (self.mass * other.mass) / (r**2)
          
          theta = math.atan2(dY, dX)
          x_acc = math.cos(theta) * F/self.mass
          y_acc = math.sin(theta) * F/self.mass

          self.x_vel += x_acc*(1/FPS)
          self.y_vel += y_acc*(1/FPS)
          
# The main game loop
def main():
  clock = pygame.time.Clock()
  run = True
  bodies = []
  frame = 0

  draw_timer = 0
  drawing = False


  font = pygame.font.SysFont('Helvetica', 14)
  font.set_bold(True)

  print(pygame.font.get_fonts())
  text_surface = font.render('Some Text', False, BLUE)

  while run:
    clock.tick(FPS)  #5 fps
    WIN.fill(BLACK)
    pygame.draw.rect(WIN, WHITE, pygame.Rect(0, 0, WINDOW_WIDTH, 100))
    WIN.blit(text_surface, (10, 10))


    for event in pygame.event.get():
      if event.type == QUIT:
        pygame.quit()
        sys.exit()

      elif event.type == pygame.MOUSEBUTTONDOWN:
        mouse_start = pygame.mouse.get_pos()
        drawing = True

      elif event.type == pygame.MOUSEBUTTONUP:
        mouse_end = pygame.mouse.get_pos()

        drag = mouse_start[0] - mouse_end[0], mouse_start[1] - mouse_end[1]
        x_vel, y_vel = drag

        drawing = False
        
        #Add drawn body
        if draw_timer > 0.5:
          bodies.append(
            Body(mouse_start[0], mouse_start[1], 10*draw_timer, 10*draw_timer**3,
          VEL_CONST*x_vel, VEL_CONST*y_vel, TRAIL_COLORS[len(bodies)%len(TRAIL_COLORS)])
          )
        draw_timer = 0
      
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
            bodies.clear()

    if drawing:
      draw_timer += 1/FPS
      inflate(mouse_start[0], mouse_start[1], draw_timer)

    frame += 1

    for body in bodies:
      body.updateVelocity(bodies)
      body.updatePosition()
      body.drawBody()
      body.drawVelVector()

      if frame%(FPS//4) == 1:
        frame%(FPS//4) == 1
        body.addTrailpoint()
      
      body.drawTrail()

      # Remove if body has left screen
      if body.x < 0 or body.x > WINDOW_WIDTH or body.y < 100 or body.y > WINDOW_HEIGHT:
        bodies.remove(body)
    pygame.display.update()

if __name__ == '__main__':
  main()