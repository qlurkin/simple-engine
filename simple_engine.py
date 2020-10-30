import pygame
import key

class ExitApplication(Exception):
	pass

class Canvas:
	def __init__(self, surface, data):
		self.__surface = surface
		self.__data = data
		self.__color = (255, 255, 255)
		self.__width = 1
		self.__imageCache = {}
		self.__soundCache = {}
		self.__fontCache = {}

	def hideMouseCursor(self):
		pygame.mouse.set_visible(False)

	def showMouseCursor(self):
		pygame.mouse.set_visible(True)

	def setPixel(self, x, y):
		self.__surface.set_at((round(x), round(y)), self.__color)

	def getPixel(self,x, y):
		return self.__surface.get_at((round(x), round(y)))[:-1]

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

	def drawImage(self, left, top, path, partialLeft=None, partialTop=None, partialWidth=None, partialHeight=None):
		if partialTop is None or partialLeft is None or partialWidth is None or partialHeight is None:
			area = None
		else:
			area = pygame.Rect(partialLeft, partialTop, partialWidth, partialHeight)

		if path not in self.__imageCache:
			self.__imageCache[path] = pygame.image.load(path)
		self.__surface.blit(self.__imageCache[path], (left, top), area)

	def clear(self, red=0, green=0, blue=0):
		self.__surface.fill((red, green, blue))

	@property
	def elapsedTime(self):
		return self.__data["elapsedTime"]

	@property
	def mouseX(self):
		return self.__data["mousePos"][0]

	@property
	def mouseY(self):
		return self.__data["mousePos"][1]

	def __handleStrKey(self, key):
		if isinstance(key, str):
			return self.__data['keyDict'][key]
		return key

	def __handleModKeys(self, mods):
		res = 0
		for mod in mods:
			res|=mod
		return res

	def isDown(self, key):
		try:
			return self.__handleStrKey(key) in self.__data["keyDown"]
		except KeyError:
			return False

	def wasPressed(self, key, mod=[]):
		mods = self.__handleModKeys(mod)
		try:
			key = self.__handleStrKey(key)
		except KeyError:
			return False

		for event in self.__data["keyPressed"]:
			if event[0] == key and event[1] & mods:
				return True
		return False
		

	def wasReleased(self, key, mod=[]):
		mods = self.__handleModKeys(mod)
		try:
			key = self.__handleStrKey(key)
		except KeyError:
			return False

		for event in self.__data["keyReleased"]:
			if event[0] == key and event[1] & mods:
				return True
		return False

	@property
	def width(self):
		return self.__surface.get_width()

	@property
	def height(self):
		return self.__surface.get_height()

	def exit(self):
		raise ExitApplication()

	def setColor(self, red=255, green=255, blue=255):
		self.__color = (red, green, blue)
	
	def setStrokeWidth(self, width=1):
		if width < 1:
			width = 1
			print("Warning: Cannot set stroke width to less than 1")
		self.__width = width

	def playSound(self, path, loop=False):
		if path not in self.__soundCache:
			self.__soundCache[path] = pygame.mixer.Sound(path)
		if loop:
			loop = -1
		else:
			loop = 0
		self.__soundCache[path].play(loop)

	def drawText(self, left, top, text, fontSize=12, font='freesansbold.ttf'):
		if (font, fontSize) not in self.__fontCache:
			self.__fontCache[font, fontSize] = pygame.font.Font(font, fontSize)
		textImage = self.__fontCache[font, fontSize].render(text, False, self.__color)
		textRect = textImage.get_rect()
		textRect.top = top
		textRect.left = left
		self.__surface.blit(textImage, textRect)

class SimpleEngine:
	def __init__(self, width=256, height=240, pixelSize=3):
		self.__width = width
		self.__height = height
		self.__pixelSize = pixelSize

		pygame.init()
		pygame.mixer.init()
		self.__window = pygame.display.set_mode((width*pixelSize,height*pixelSize))
		self.__surface = pygame.Surface((width, height))

	def run(self, fn, *args):
		state = tuple(args)
		data = {
			"elapsedTime": 0,
			"keyDown": set(),
			"keyPressed": set(),
			"keyReleased": set(),
			"keyDict": {},
			"mousePos": (0, 0)
		}
		canvas = Canvas(self.__surface, data)
		
		clock = pygame.time.Clock()
		try:
			while True:
				elapsedTime = clock.tick(60)/1000
				data["elapsedTime"] = elapsedTime
				pygame.display.set_caption("Simple Engine (FPS: {})".format(round(1/elapsedTime)))
				
				data["keyPressed"] = set()
				data["keyReleased"] = set()

				mouseX, mouseY = pygame.mouse.get_pos()
				data["mousePos"] = (mouseX/self.__pixelSize, mouseY/self.__pixelSize)
				
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
							raise ExitApplication()
					
					if event.type == pygame.KEYDOWN:
						data["keyPressed"].add((event.key, event.mod))
						data["keyDown"].add(event.key)
						data["keyDict"][event.unicode] = event.key
					
					if event.type == pygame.KEYUP:
						data["keyReleased"].add((event.key, event.mod))
						data["keyDown"].remove(event.key)

					if event.type == pygame.MOUSEBUTTONUP:
						mod = pygame.key.get_mods()
						key = -event.button
						mouseX, mouseY = event.pos
						data["mousePos"] = (mouseX/self.__pixelSize, mouseY/self.__pixelSize)
						data["keyReleased"].add((key, mod))
						data["keyDown"].remove(key)

					if event.type == pygame.MOUSEBUTTONDOWN:
						mod = pygame.key.get_mods()
						key = -event.button
						mouseX, mouseY = event.pos
						data["mousePos"] = (mouseX/self.__pixelSize, mouseY/self.__pixelSize)
						data["keyPressed"].add((key, mod))
						data["keyDown"].add(key)

				state = fn(canvas, *state)
				self.__window.blit(pygame.transform.scale(self.__surface, self.__window.get_rect().size), (0, 0))
				pygame.display.flip()
		except ExitApplication:
			pass 

if __name__ == "__main__":
	def update(canvas: Canvas, x, y, vx, vy):
		canvas.clear()
		canvas.hideMouseCursor()
		canvas.setColor(0, 255, 0)
		canvas.setStrokeWidth(2)
		canvas.drawCircle(x, y, 10)
		canvas.drawText(canvas.mouseX, canvas.mouseY, "Prout")

		if canvas.wasPressed('a'):
			print("A")

		if canvas.wasPressed(key.K_a):
			print("Q")

		if canvas.wasPressed(key.MOUSEBUTTON_LEFT, [key.KMOD_CTRL]):
			print("click")

		if canvas.wasReleased(key.MOUSEBUTTON_LEFT, [key.KMOD_ALT]):
			print("declick")

		x += vx * canvas.elapsedTime
		y += vy * canvas.elapsedTime
		if x <= 10 :
			vx = -vx
			x = 10
		if x >= canvas.width-1-10:
			vx = -vx
			x = canvas.width-1-10
		if y <= 10:
			vy = -vy
			y = 10
		if y >= canvas.height-1-10:
			vy = -vy
			y = canvas.height-1-10

		return x, y, vx, vy

	SimpleEngine().run(update, 10, 10, 50, 30)