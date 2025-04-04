import pygame
import copy

W_WIDTH = 900
W_HEIGHT = 600
FRAMERATE = 30
BACKGROUND_COLOR = "black"
GRID_COLOR = "gray"
SOLID_COLOR = "white"
WATER_COLOR = "darkslategray1"
PRESSURISED_WATER_COLOR = "dodgerblue4"
GRID_THICKNESS = 1
ROWS = 30
COLUMNS = 45
EMPTY_STATE = 0
SOLID_STATE = 1
WATER_STATE = 2
FULL_WATER_LEVEL = 1
INITIAL_WATER_LEVEL = FULL_WATER_LEVEL
WATER_LEVELUP = 0.1
SIDEWAYS_FLOW_PORTION = 4
UPWARDS_FLOW_PORTION = 3

pygame.init()
surface = pygame.display.set_mode((W_WIDTH, W_HEIGHT))
clock = pygame.time.Clock()
block_width = W_WIDTH/COLUMNS
block_height = W_HEIGHT/ROWS
water_base_color = pygame.Color(WATER_COLOR)
sideways_water = FULL_WATER_LEVEL/SIDEWAYS_FLOW_PORTION

def draw_grid():
	for c in range(1, COLUMNS):
		col_x = block_width*c
		pygame.draw.rect(surface, GRID_COLOR, pygame.Rect(col_x, 0, GRID_THICKNESS, W_HEIGHT))

	for r in range(1, ROWS):
		row_y = block_height*r
		pygame.draw.rect(surface, GRID_COLOR, pygame.Rect(0, row_y, W_WIDTH, GRID_THICKNESS))

class Block():
	def __init__(self, x, y):
		self.state = EMPTY_STATE
		self.water_level = 0
		self.x_pos = x
		self.y_pos = y

	def draw(self, empty_above):
		if (self.state==WATER_STATE and self.water_level>0.0):
			water_color = "darkslateblue" if self.water_level>FULL_WATER_LEVEL else water_base_color.lerp(PRESSURISED_WATER_COLOR, self.water_level/FULL_WATER_LEVEL)

			# if (empty_above and self.water_level>0):
			# 	water_height = block_height*FULL_WATER_LEVEL if self.water_level >= FULL_WATER_LEVEL else block_height*self.water_level
			# 	pygame.draw.rect(surface, water_color, pygame.Rect(self.x_pos, self.y_pos+(block_height-water_height), block_width, water_height))
			# else:
			# 	pygame.draw.rect(surface, water_color, pygame.Rect(self.x_pos, self.y_pos, block_width, block_height))

			water_height = block_height*FULL_WATER_LEVEL if self.water_level >= FULL_WATER_LEVEL else block_height*self.water_level
			pygame.draw.rect(surface, water_color, pygame.Rect(self.x_pos, self.y_pos+(block_height-water_height), block_width, water_height))

		elif (self.state==SOLID_STATE):
			pygame.draw.rect(surface, SOLID_COLOR, pygame.Rect(self.x_pos, self.y_pos, block_width, block_height))

def draw_blocks(blocks):
	for r in range(ROWS):
		for c in range(COLUMNS):
			block = blocks[r][c]
			empty_above = False

			if (block.state==WATER_STATE):
				if (r>0):
					block_above = blocks[r-1][c]
					if (block_above.state==EMPTY_STATE or block_above.water_level<=0):
						empty_above = True

			block.draw(empty_above)

