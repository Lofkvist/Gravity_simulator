import pygame
import math
import numpy as np

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
NAVBAR_HEIGHT = 100
BACKGROUND = pygame.image.load("space_bg.png")

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

FPS = 70
VEL_CONST = 0.02

class Body():

  def __init__(self, x, y, radius, mass, x_vel, y_vel, trail_color):
    self.x = x
    self.y = y
    self.radius = radius
    self.mass = mass
    self.x_vel = x_vel
    self.y_vel = y_vel
    self.decay_const = self.mass*10 ** -8

    self.trail_color = trail_color
    self.trail = []
    self.time_of_creation = 0

  def drawBody(self):
    pygame.draw.circle(WIN, WHITE, (self.x, self.y), self.radius, 0)
  
  def drawVelVector(self):
    pygame.draw.line(WIN, RED, (self.x, self.y), (self.x + 0.2*self.x_vel, self.y + 0.2*self.y_vel))

  def addTrailpoint(self):
    self.trail.append((self.x, self.y))

    if len(self.trail) > 50:
      self.trail = self.trail[-50:-1]

  def massDecay(self, frame, bodies):
    self.radius = self.radius * math.e ** ( -self.decay_const * (frame - self.time_of_creation) )
    self.mass = self.mass * math.e ** ( -self.decay_const * (frame - self.time_of_creation) )
    self.decay_const = self.mass*10 ** -8

    if self.mass < 1 or self.radius < 2:
      bodies.remove(self)

  def drawTrail(self):
    for p in self.trail:
      pygame.draw.circle(WIN, self.trail_color, (p[0], p[1]), 1, 0)
  
  def drawData(self, font):
    mass_text = font.render(f'Mass: {round(self.mass)} kg', False, WHITE)
    vel_text = font.render(f'Velocity: {round(math.sqrt(self.x_vel**2 + self.y_vel**2)):,} m/s', False, WHITE)

    WIN.blit(mass_text, (self.x + self.radius, self.y - self.radius))
    WIN.blit(vel_text, (self.x + self.radius, self.y - self.radius - 20))


  def collision(self, other, bodies):
    if round(self.x_vel, 3) == round(other.x_vel, 3) and round(self.y_vel, 3) == round(other.y_vel, 3):
      if self.mass > other.mass:
        self.mass += other.mass
        self.radius += math.sqrt(other.mass)
        bodies.remove(other)
      else:
        other.mass += self.mass
        other.radius += math.sqrt(self.radius)
        bodies.remove(self)

    m1 = self.mass
    m2 = other.mass

    v_1 = np.array([self.x_vel, self.y_vel])
    pos_1 = np.array([self.x, self.y])

    v_2 = np.array([other.x_vel, other.y_vel])
    pos_2 = np.array([other.x, other.y])

    v_1_new = v_1 - (pos_1 - pos_2) * (2 * m2/(m1 + m2)) * np.inner(v_1 - v_2, pos_1 - pos_2) / (np.inner(pos_1 - pos_2, pos_1 - pos_2)) 
    v_2_new = v_2 - (pos_2 - pos_1) * (2 * m1/(m1 + m2)) * np.inner(v_2 - v_1, pos_2 - pos_1) / (np.inner(pos_2 - pos_1, pos_2 - pos_1))
    
    self.x_vel, self.y_vel = v_1_new
    other.x_vel, other.y_vel = v_2_new

    self.x += self.x_vel*(1/FPS)
    self.y += self.y_vel*(1/FPS)
    other.x += other.x_vel*(1/FPS)
    other.y += other.y_vel*(1/FPS)

  def updatePosition(self):
    self.x += self.x_vel*(1/FPS)
    self.y += self.y_vel*(1/FPS)

  def updateVelocity(self, bodies, G, collison_bool):
    for other in bodies:
      if other == self:
        continue

      else:
        # Gravitational force from other bodies
        dX = self.x - other.x
        dY = self.y - other.y
        r = math.sqrt((dX)**2 + (dY)**2)
        
        dX_next = (self.x + self.x_vel*(1/FPS)) - (other.x + other.x_vel*(1/FPS))
        dY_next = (self.y + self.y_vel*(1/FPS)) - (other.y + other.y_vel*(1/FPS))
        r_next = math.sqrt((dX_next)**2 + (dY_next)**2)

        # Check for collision in next frame
        if r_next <= self.radius + other.radius and collison_bool:
          self.collision(other, bodies)

        else:
          F = -G * (self.mass * other.mass) / (r**2)
          
          theta = math.atan2(dY, dX)
          x_acc = math.cos(theta) * F/self.mass
          y_acc = math.sin(theta) * F/self.mass

          self.x_vel += 2*x_acc*(1/FPS)
          self.y_vel += 2*y_acc*(1/FPS)