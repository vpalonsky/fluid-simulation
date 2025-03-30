import pygame
import copy

W_WIDTH = 900
W_HEIGHT = 600
FRAMERATE = 15
BACKGROUND_COLOR = "black"
GRID_COLOR = "gray"
SOLID_COLOR = "white"
WATER_COLOR = "darkslategray1"
PRESSURISED_WATER_COLOR = "dodgerblue4"
GRID_THICKNESS = 1
ROWS = 30
COLUMNS = 30
EMPTY_STATE = 0
SOLID_STATE = 1
WATER_STATE = 2
MAX_WATER_LEVEL = 1
MIN_WATER_LEVEL = MAX_WATER_LEVEL/10
SIDEWAYS_FLOW_PORTION = 4
UPWARDS_FLOW_PORTION = 10

pygame.init()
surface = pygame.display.set_mode((W_WIDTH, W_HEIGHT))
clock = pygame.time.Clock()
block_width = W_WIDTH/COLUMNS
block_height = W_HEIGHT/ROWS
water_base_color = pygame.Color(WATER_COLOR)

class Block():
	def __init__(self, x, y):
		self.state = EMPTY_STATE
		self.water_level = 0
		self.x_pos = x
		self.y_pos = y
		self.falling = False

	def draw(self, empty_above):
		if (self.state==WATER_STATE):
			if self.water_level<0: return

			water_color = PRESSURISED_WATER_COLOR
			if self.water_level<=MAX_WATER_LEVEL: water_color = water_base_color.lerp(PRESSURISED_WATER_COLOR, self.water_level/MAX_WATER_LEVEL)

			if (self.falling):
				water_height = block_height if self.water_level > MAX_WATER_LEVEL else block_height*(self.water_level/MAX_WATER_LEVEL)
				pygame.draw.rect(surface, water_color, pygame.Rect(self.x_pos, self.y_pos+(block_height-water_height), block_width, water_height))
			else:
				pygame.draw.rect(surface, water_color, pygame.Rect(self.x_pos, self.y_pos, block_width, block_height))

			# water_height = block_height if self.water_level > MAX_WATER_LEVEL else block_height*(self.water_level/MAX_WATER_LEVEL)
			# pygame.draw.rect(surface, water_color, pygame.Rect(self.x_pos, self.y_pos+(block_height-water_height), block_width, water_height))

		elif (self.state==SOLID_STATE):
			pygame.draw.rect(surface, SOLID_COLOR, pygame.Rect(self.x_pos, self.y_pos, block_width, block_height))


def draw_grid():
	for c in range(1, COLUMNS):
		col_x = block_width*c
		pygame.draw.rect(surface, GRID_COLOR, pygame.Rect(col_x, 0, GRID_THICKNESS, W_HEIGHT))

	for r in range(1, ROWS):
		row_y = block_height*r
		pygame.draw.rect(surface, GRID_COLOR, pygame.Rect(0, row_y, W_WIDTH, GRID_THICKNESS))


def draw_blocks(blocks):
	for r in range(ROWS):
		for c in range(COLUMNS):
			block = blocks[r][c]
			empty_above = True

			if (block.state==WATER_STATE and r>0):
				if (blocks[r-1][c].state==WATER_STATE and blocks[r-1][c].water_level>=MIN_WATER_LEVEL):
					empty_above = False

			if (block.falling): print("Falling")

			block.draw(empty_above)


