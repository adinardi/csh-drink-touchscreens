import pygame
from pygame.locals import *
import drinkAPI
import math
import time
from threading import Thread

pygame.init()
font = pygame.font.Font(None, 36)
BUTTONS = {}

def main():
	global BUTTONS

	ibuttonreader = checkibutton()
	ibuttonreader.start()
	# State
	# 1 = Unauthenicated
	# 2 = Select Machine
	# 3 = Select Drink
	# 4 = Dropping
	drink_state = 1

	# Machine we're using
	current_machine = None

	last_ibutton = ''

	# Initialise screen
	screen = pygame.display.set_mode((800, 600))
	pygame.display.set_caption('Basic Pygame program')

	# Fill background
	background = pygame.Surface(screen.get_size())
	background = background.convert()
	background.fill((250, 250, 250))

	# Display some text
	#text = font.render("Hello There", 1, (10, 10, 10))
	#textpos = text.get_rect()
	#textpos.centerx = background.get_rect().centerx
	#background.blit(text, textpos)

	# Blit everything to the screen
	screen.blit(background, (0, 0))
	pygame.display.flip()


	CHANGE = 1
	PROCESSING = 0
	csh_net = drinkAPI.Network('csh.rit.edu')
	user = None
	auth_ibutton = None
	# Event loop
	while 1:
		if ibuttonreader.ibutton != last_ibutton and ibuttonreader.ibutton != '':
			drink_state = 2
			CHANGE = 1
			PROCESSING = 1
			auth_ibutton = ibuttonreader.ibutton
			ibuttonreader.ibutton = ''
			last_ibutton = auth_ibutton

		for event in pygame.event.get():
			if event.type == QUIT:
				return

			if event.type == MOUSEBUTTONDOWN:
				#print 'buttons: ' + str(BUTTONS)
				testrect = pygame.Rect(event.pos, (0, 0))
				#print 'test rect: ' + str(testrect)
				clicked_button = testrect.collidedict(BUTTONS)
				#print 'clicked button: ' + str(clicked_button)
				if clicked_button is None:
					continue

				elif clicked_button[1]['type'] == 'logout':
					# Reset everything!
					drink_state = 1
					CHANGE = 1
					PROCESSING = 0

				elif drink_state == 1:
					if clicked_button[1]['type'] == 'login':
							drink_state = 2 # Jump right to machine listing ATM
							CHANGE = 1
							PROCESSING = 1

				elif drink_state == 3:
					clicked_key = clicked_button[1]
					print "checking clicked key: " + str(clicked_key)
					if clicked_key['type'] == 'item':
						print "got item click: " + str(clicked_key['item'])
						drink_state = 4
						CHANGE = 1
						PROCESSING = 1
						item_to_drop = clicked_key['item']

		if CHANGE == 1:
			CHANGE = 0
			background.fill((255, 255, 255))
			# Redrawing the interface, so kill the stashed buttons
			BUTTONS = {}
			if drink_state == 1:
				#login_btn = pygame.Surface((200, 50))
				#login_btn_rect = login_btn.get_rect()
				#login_btn_rect.left = 20
				#login_btn_rect.top = 550
				#text = font.render("Login", 1, (255, 255, 255))
				#login_btn.blit(text, (10, 10))
				# background.blit(login_btn, login_btn_rect)
				#BUTTONS[tuple(login_btn_rect)] = {'type': 'login'}
				render_message(background, "Touch iButton to continue...")


			elif drink_state == 2:
				c = 1
				render_message(background, "Authenticating...")

			elif drink_state == 2.5:
				c = 1

			elif drink_state == 3:
				render_switch_btn(background)
				render_user_info(background, user)
				render_logout_btn(background)

				inv = system.inventory
				render_drink_choices(background, inv)

			elif drink_state == 4:
				c = 1
				render_message(background, "Dropping...")

		screen.blit(background, (0, 0))
		pygame.display.flip()

		if PROCESSING == 1:
			if drink_state == 2 and auth_ibutton is not None:
				# user = drinkAPI.User('', '3b00000e4bbC9301')
				user = drinkAPI.User('', auth_ibutton)
				auth_ibutton = None
				last_ibutton = ''
				system = drinkAPI.System('Little Drink', 'ld')
				authed = user.connect_to_system(system, csh_net)
				if authed:
					drink_state = 3
					CHANGE = 1
					PROCESSING = 0
			elif drink_state == 4:
				print 'dropping ' + str(item_to_drop)
				user.purchase(item_to_drop, 0)
				time.sleep(5)
				PROCESSING = 0
				CHANGE = 1
				drink_state = 1


