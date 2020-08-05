import sys, pygame	
pygame.init()

WIN_WIDTH = 300
WIN_HEIGHT = 500


win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT));
pygame.display.set_caption("Not Flappy Bird")

class Bird:
	y_vel = 0.0
	y_pos = WIN_HEIGHT/2
	radius = 10
	G = 0.1;
	
	def __init__(self, y, currentObstacle):
		self.y_pos = y
		self.currentObstacle = currentObstacle
		
	def draw(self, win):
		pygame.draw.circle(win, (255,255,255), (int(WIN_WIDTH/2),int(self.y_pos)), self.radius)
		pygame.draw.line(win, (255,0,0), (WIN_WIDTH/2, self.y_pos), (self.currentObstacle.xpos, self.currentObstacle.top_height))
		pygame.draw.line(win, (255,0,0), (WIN_WIDTH/2, self.y_pos), (self.currentObstacle.xpos, self.currentObstacle.y_start_bottom))
		
	def update(self):
		self.y_pos = self.y_pos + self.y_vel;
		self.y_vel = self.y_vel + 0.0001
	def jump(self):
		self.y_vel = -0.1;
	
	def collide(self):
		if (self.currentObstacle.xpos < (WIN_WIDTH/2)+self.radius and (self.y_pos-self.radius < self.currentObstacle.top_height or self.y_pos+self.radius > self.currentObstacle.y_start_bottom)):
			return True			
		return False
	
	def offScreen(self):
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
		self.xpos = WIN_WIDTH
		
	def update(self):
		self.xpos = self.xpos - self.vel
		
	def draw(self, win):
		pygame.draw.rect(win, (255,255,255), (int(self.xpos), 0, self.width, self.top_height))
		pygame.draw.rect(win, (255,255,255), (int(self.xpos), self.y_start_bottom, self.width, self.bottom_height))
		

def draw_window(win, bird, obstcl_list):
	win.fill((0,0,0))
	bird.draw(win)
	for obs in obstcl_list:
		obs.draw(win)
	pygame.display.update()

def main():
	run = True	

	
	obstcl = Obstacle(100)
	obstcl_list = [obstcl];
	bird = Bird(250, obstcl)

	while run:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					bird.jump()
		
		if(bird.currentObstacle.xpos < ((WIN_WIDTH/2 ) - bird.radius - bird.currentObstacle.width)):
			newObs = Obstacle(100)
			obstcl_list.append(newObs)
			bird.currentObstacle = newObs
			
		bird.update()
		if (bird.collide() == True):
			p = 1
			print("HIT")
		if (bird.offScreen() == True):
			p = 1
			print("OFFSCREEN")
		
		for obs in reversed(obstcl_list):
			obs.update()
			if obs.xpos < 0:
				obstcl_list.remove(obs)

		draw_window(win, bird, obstcl_list)

	
main()


