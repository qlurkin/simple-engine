import pygame

class ExitApplication(Exception):
	pass

class Canvas:
	def __init__(self, surface, data):
		self.__surface = surface
		self.__data = data
		self.__color = (255, 255, 255)
		self.__width = 1
		self.__imageCache = {}

	def drawPixel(self, x, y):
		self.__surface.set_at((round(x), round(y)), self.__color)

	def drawRect(self, left, top, width, height):
		pygame.draw.rect(self.__surface, self.__color, pygame.Rect(left, top, width, height), self.__width)

	def fillRect(self, left, top, width, height):
		pygame.draw.rect(self.__surface, self.__color, pygame.Rect(left, top, width, height))

	def drawLine(self, x1, y1, x2, y2):
		pygame.draw.line(self.__surface, self.__color, (x1, y1), (x2, y2), self.__width)

	def drawTriangle(self, x1, y1, x2, y2, x3, y3):
		pygame.draw.polygon(self.__surface, self.__color, [(x1, y1), (x2, y2), (x3, y3)], self.__width)

	def fillTriangle(self, x1, y1, x2, y2, x3, y3):
		pygame.draw.polygon(self.__surface, self.__color, [(x1, y1), (x2, y2), (x3, y3)])

	def drawCircle(self, x, y, radius):
		pygame.draw.circle(self.__surface, self.__color, (round(x), round(y)), radius, self.__width)

	def fillCircle(self, x, y, radius):
		pygame.draw.circle(self.__surface, self.__color, (round(x), round(y)), radius)

	def drawImage(self, x, y, path):
		if path not in self.__imageCache:
			self.__imageCache[path] = pygame.image.load(path)
		self.__surface.blit(self.__imageCache[path], (x, y))

	def clear(self):
		self.__surface.fill((0,0,0))

	@property
	def mouseX(self):
		raise NotImplementedError()

	@property
	def elapsedTime(self):
		return self.__data["elapsedTime"]

	@property
	def mouseY(self):
		raise NotImplementedError()

	def isPressed(self, key):
		raise NotImplementedError()

	@property
	def width(self):
		return self.__surface.get_width()

	@property
	def height(self):
		return self.__surface.get_height()

	def exit(self):
		raise ExitApplication()

	def setColor(self, red, green, blue):
		self.__color = (red, green, blue)
	
	def setStrokeWidth(self, width):
		if width < 1:
			width = 1
			print("Warning: Cannot set stroke width to less than 1")
		self.__width = width

class SimpleEngine:
	def __init__(self, width, height, pixelSize):
		self.__width = width
		self.__height = height
		self.__pixelSize = pixelSize

		pygame.init()
		self.__window = pygame.display.set_mode((width*pixelSize,height*pixelSize))
		self.__surface = pygame.Surface((width, height))

	def run(self, fn, *args):
		state = tuple(args)
		data = {
			"elapsedTime": 0
		}
		canvas = Canvas(self.__surface, data)
		
		clock = pygame.time.Clock()
		try:
			while True:
				elapsedTime = clock.tick(60)/1000
				data["elapsedTime"] = elapsedTime
				
				for event in pygame.event.get():
					print(event.type)
					if event.type == pygame.QUIT:
							raise ExitApplication()
				
				pygame.display.set_caption("Simple Engine (FPS: {})".format(round(1/elapsedTime)))
				state = fn(canvas, *state)
				self.__window.blit(pygame.transform.scale(self.__surface, self.__window.get_rect().size), (0, 0))
				pygame.display.flip()
		except ExitApplication:
			pass

if __name__ == "__main__":
	def update(canvas, x, y, vx, vy):
		canvas.clear()
		canvas.setColor(0, 255, 0)
		canvas.setStrokeWidth(2)
		canvas.fillCircle(x, y, 10)
		canvas.fillTriangle(20, 20, 40, 20, 30, 40)
		canvas.fillRect(20, 50, 60, 20)
		canvas.drawLine(50, 50, 100, 150)
		canvas.drawImage(0, 0, "poop.png")

		x += vx * canvas.elapsedTime
		y += vy * canvas.elapsedTime
		if x <= 5 :
			vx = -vx
			x = 5
		if x >= canvas.width-1-5:
			vx = -vx
			x = canvas.width-1-5
		if y <= 5:
			vy = -vy
			y = 5
		if y >= canvas.height-1-5:
			vy = -vy
			y = canvas.height-1-5

		return x, y, vx, vy

	SimpleEngine(200, 150, 4).run(update, 10, 10, 50, 30)