from threading import Thread
from os import system, name

import json
import sys
import readline
import teclionpyModules.initdata as initdata
#import teclionpyModules.eventHandler as eventHandler

def fitScreen():
	if name == 'nt':
		system('cls')
	else:
		system('clear')

chatFiltersState = []
def changeChatFiltersState (newJsonState):
	global chatFiltersState
	chatFiltersState = sorted(newJsonState["chat_filters"], key = lambda item: item['id'])

def printState():
	fitScreen()
	for item in chatFiltersState:
		print(item["title"],' |', end = ' ')
	print('\nteclionpy> ')
	sys.stdout.flush()

keepWorking = True
def tUpdateListener():
	while keepWorking:
		event = initdata.td_receive()
		#eventHandler.Handle(event) 
		if event:
			if event['@type'] == 'updateAuthorizationState':
				auth_state = event['authorization_state']

				if auth_state['@type'] == 'authorizationStateClosed':#todo unclear when it happens. Need to investigate.
					break

				if auth_state['@type'] == 'authorizationStateWaitEncryptionKey':
					initdata.td_send({'@type': 'checkDatabaseEncryptionKey', 'encryption_key': ''})

				if auth_state['@type'] == 'authorizationStateWaitPhoneNumber':
					phone_number = input('Kindly let the app know your phone number:\n')
					initdata.td_send({'@type': 'setAuthenticationPhoneNumber', 'phone_number': phone_number})

				if auth_state['@type'] == 'authorizationStateWaitCode':
					code = input('Kindly enter the code your received:\n')
					initdata.td_send({'@type': 'checkAuthenticationCode', 'code': code})

				if auth_state['@type'] == 'authorizationStateWaitRegistration':
					first_name = input('Kindly enter your first name: ')
					last_name = input('Last name: ')
					initdata.td_send({'@type': 'registerUser', 'first_name':first_name, 'last_name': last_name})

				if auth_state['@type'] == 'authorizationStateWaitPassword':
					password = input('Kindly enter your 2fa password:\n')
					initdata.td_send({'@type': 'checkAuthenticationPassword', 'password': password})

			if event['@type'] == 'updateChatFilters':
				changeChatFiltersState(event)
				printState()
			sys.stdout.flush()

tUpdateListenerThread = Thread(target = tUpdateListener)
tUpdateListenerThread.start()
while (True):
	fitScreen()
	line = input('teclionpy> ')
	#inputHandler(line)
	if (line == 'exit'):
		keepWorking = False
		tUpdateListenerThread.join()
		sys.exit()