def change_block_state(blocks, mouse_pos, button, draw_state):
	if button==2: return

	(mouse_x, mouse_y) = mouse_pos
	block_row = int(mouse_y//block_height)
	block_col = int(mouse_x//block_width)

	if button==1:
		if draw_state==WATER_STATE:
			blocks[block_row][block_col].state = WATER_STATE
			blocks[block_row][block_col].water_level += MAX_WATER_LEVEL
		else:
			blocks[block_row][block_col].state = SOLID_STATE
	else:
		if blocks[block_row][block_col].state==SOLID_STATE:	blocks[block_row][block_col].state = EMPTY_STATE


def apply_rule1(block, block_below, next_block, next_block_below):
	next_block_below.falling = False
	if block_below.state==EMPTY_STATE:
		# next_block_below.state = WATER_STATE
		next_block_below.water_level += block.water_level
		next_block.water_level -= block.water_level
	else:
		empty_space_below = MAX_WATER_LEVEL - block_below.water_level

		if (empty_space_below>=block.water_level):
			next_block_below.water_level += block.water_level
			next_block.water_level -= block.water_level
		else:
			next_block_below.water_level += empty_space_below
			next_block_below.falling = True
			next_block.water_level -= empty_space_below

def apply_rule2_left(block_left, block, next_block_left, next_block):
	# if block_left.state==EMPTY_STATE: next_block_left.state = WATER_STATE
	water_diff = block.water_level-block_left.water_level
	next_block_left.water_level += water_diff/4
	next_block.water_level -= water_diff/4

def apply_rule2_right(block, block_right, next_block, next_block_right):
	# if block_right.state==EMPTY_STATE: next_block_right.state = WATER_STATE
	water_diff = block.water_level-block_right.water_level
	next_block_right.water_level += water_diff/4
	next_block.water_level -= water_diff/4

def apply_rule3(block, block_above, next_block, next_block_above):
	# if block_above.state==EMPTY_STATE: next_block_above.state = WATER_STATE
	water_diff = block.water_level-block_above.water_level
	next_block_above.water_level += water_diff/10
	next_block.water_level -= water_diff/10



def simulate_fluid(blocks):
	next_blocks = copy.deepcopy(blocks)

	for r in range(ROWS):
		for c in range(COLUMNS):
			block = blocks[r][c]
			if (block.state==WATER_STATE):
				if (r<ROWS-1 and next_blocks[r][c].water_level>=MIN_WATER_LEVEL):
					block_below = blocks[r+1][c]
					if (block_below.state==EMPTY_STATE or (block_below.state==WATER_STATE and block_below.water_level<block.water_level)):
						apply_rule1(blocks[r][c], blocks[r+1][c], next_blocks[r][c], next_blocks[r+1][c])

						if next_blocks[r+1][c].state==EMPTY_STATE and next_blocks[r+1][c].water_level>=MIN_WATER_LEVEL:
							next_blocks[r+1][c].state=WATER_STATE

				if (c>0 and next_blocks[r][c].water_level>=MIN_WATER_LEVEL):
					block_left = blocks[r][c-1]
					if (block_left.state==EMPTY_STATE or (block_left.state==WATER_STATE and block_left.water_level<block.water_level)):
						apply_rule2_left(blocks[r][c-1], blocks[r][c], next_blocks[r][c-1], next_blocks[r][c])

						if next_blocks[r][c-1].state==EMPTY_STATE and next_blocks[r][c-1].water_level>=MIN_WATER_LEVEL:
							next_blocks[r][c-1].state=WATER_STATE

				if (c<COLUMNS-1 and next_blocks[r][c].water_level>=MIN_WATER_LEVEL):
					block_right = blocks[r][c+1]
					if (block_right.state==EMPTY_STATE or (block_right.state==WATER_STATE and block_right.water_level<block.water_level)):
						apply_rule2_right(blocks[r][c], blocks[r][c+1], next_blocks[r][c], next_blocks[r][c+1])

						if next_blocks[r][c+1].state==EMPTY_STATE and next_blocks[r][c+1].water_level>=MIN_WATER_LEVEL:
							next_blocks[r][c+1].state=WATER_STATE

				if (r>0 and next_blocks[r][c].water_level>=MIN_WATER_LEVEL):
					block_above = blocks[r-1][c]
					if (block.water_level>MAX_WATER_LEVEL and (block_above.state==EMPTY_STATE or (block_above.state==WATER_STATE and block_above.water_level<block.water_level))):
						apply_rule3(blocks[r][c], blocks[r-1][c], next_blocks[r][c], next_blocks[r-1][c])

						if next_blocks[r-1][c].state==EMPTY_STATE and next_blocks[r-1][c].water_level>=MIN_WATER_LEVEL:
							next_blocks[r-1][c].state=WATER_STATE

				if next_blocks[r][c].water_level<MIN_WATER_LEVEL:
					next_blocks[r][c].state=EMPTY_STATE

	for r in range(ROWS):
		for c in range(COLUMNS):
			blocks[r][c] = next_blocks[r][c]
			blocks[r][c].water_level = max(0, min(blocks[r][c].water_level, MAX_WATER_LEVEL))


def initialize_blocks():
	first_blocks = []

	for r in range(ROWS):
		row = []
		for c in range(COLUMNS):
			row.append(Block(block_width*c, block_height*r))
		first_blocks.append(row)

	return first_blocks


def main():
	blocks = initialize_blocks()
	running = True
	simulation = True
	draw_state = SOLID_STATE

	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False
				if event.key == pygame.K_SPACE:
					draw_state = WATER_STATE if draw_state==SOLID_STATE else SOLID_STATE
				if event.key == pygame.K_s:
					simulation = not simulation
			if event.type == pygame.MOUSEMOTION:
				(button1, _, button3) = event.buttons
				button = 2
				if button1==1: button=1
				elif button3==1: button=3
				change_block_state(blocks, event.pos, button, draw_state)

		surface.fill(BACKGROUND_COLOR)

		draw_grid()

		if (simulation): simulate_fluid(blocks)

		draw_blocks(blocks)
		pygame.display.flip()

		clock.tick(FRAMERATE)

	pygame.quit()


if __name__ == '__main__':
	main()