def change_block_state(blocks, mouse_pos, button, draw_state):
	if button==2: return

	(mouse_x, mouse_y) = mouse_pos
	block_row = int(mouse_y//block_height)
	block_col = int(mouse_x//block_width)

	# print(blocks[block_row][block_col].water_level)
	if button==1:
		if draw_state==WATER_STATE:
			# if blocks[block_row][block_col].state==WATER_STATE:
			# 	blocks[block_row][block_col].water_level+=WATER_LEVELUP
			# elif blocks[block_row][block_col].state==EMPTY_STATE:
			blocks[block_row][block_col].state = WATER_STATE
			blocks[block_row][block_col].water_level = INITIAL_WATER_LEVEL
		else:
			blocks[block_row][block_col].state = SOLID_STATE
	else:
		if blocks[block_row][block_col].state==SOLID_STATE:	blocks[block_row][block_col].state = EMPTY_STATE

def apply_rule1(block, block_below, next_block, next_block_below):
	if block_below.state==EMPTY_STATE:
		next_block_below.state = WATER_STATE
		next_block_below.water_level += block.water_level
		next_block.state = EMPTY_STATE
	else:
		empty_space_below = FULL_WATER_LEVEL - block_below.water_level

		if (empty_space_below>=block.water_level):
			next_block_below.water_level += block.water_level
			next_block.state = EMPTY_STATE
		else:
			next_block_below.water_level += empty_space_below
			next_block.water_level -= empty_space_below

def apply_rule2(block_left, block, block_right, next_block_left, next_block, next_block_right):
	block_left_water_flow = 0
	block_water_flow = 0
	block_right_water_flow = 0

	if (block_left.state==EMPTY_STATE):
		block_left.state = WATER_STATE

		if (block_right.state==EMPTY_STATE):
			block_right.state = WATER_STATE

			water_flow = block.water_level/SIDEWAYS_FLOW_PORTION

			block_left_water_flow=water_flow
			block_water_flow=-2*water_flow
			block_right_water_flow=water_flow

		elif (block_right.state==SOLID_STATE):
			water_flow = block.water_level/SIDEWAYS_FLOW_PORTION

			block_left_water_flow=water_flow
			block_water_flow=-water_flow

		else:
			if (block_right.water_level<block.water_level):
				water_diff = block.water_level-block_right.water_level
				water_flow_right = water_diff/SIDEWAYS_FLOW_PORTION
				water_flow_left = (block.water_level-water_flow_right)/SIDEWAYS_FLOW_PORTION

				block_left_water_flow=water_flow_left
				block_water_flow=-(water_flow_left+water_flow_right)
				block_right_water_flow=water_flow_right
			else:
				water_flow = block.water_level/SIDEWAYS_FLOW_PORTION

				block_left_water_flow=water_flow
				block_water_flow=-water_flow

	elif (block_left.state==SOLID_STATE):
		if (block_right.state==EMPTY_STATE):
			block_right.state = WATER_STATE

			water_flow = block.water_level/SIDEWAYS_FLOW_PORTION

			block_water_flow=-water_flow
			block_right_water_flow=water_flow
		else:
			water_diff = block.water_level-block_right.water_level
			water_flow = water_diff/SIDEWAYS_FLOW_PORTION

			block_water_flow=-water_flow
			block_right_water_flow=water_flow

	else:
		if (block_left.water_level<block.water_level):
			if (block_right.state==EMPTY_STATE):
				block_right.state = WATER_STATE

				water_diff = block.water_level-block_left.water_level
				water_flow_left = water_diff/SIDEWAYS_FLOW_PORTION
				water_flow_right = (block.water_level-water_flow_left)/SIDEWAYS_FLOW_PORTION

				block_left_water_flow=water_flow_left
				block_water_flow=-(water_flow_left+water_flow_right)
				block_right_water_flow=water_flow_right
			elif (block_right.state==SOLID_STATE):
				water_diff = block.water_level-block_left.water_level
				water_flow = water_diff/SIDEWAYS_FLOW_PORTION

				block_left_water_flow=water_flow
				block_water_flow=-water_flow
			else:
				if (block_right.water_level<block.water_level):
					water_diff_left = block.water_level-block_left.water_level
					water_diff_right = block.water_level-block_right.water_level
					water_flow_left = water_diff_left/SIDEWAYS_FLOW_PORTION
					water_flow_right = water_diff_right/SIDEWAYS_FLOW_PORTION

					block_left_water_flow=water_flow_left
					block_water_flow=-(water_flow_left+water_flow_right)
					block_right_water_flow=water_flow_right
				else:
					water_diff = block.water_level-block_left.water_level
					water_flow = water_diff/SIDEWAYS_FLOW_PORTION

					block_left_water_flow=water_flow
					block_water_flow=-water_flow
		else:
			if (block_right.state==EMPTY_STATE):
				block_right.state = WATER_STATE

				water_flow = block.water_level/SIDEWAYS_FLOW_PORTION

				block_water_flow=-water_flow
				block_right_water_flow=water_flow
			else:
				water_diff = block.water_level-block_right.water_level
				water_flow = water_diff/SIDEWAYS_FLOW_PORTION

				block_water_flow=-water_flow
				block_right_water_flow=water_flow

	next_block_left.water_level += block_left_water_flow
	next_block.water_level += block_water_flow
	next_block_right.water_level += block_right_water_flow

# def apply_rule3(block, block_above):
# 	if (block_above.state==EMPTY_STATE):
# 		block_above.state = WATER_STATE

# 	water_flow = block.water_level/UPWARDS_FLOW_PORTION

# 	block_above.water_level+=water_flow
# 	block.water_level-=water_flow

	# if next_block.water_level<=0:
	# 	next_block.state=EMPTY_STATE
	# 	next_block.water_level=0


def simulate_fluid(blocks):
	next_blocks = copy.deepcopy(blocks)

	# for r in range(ROWS):
	# 	for c in range(COLUMNS):
	# 		block = blocks[r][c]

			# if (block.state==WATER_STATE):
			# 	if (r<ROWS-1):
			# 		block_below = blocks[r+1][c]
			# 		if (block_below.state==EMPTY_STATE or (block_below.state==WATER_STATE and block_below.water_level<=block.water_level)):
			# 			apply_rule1(next_blocks[r][c], next_blocks[r+1][c])

			# 		elif (c>0 and c<COLUMNS-1):
			# 			block_left = blocks[r][c-1]
			# 			block_right = blocks[r][c+1]

			# 			if (block_left.state==EMPTY_STATE or block_right.state==EMPTY_STATE or (block_left.state==WATER_STATE and block_left.water_level<block.water_level) or (block_right.state==WATER_STATE and block_right.water_level<block.water_level)):
			# 				apply_rule2(next_blocks[r][c-1], next_blocks[r][c], next_blocks[r][c+1])

			# 		# elif (r>0):
			# 		# 	block_above = blocks[r-1][c]

			# 		# 	if (block.water_level>FULL_WATER_LEVEL and block_above.state!=SOLID_STATE and block_above.water_level<block.water_level):
			# 		# 		apply_rule3(next_blocks[r][c], next_blocks[r-1][c])

			# 	elif (c>0 and c<COLUMNS-1):
			# 			block_left = blocks[r][c-1]
			# 			block_right = blocks[r][c+1]

			# 			if (block_left.state==EMPTY_STATE or block_right.state==EMPTY_STATE or (block_left.state==WATER_STATE and block_left.water_level<block.water_level) or (block_right.state==WATER_STATE and block_right.water_level<block.water_level)):
			# 				apply_rule2(next_blocks[r][c-1], next_blocks[r][c], next_blocks[r][c+1])

			# 			# elif (r>0):
			# 			# 	block_above = blocks[r-1][c]

			# 			# 	if (block.water_level>FULL_WATER_LEVEL and block_above.state!=SOLID_STATE and block_above.water_level<block.water_level):
			# 			# 		apply_rule3(next_blocks[r][c], next_blocks[r-1][c])

			# 	# elif (r>0):
			# 	# 	block_above = blocks[r-1][c]

			# 	# 	if (block.water_level>FULL_WATER_LEVEL and block_above.state!=SOLID_STATE and block_above.water_level<block.water_level):
			# 	# 		apply_rule3(next_blocks[r][c], next_blocks[r-1][c])

	for r in range(ROWS):
		for c in range(COLUMNS):
			block = blocks[r][c]
			if (block.state==WATER_STATE):
				if (r<ROWS-1):
					block_below = blocks[r+1][c]
					if (block_below.state==EMPTY_STATE or (block_below.state==WATER_STATE and block_below.water_level<block.water_level)):
						apply_rule1(blocks[r][c], blocks[r+1][c], next_blocks[r][c], next_blocks[r+1][c])

				# if (c>0 and c<COLUMNS-1):
				# 	block_left = blocks[r][c-1]
				# 	block_right = blocks[r][c+1]

				# 	if (block_left.state==EMPTY_STATE or block_right.state==EMPTY_STATE or (block_left.state==WATER_STATE and block_left.water_level<block.water_level) or (block_right.state==WATER_STATE and block_right.water_level<block.water_level)):
				# 		apply_rule2(blocks[r][c-1], blocks[r][c], blocks[r][c+1], next_blocks[r][c-1], next_blocks[r][c], next_blocks[r][c+1])

	for r in range(ROWS):
		for c in range(COLUMNS):
			# next_block = next_blocks[r][c]
			# if next_block.state==WATER_STATE and next_block.water_level<=FULL_WATER_LEVEL/10:
			# 	next_block.state=EMPTY_STATE
				# next_block.water_level=0
			# blocks[r][c] = next_block

			blocks[r][c] = next_blocks[r][c]

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
	draw_state = SOLID_STATE
	simulation = True

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
		draw_blocks(blocks)

		if (simulation): simulate_fluid(blocks)

		pygame.display.flip()

		clock.tick(FRAMERATE)

	pygame.quit()


if __name__ == '__main__':
	main()