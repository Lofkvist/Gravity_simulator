import pygame, sys
from pygame.locals import *
import math
from body import Body

#
# Reviewed by Tom
#

pygame.init()
pygame.font.init()
 
# Game Setup
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
NAVBAR_HEIGHT = 100
FPS = 70
BACKGROUND = pygame.image.load("./space_bg.png")
pygame.display.set_caption('Newtonian Mechanics simulator')
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
MINT = (204, 255, 229)
TRAIL_COLORS = [MINT, PINK, ORANGE, PURPLE, GREEN, RED]

def totalEnergy(bodies):
	E = 0
	for body in bodies:
		v = body.getVelocity()
		E += (body.mass/2) * (v ** 2)
	return round(E, 2)


def inflate(x, y, time): # Inflate body
    pygame.draw.circle(WIN, WHITE, (x, y), 10*time, 0)
    
    (currpos_x, currpos_y) = pygame.mouse.get_pos()
	
    aim_pos = (2*x - currpos_x, 2*y - currpos_y)
	

    pygame.draw.line(WIN, MINT, (x, y), aim_pos, width=2)


# Main game loop
def main():
	clock = pygame.time.Clock()
	bodies = []
	frame = 0
	draw_timer = 0
	G = 40

	TRAIL_SHOWN = True
	DRAWING = False
	DECAY_ACTIVE = False
	COLLISION_ABSORB = True
	PAUSE = False

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
				DRAWING = True

			elif event.type == pygame.MOUSEBUTTONUP:
				mouse_end = pygame.mouse.get_pos()
				drag = mouse_start[0] - mouse_end[0], mouse_start[1] - mouse_end[1]
				x_vel, y_vel = drag
        
				#Add drawn body
				if draw_timer > 0.5:
					bodies.append(
					Body(mouse_start[0], mouse_start[1], 10*draw_timer, 10*draw_timer ** 4,
					x_vel, y_vel, TRAIL_COLORS[len(bodies)%len(TRAIL_COLORS)]))

					bodies[-1].time_of_creation = frame

				draw_timer = 0
				DRAWING = False
      
			#Keyboard input
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_r:
					bodies.clear()

				elif event.key == pygame.K_t:
					TRAIL_SHOWN = not TRAIL_SHOWN

				elif event.key == pygame.K_PLUS:
					G += 100

				elif event.key == pygame.K_MINUS:
					G -= 100
					if G < 0:
						G = 0
				elif event.key == pygame.K_p:
					PAUSE = not PAUSE

				elif event.key == pygame.K_d:
					DECAY_ACTIVE = not DECAY_ACTIVE
	
				elif event.key == pygame.K_c:
					COLLISION_ABSORB = not COLLISION_ABSORB

		if DRAWING:
			draw_timer += 1/FPS
			inflate(mouse_start[0], mouse_start[1], draw_timer)

		# Update data of bodies
		for body in bodies:
			if PAUSE:
				WIN.blit(while_paused_text, (WINDOW_WIDTH//2 - 30, WINDOW_HEIGHT//2))
				body.drawBody()
				body.drawVelVector()
				body.drawData(font)
				if TRAIL_SHOWN:
					body.drawTrail()
				continue

			body.updateVelocity(bodies, G, COLLISION_ABSORB)
			body.updatePosition()
			body.drawBody()
			body.drawVelVector()
			body.drawData(font)
					
			if frame%(FPS//25) == 1:
				body.addTrailpoint()

			if TRAIL_SHOWN:
				body.drawTrail()
      
			if DECAY_ACTIVE:
				body.massDecay(frame, bodies)

			# Bounce of walls
			if body.y + body.y_vel*(1/FPS) - body.radius < NAVBAR_HEIGHT or body.y + body.y_vel*(1/FPS) + body.radius > WINDOW_HEIGHT:
				body.y_vel = -body.y_vel

			if body.x + body.x_vel*(1/FPS) - body.radius < 0 or body.x + body.x_vel*(1/FPS) + body.radius > WINDOW_WIDTH:
				body.x_vel = -body.x_vel

		pygame.display.update()

if __name__ == '__main__':
  main()