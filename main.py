import pygame
from pygame import Surface

W_WIDTH = 900
W_HEIGHT = 600
FRAMERATE = 60
BACKGROUND_COLOR = "black"
SOLID_COLOR = "white"
WATER_COLOR = "darkslategray1"
GRID_COLOR = "gray"
GRID_THICKNESS = 1
ROWS = 60
COLUMNS = 60
EMPTY_STATE = 0
SOLID_STATE = 1
WATER_STATE = 2
MAX_WATER_LEVEL = 1
INITIAL_WATER_LEVEL = 2
MIN_WATER_LEVEL = 0.005
GRID = False

pygame.init()
pygame.display.set_caption("Water Simulation")
surface = pygame.display.set_mode((W_WIDTH, W_HEIGHT))
clock = pygame.time.Clock()
block_width = W_WIDTH / COLUMNS
block_height = W_HEIGHT / ROWS
water_base_color = pygame.Color(WATER_COLOR)

class Block():
	def __init__(self, x, y):
		self.state = EMPTY_STATE
		self.water_level = 0
		self.x_pos = x
		self.y_pos = y
		self.flow_directions = []

	def draw(self):
		if self.state == WATER_STATE:
			# if self.water_level>MAX_WATER_LEVEL: print(self.water_level)
			water_color = "dodgerblue4" if self.water_level>MAX_WATER_LEVEL else water_base_color.lerp("dodgerblue4", self.water_level/MAX_WATER_LEVEL)

			if len(self.flow_directions) == 1 and self.flow_directions[0] == "down":
				pygame.draw.rect(surface, water_color, pygame.Rect(self.x_pos, self.y_pos, block_width, block_height))
			else:
				water_height = block_height if self.water_level>MAX_WATER_LEVEL else block_height*(self.water_level/MAX_WATER_LEVEL)
				pygame.draw.rect(surface, water_color, pygame.Rect(self.x_pos, self.y_pos+(block_height-water_height), block_width, water_height))

			for direction in self.flow_directions:
				# draw an arrow from the center of the block to the direction
				block_mid_x = self.x_pos + block_width / 2
				block_mid_y = self.y_pos + block_height / 2
				arrow_length_horizontal = (block_width / 2) * 0.9
				arrow_length_vertical = (block_height / 2) * 0.9
				arrow_height = block_height / 4
				arrow_width = block_width / 6
				arrow_rect_length_horizontal = arrow_length_horizontal * 0.6
				arrow_rect_length_vertical = arrow_length_vertical * 0.6
				arrow_color = "red"

				if direction == "left":
					pygame.draw.polygon(surface, arrow_color,
						[
							(block_mid_x, block_mid_y-arrow_height/4),
							(block_mid_x, block_mid_y+arrow_height/4),
							(block_mid_x-arrow_rect_length_horizontal, block_mid_y+arrow_height/4),
							(block_mid_x-arrow_rect_length_horizontal, block_mid_y+arrow_height/2),
							(block_mid_x-arrow_length_horizontal, block_mid_y),
							(block_mid_x-arrow_rect_length_horizontal, block_mid_y-arrow_height/2),
							(block_mid_x-arrow_rect_length_horizontal, block_mid_y-arrow_height/4),
						]
					)

				elif direction == "right":
					pygame.draw.polygon(surface, arrow_color,
						[
							(block_mid_x, block_mid_y-arrow_height/4),
							(block_mid_x, block_mid_y+arrow_height/4),
							(block_mid_x+arrow_rect_length_horizontal, block_mid_y+arrow_height/4),
							(block_mid_x+arrow_rect_length_horizontal, block_mid_y+arrow_height/2),
							(block_mid_x+arrow_length_horizontal, block_mid_y),
							(block_mid_x+arrow_rect_length_horizontal, block_mid_y-arrow_height/2),
							(block_mid_x+arrow_rect_length_horizontal, block_mid_y-arrow_height/4),
						]
					)

				elif direction == "up":
					pygame.draw.polygon(surface, arrow_color,
						[
							(block_mid_x-arrow_width/4, block_mid_y),
							(block_mid_x+arrow_width/4, block_mid_y),
							(block_mid_x+arrow_width/4, block_mid_y-arrow_rect_length_vertical),
							(block_mid_x+arrow_width/2, block_mid_y-arrow_rect_length_vertical),
							(block_mid_x, block_mid_y-arrow_length_vertical),
							(block_mid_x-arrow_width/2, block_mid_y-arrow_rect_length_vertical),
							(block_mid_x-arrow_width/4, block_mid_y-arrow_rect_length_vertical),
						]
					)

				elif direction == "down":
					pygame.draw.polygon(surface, arrow_color,
						[
							(block_mid_x-arrow_width/4, block_mid_y),
							(block_mid_x+arrow_width/4, block_mid_y),
							(block_mid_x+arrow_width/4, block_mid_y+arrow_rect_length_vertical),
							(block_mid_x+arrow_width/2, block_mid_y+arrow_rect_length_vertical),
							(block_mid_x, block_mid_y+arrow_length_vertical),
							(block_mid_x-arrow_width/2, block_mid_y+arrow_rect_length_vertical),
							(block_mid_x-arrow_width/4, block_mid_y+arrow_rect_length_vertical),
						]
					)

		else:
			pygame.draw.rect(surface, SOLID_COLOR, pygame.Rect(self.x_pos, self.y_pos, block_width, block_height))

