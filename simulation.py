import pygame, sys
from pygame.locals import *
import math
from body import Body

pygame.init()
pygame.font.init()
 
# Game Setup
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
NAVBAR_HEIGHT = 100
FPS = 70
BACKGROUND = pygame.image.load("space_bg.png")
WIN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
VEL_CONST = 0.02
prefix = ['', 'k', 'M', 'G', 'T', 'P']

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0) 
RED = (255,0,0)
BLUE = (65,105,225)
PINK = (226, 99, 149)
GREEN = (124,252,0)
PURPLE = (163, 22, 250)
ORANGE = (252, 140, 45)
TRAIL_COLORS = [PINK, GREEN, PURPLE, ORANGE, RED]


def totalEnergy(bodies):
  E = 0
  for body in bodies:
    v = math.sqrt(body.x_vel**2 + body.y_vel**2)
    E += (body.mass/2) * (v ** 2)
  return round(E, 2)


def inflate(x, y, time): # Inflate body
  pygame.draw.circle(WIN, WHITE, (x, y), 10*time, 0)


# Main game loop
def main():
  clock = pygame.time.Clock()
  bodies = []
  frame = 0
  draw_timer = 0
  G = 40

  trail_shown = True
  drawing = False
  decay_active = False
  collision_absorb = True
  pause = False

  font = pygame.font.SysFont('Helvetica', 14)
  bigFont = pygame.font.SysFont('Helvetica', 30)
  font.set_bold(True)
  bigFont.set_bold(True)

  game_header = bigFont.render('Simulation of Newtonian Mechanics', False, BLUE)
  clear_text = font.render('Clear simulation:   [R]', False, BLUE)
  trail_toggle = font.render('Toggle trail:          [T]', False, BLUE)
  grav_const = font.render(f'Toggle G by 100:                                   [+/-]', False, BLUE)
  decay_text = font.render('Toggle mass decay:                               [D]', False, BLUE)
  collision_absorb_text = font.render('Toggle ellastic collision and absorbtion:  [C]', False, BLUE)
  pause_text = font.render('Pause simulation:  [P]', False, BLUE)
  while_paused_text = bigFont.render('PAUSED', False, BLUE)


  while True:
    clock.tick(FPS)
    WIN.blit(BACKGROUND, (0,0))
    pygame.display.set_caption('Gravity simulator')
    pygame.draw.rect(WIN, WHITE, pygame.Rect(0, 0, WINDOW_WIDTH, NAVBAR_HEIGHT))

    E = totalEnergy(bodies)
    i = 0
    while E > 1000:
      E = E/1000
      i += 1

    pre = prefix[i]
    energy_text = font.render(f'Total kinetic energy: {round(E, 4)} {pre}J', False, BLUE)

    #Display text
    WIN.blit(game_header, (10, 5))

    WIN.blit(clear_text, (10, 40))
    WIN.blit(trail_toggle, (10, 60))
    WIN.blit(pause_text, (10, 80))

    WIN.blit(collision_absorb_text, (270, 40))
    WIN.blit(decay_text, (270, 60))
    WIN.blit(grav_const, (270, 80))

    WIN.blit(energy_text, (900, 80))

    frame += 1

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
        
        #Add drawn body
        if draw_timer > 0.5:
          bodies.append(
            Body(mouse_start[0], mouse_start[1], 10*draw_timer, 10*draw_timer**3,
          x_vel, y_vel, TRAIL_COLORS[len(bodies)%len(TRAIL_COLORS)]))
          bodies[-1].time_of_creation = frame
        draw_timer = 0
        drawing = False
      
      #Keyboard input
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
          bodies.clear()

        elif event.key == pygame.K_t:
          trail_shown = not trail_shown

        elif event.key == pygame.K_PLUS:
          G += 100

        elif event.key == pygame.K_MINUS:
          G -= 100
          if G < 0:
            G = 0
        elif event.key == pygame.K_p:
          pause = not pause

        elif event.key == pygame.K_d:
          decay_active = not decay_active
          
        elif event.key == pygame.K_c:
          collision_absorb = not collision_absorb

    if drawing:
      draw_timer += 1/FPS
      inflate(mouse_start[0], mouse_start[1], draw_timer)

    # Update data of bodies
    for body in bodies:
      if pause:
        WIN.blit(while_paused_text, (WINDOW_WIDTH//2 - 30, WINDOW_HEIGHT//2))
        body.drawBody()
        body.drawVelVector()
        body.drawData(font)
        if trail_shown:
          body.drawTrail()
        continue

      body.updateVelocity(bodies, G,collision_absorb)
      body.updatePosition()
      body.drawBody()
      body.drawVelVector()
      body.drawData(font)

      if frame%(FPS//8) == 1:
        body.addTrailpoint()

      if trail_shown:
        body.drawTrail()
      
      if decay_active:
        body.massDecay(frame, bodies)

      # Bounce of walls
      if body.y + body.y_vel*(1/FPS) - body.radius < NAVBAR_HEIGHT or body.y + body.y_vel*(1/FPS) + body.radius > WINDOW_HEIGHT:
        body.y_vel = -body.y_vel

      if body.x + body.x_vel*(1/FPS) - body.radius < 0 or body.x + body.x_vel*(1/FPS) + body.radius > WINDOW_WIDTH:
        body.x_vel = -body.x_vel

    pygame.display.update()

if __name__ == '__main__':
  main()