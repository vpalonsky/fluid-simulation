import pygame
from pygame import Surface

W_WIDTH = 900
W_HEIGHT = 600
FRAMERATE = 15
BACKGROUND_COLOR = "black"
SOLID_COLOR = "white"
WATER_COLOR = "darkslategray1"
GRID_COLOR = "gray"
GRID_THICKNESS = 1
ROWS = 30
COLUMNS = 30
EMPTY_STATE = 0
SOLID_STATE = 1
WATER_STATE = 2
MAX_WATER_LEVEL = 1
MIN_WATER_LEVEL = MAX_WATER_LEVEL / 100

pygame.init()
pygame.display.set_caption("Water Simulation")
surface = pygame.display.set_mode((W_WIDTH, W_HEIGHT))
clock = pygame.time.Clock()
block_width = W_WIDTH / COLUMNS
block_height = W_HEIGHT / ROWS

class Block():
	def __init__(self, x, y):
		self.state = EMPTY_STATE
		self.water_level = 0
		self.x_pos = x
		self.y_pos = y

	def draw(self):
		if self.state == WATER_STATE:
			water_height = block_height if self.water_level > MAX_WATER_LEVEL else block_height*(self.water_level/MAX_WATER_LEVEL)
			pygame.draw.rect(surface, WATER_COLOR, pygame.Rect(self.x_pos, self.y_pos+(block_height-water_height), block_width, water_height))
		else:
			pygame.draw.rect(surface, SOLID_COLOR, pygame.Rect(self.x_pos, self.y_pos, block_width, block_height))

def draw_grid(surface: Surface, rows, columns, grid_color, grid_thickness):
	w_height = surface.get_height()
	w_width = surface.get_width()

	for r in range(1, rows):
		pygame.draw.rect(surface, grid_color, (0, r * (w_height / rows), w_width, grid_thickness))

	for c in range(1, columns):
		pygame.draw.rect(surface, grid_color, (c * (w_width / columns), 0, grid_thickness, w_height))

def draw_blocks(blocks: list[list[Block]]):
	for row in blocks:
		for block in row:
			if block.state == EMPTY_STATE:
				continue
			block.draw()

def handle_mouse_down(event, blocks: list[list[Block]]):
	x, y = event.pos
	block_r, block_c = int(y / block_height), int(x / block_width)
	block = blocks[block_r][block_c]
	if event.button == 1:  # Left mouse button
		if block.state == EMPTY_STATE:
			block.state = SOLID_STATE
			return SOLID_STATE
		else:
			block.state = EMPTY_STATE
			return EMPTY_STATE
	else:  # Right mouse button
		if block.state == EMPTY_STATE:
			block.state = WATER_STATE
			block.water_level = MAX_WATER_LEVEL
			return WATER_STATE

def handle_mouse_move(event, blocks: list[list[Block]], draw_mode):
	(button1, _, button3) = event.buttons

	x, y = event.pos
	block_r, block_c = int(y / block_height), int(x / block_width)
	block = blocks[block_r][block_c]

	if button1:
		if draw_mode == SOLID_STATE and block.state == EMPTY_STATE:
			block.state = SOLID_STATE
		elif draw_mode == EMPTY_STATE and block.state == SOLID_STATE:
			block.state = EMPTY_STATE
	elif block.state == EMPTY_STATE:
			block.state = WATER_STATE
			block.water_level = MAX_WATER_LEVEL

def main():
	blocks = [[Block(c * block_width, r * block_height) for c in range(COLUMNS)] for r in range(ROWS)]
	running = True
	draw_mode = SOLID_STATE

	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 2: return
				draw_mode = handle_mouse_down(event, blocks)
			elif event.type == pygame.MOUSEMOTION:
				if event.buttons[1]: return
				if event.buttons[0] or event.buttons[2]:
					handle_mouse_move(event, blocks, draw_mode)

		surface.fill(BACKGROUND_COLOR)

		draw_grid(surface, ROWS, COLUMNS, GRID_COLOR, GRID_THICKNESS)
		draw_blocks(blocks)

		pygame.display.flip()
		clock.tick(FRAMERATE)

	pygame.quit()

if __name__ == '__main__':
	main()