def draw_grid():
	w_height = surface.get_height()
	w_width = surface.get_width()

	for r in range(1, ROWS):
		pygame.draw.rect(surface, GRID_COLOR, (0, r * (w_height / ROWS), w_width, GRID_THICKNESS))

	for c in range(1, COLUMNS):
		pygame.draw.rect(surface, GRID_COLOR, (c * (w_width / COLUMNS), 0, GRID_THICKNESS, w_height))

def draw_blocks(blocks: list[list[Block]]):
	for r in range(ROWS):
		for c in range(COLUMNS):
			block = blocks[r][c]

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
		if not block.state == SOLID_STATE:
			block.state = WATER_STATE
			block.water_level += INITIAL_WATER_LEVEL
			return WATER_STATE

def handle_mouse_move(event, blocks: list[list[Block]], draw_mode):
	(button1, _, _) = event.buttons

	x, y = event.pos
	block_r, block_c = int(y / block_height), int(x / block_width)
	block = blocks[block_r][block_c]

	if button1:
		if draw_mode == SOLID_STATE:
			block.state = SOLID_STATE
		elif draw_mode == EMPTY_STATE and block.state == SOLID_STATE:
			block.state = EMPTY_STATE
	elif draw_mode == WATER_STATE:
		block.state = WATER_STATE
		block.water_level += INITIAL_WATER_LEVEL

def simulate_fluid(blocks: list[list[Block]]):
	for r in range(ROWS-1, -1, -1):  # Process rows from bottom to top
		for c in range(COLUMNS):
			block = blocks[r][c]

			block.flow_directions = []

			if block.state == SOLID_STATE or block.state == EMPTY_STATE:
				block.water_level = 0
				continue

			if block.water_level < MIN_WATER_LEVEL:
				block.state = EMPTY_STATE
				block.water_level = 0
				continue

			if r < ROWS - 1:  # Check the block below
				block_below = blocks[r + 1][c]

				if not (block_below.state==SOLID_STATE or block_below.water_level>=MAX_WATER_LEVEL):
					block.flow_directions.append("down")

					if block_below.state == EMPTY_STATE:
						block_below.state = WATER_STATE
						water_flow = block.water_level
						block_below.water_level += water_flow
						block.water_level -= water_flow
					# elif block_below.water_level < block.water_level:
					else:
						empty_space_below = MAX_WATER_LEVEL - block_below.water_level
						water_flow = min(block.water_level, empty_space_below)
						block_below.water_level += water_flow
						block.water_level -= water_flow

			if block.water_level < MIN_WATER_LEVEL:
				block.state = EMPTY_STATE
				block.water_level = 0
				continue

			if c > 0:  # Check the block to the left
				block_left = blocks[r][c - 1]

				if not (block_left.state == SOLID_STATE or block_left.water_level >= MAX_WATER_LEVEL):
					block.flow_directions.append("left")

					if block_left.state == EMPTY_STATE:
						block_left.state = WATER_STATE
						water_flow = (block.water_level - block_left.water_level) / 4
						block_left.water_level += water_flow
						block.water_level -= water_flow
					elif block_left.water_level < block.water_level:
						water_flow = (block.water_level - block_left.water_level) / 4
						block_left.water_level += water_flow
						block.water_level -= water_flow

			if block.water_level < MIN_WATER_LEVEL:
				block.state = EMPTY_STATE
				block.water_level = 0
				continue

			if c < COLUMNS - 1:  # Check the block to the right
				block_right = blocks[r][c + 1]

				if not (block_right.state == SOLID_STATE or block_right.water_level >= MAX_WATER_LEVEL):
					block.flow_directions.append("right")

					if block_right.state == EMPTY_STATE:
						block_right.state = WATER_STATE
						water_flow = (block.water_level - block_right.water_level) / 3
						block_right.water_level += water_flow
						block.water_level -= water_flow
					elif block_right.water_level < block.water_level:
						water_flow = (block.water_level - block_right.water_level) / 3
						block_right.water_level += water_flow
						block.water_level -= water_flow

			if block.water_level < MIN_WATER_LEVEL:
				block.state = EMPTY_STATE
				block.water_level = 0
				continue

			if r > 0:
				block_above = blocks[r - 1][c]

				if block_above.state != SOLID_STATE and block.water_level > MAX_WATER_LEVEL:
					block.flow_directions.append("up")

					water_excess = (block.water_level - MAX_WATER_LEVEL) / 4
					block_above.state = WATER_STATE
					block_above.water_level += water_excess
					block.water_level -= water_excess

			if block.water_level < MIN_WATER_LEVEL:
				block.state = EMPTY_STATE
				block.water_level = 0

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

		if GRID: draw_grid()
		simulate_fluid(blocks)
		draw_blocks(blocks)

		pygame.display.flip()
		clock.tick(FRAMERATE)

	pygame.quit()

if __name__ == '__main__':
	main()