def render_message(bg, message):
	msg = pygame.Surface((800, 400))
	msg.fill((255, 255, 255))
	rect = msg.get_rect()
	rect.left = 20
	rect.top = 50
	text = font.render(message, 1, (0, 0, 0))
	msg.blit(text, (0, 0))
	bg.blit(msg, rect)
	return rect

def render_switch_btn(bg):
	switch_btn = pygame.Surface((200, 50))
	rect = switch_btn.get_rect()
	rect.left = 20
	rect.top = 550
	BUTTONS[tuple(rect)] = {'type': 'switch'}
	text = font.render("Switch", 1, (255, 255, 255))
	switch_btn.blit(text, (10, 10))
	bg.blit(switch_btn, rect)
	return rect

def render_logout_btn(bg):
	logout = pygame.Surface((200, 50))
	rect = logout.get_rect()
	rect.left = 420
	rect.top = 550
	BUTTONS[tuple(rect)] = {'type': 'logout'}
	text = font.render("Logout", 1, (255, 255, 255))
	logout.blit(text, (10, 10))
	bg.blit(logout, rect)
	return rect

def render_user_info(bg, user):
	user_info = pygame.Surface((200, 50))
	user_info.fill((255, 255, 255))
	rect = user_info.get_rect()
	rect.left = 220
	rect.top = 550
	font = pygame.font.Font(None, 20)
	text = font.render("User: " + user.name, 1, (0, 0, 0))
	user_info.blit(text, (10, 10))
	text2 = font.render("Credits: " + str(user.get_credits_balance()), 1, (0, 0, 0))
	user_info.blit(text2, (10, 20))
	bg.blit(user_info, rect)
	return rect

def render_drink_choices(bg, choices):
	#inv = pygame.Surface((800, 500))
	#inv.fill((255, 255, 255))
	#rect = inv.get_rect()
	#rect.left = 0
	#rect.top = 50
	font = pygame.font.Font(None, 20)
	item_count = len(choices)
	width = (770 / math.ceil(item_count / 4.0))
	cur_item_on_row = 0
	items_per_row = math.ceil(770 / width) - 1
	cur_row = 0
	for item in choices:
		s = pygame.Surface((width - 2, 98))
		s.fill((0, 0, 0))
		text = font.render(item.name, 1, (255, 255, 255))
		s.blit(text, (10, 10))
		text = font.render(str(item.price), 1, (255, 255, 255))
		s.blit(text, (10, 25))

		if (cur_item_on_row > items_per_row):
			# reset us to the next row, pos 1
			cur_item_on_row = 0
			cur_row = cur_row + 1
		sr = s.get_rect()
		sr.left = (cur_item_on_row * width) + 10
		sr.top = (cur_row * 100) + 50
		cur_item_on_row = cur_item_on_row + 1
		#inv.blit(s, sr)
		BUTTONS[tuple(sr)] = {'type': 'item', 'item': item}
		bg.blit(s, sr)
	#bg.blit(inv, rect)

class checkibutton(Thread):
	def __init__ (self):
		Thread.__init__(self)
		self.ibutton = ''
	def run(self):
		while(1):
			time.sleep(1)
			try:
				ibfile = open('/tmp/ibutton', "r")
				print 'checking file'
				if ibfile is not None:
					line = ibfile.readline()
					print 'got: "' + line + '"'
					nibutton = line
					if nibutton != '':
						self.ibutton = nibutton
					ibfile.close()
					if (self.ibutton != ''):
						ibfile = open('/tmp/ibutton', "w")
						ibfile.write("")
						ibfile.close()
			finally:
				c = 1

if __name__ == '__main__': main()
