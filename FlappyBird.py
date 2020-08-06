import sys, pygame, neat, os, random
pygame.init()

# SET UP WINDOW
WIN_WIDTH = 300
WIN_HEIGHT = 500
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT));
pygame.display.set_caption("Not Flappy Bird")

class Bird:
	y_vel = 0.0
	y_pos = WIN_HEIGHT/2 # PUT BIRD IN THE MIDDLE OF THE WINDOW
	radius = 10
	G = 0.0001; # 'GRAVITY'
	
	def __init__(self, y, currentObstacle):
		self.y_pos = y
		self.currentObstacle = currentObstacle # STORE THE NEAREST OBSTACLE SO ONLY HAS TO CHECK THAT ONE FOR COLLISION
		
	def draw(self, win):
		pygame.draw.circle(win, (255,255,255), (int(WIN_WIDTH/2),int(self.y_pos)), self.radius) #DRAW BIRD
		# DRAW LINES TO NEAREST OBSTACLE, JUST FOR SHOW REALLY
		pygame.draw.line(win, (255,0,0), (WIN_WIDTH/2, self.y_pos), (self.currentObstacle.xpos, self.currentObstacle.top_height))
		pygame.draw.line(win, (255,0,0), (WIN_WIDTH/2, self.y_pos), (self.currentObstacle.xpos, self.currentObstacle.y_start_bottom))
		
	def update(self):
		self.y_pos = self.y_pos + self.y_vel
		self.y_vel = self.y_vel + self.G
	def jump(self):
		self.y_vel = -0.1
	
	def collide(self): # CHECK FOR COLLISION WITH OBSTACLE
		if (self.currentObstacle.xpos < (WIN_WIDTH/2)+self.radius and 
		(self.y_pos-self.radius < self.currentObstacle.top_height or 
		self.y_pos+self.radius > self.currentObstacle.y_start_bottom)):
			return True			
		return False
	
	def offScreen(self): # CHECK IF ABOVE/BELOW SCREEN
		if(self.y_pos <= self.radius or self.y_pos > (WIN_HEIGHT-self.radius)):
			return True
		return False
		
class Obstacle:
	top_height = 0
	bottom_height = 0
	width = 30
	gap = 80
	xpos = 0
	y_start_bottom = 0
	vel = 0.03
	
	def __init__(self, height_base):
		self.bottom_height = height_base
		self.top_height = WIN_HEIGHT - self.gap - self.bottom_height
		self.y_start_bottom = WIN_HEIGHT - self.bottom_height
		self.xpos = WIN_WIDTH # START THE OBSTACLE AT RIGHT HAND SIDE OF WINDOW
		
	def update(self):
		self.xpos = self.xpos - self.vel
		
	def draw(self, win):
		pygame.draw.rect(win, (255,255,255), (int(self.xpos), 0, self.width, self.top_height))
		pygame.draw.rect(win, (255,255,255), (int(self.xpos), self.y_start_bottom, self.width, self.bottom_height))
		

def draw_window(win, birds, obstcl_list):
	win.fill((0,0,0)) # BLACK BACKGOUND
	for bird in birds:
		bird.draw(win)
	for obs in obstcl_list:
		obs.draw(win)
	pygame.display.update()

def main(genomes, config):
	nets = []
	ge = []
	birds = []
	
	# CREATE FIRST OBSTACLE
	obstcl = Obstacle(random.randint(20, 200))
	obstcl_list = [obstcl];
	
	# STORE THE NN's, BIRDS
	for _, g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g,config)
		nets.append(net)
		birds.append(Bird(250, obstcl))
		g.fitness = 0
		ge.append(g)

	run = True

	while run:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
			# NO LONGER RELEVANT	
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					bird.jump()
		
		# STOP GENERATION IF ALL HAVE FAILED
		if len(birds) < 1:
			run = False
			break
		
		for x, bird in enumerate(birds):
			# GET OUTPUT FROM NN
			output = nets[x].activate((bird.y_pos, abs(bird.y_pos - bird.currentObstacle.top_height), abs(bird.y_pos - bird.currentObstacle.y_start_bottom)))
			if(output[0] > 0.5):
				bird.jump()
				
			bird.update()
			ge[x].fitness += 0.005 # REWARD FOR SURVIVING
			if (bird.collide() == True):
				ge[x].fitness -= 1 # PUNISH FOR CRASHING
				birds.pop(x)
				nets.pop(x)
				ge.pop(x)
			if (bird.offScreen() == True): #JUST GET RID IF OFF SCREEN
				birds.pop(x)
				nets.pop(x)
				ge.pop(x)
				
		if len(birds) < 1:
			run = False
			break
		
		# GENERATE NEW OBSTACLE ONCE CURRENT HAS MOVED PAST BIRD
		if(birds[0].currentObstacle.xpos < ((WIN_WIDTH/2 ) - birds[0].radius - birds[0].currentObstacle.width)):
			newObs = Obstacle(random.randint(20, 200))
			obstcl_list.append(newObs)
			for bird in birds:
				bird.currentObstacle = newObs
			for g in ge:
				g.fitness += 3 # LARGE REWARD FOR GOING THROUGH OBSTACLE
		
		# DELETE OBSTACLES THAT HAVE GONE THROUGH THE WINDOW
		for obs in reversed(obstcl_list):
			obs.update()
			if obs.xpos < 0:
				obstcl_list.remove(obs)

		draw_window(win, birds, obstcl_list)

	

def run(config_path):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
	
	p = neat.Population(config)
	
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)
	
	winner = p.run(main,50)

if __name__ == "__main__":
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, "config-feedforward.txt")
	run(config_path)
