from ctypes.util import find_library
from ctypes import *
from threading import Thread
import json
import sys
import readline

#tdjson_path = find_library('td/tdlib/lib/libtdjson.so') #or 'libtdjson.dll' #?? for Windows
tdjson_path = 'td/tdlib/lib/libtdjson.so.1.8.4'
if tdjson_path is None:
	sys.exit("Can't find the TDLib")
tdjson = CDLL(tdjson_path)

#load TDLib functions from shared library
_td_create_client_id = tdjson.td_create_client_id
_td_create_client_id.restype = c_int
_td_create_client_id.argtypes = []

_td_receive = tdjson.td_receive
_td_receive.restype = c_char_p
_td_receive.argtypes = [c_double] #timeout -- maximum number of seconds allowed to wait for new data

_td_send = tdjson.td_send
_td_send.restype = None
_td_send.argtypes = [c_int, c_char_p]

tdlib_timeout = 2.0
api_id = 0
api_hash = ''
keepWorking = True

client_id = _td_create_client_id()

def td_send(query):
	query = json.dumps(query).encode('utf-8')
	_td_send(client_id, query)
	
def td_receive():
	result = _td_receive(tdlib_timeout)
	if result:
		result = json.loads(result.decode('utf-8'))
	return result

try:
	configFile = open('teclionpy.config', 'r')
	configFileLines = configFile.readlines()
	api_id_line = (configFileLines[0].strip()).split(' ')
	api_hash_line = (configFileLines[1].strip()).split(' ')
	if api_id_line[0] == 'api_id' and api_hash_line[0] == 'api_hash':
		api_id = api_id_line[1]
		api_hash = api_hash_line[1]
	else:
		print('Broken config file.')
		sys.stdout.flush()
		configFile.close()
		quit()
except:			
	print('Broken config file.')
	sys.stdout.flush()
	quit()


td_send({'@type': 'setLogStream', 'log_stream': {
				'@type': 'logStreamFile',
				'path': 'teclionpy.log',
				'max_file_size': 104857600,
				'redirect_stderr': True}})
td_send({'@type': 'setLogVerbosityLevel', 'new_verbosity_level': 1})

chatFiltersState = []
def changeChatFiltersState (newJsonState):
	chatFiltersState = newJsonState["chat_filters"]#.sort(key = lambda item: item['id'])
	print('\n Hey! \n')
	print(str(chatFiltersState).encode('utf-8'))
	print("\n")
def printState():
	for item in chatFiltersState:
		print(str(item["title"]).encode('utf-8'))
	sys.stdout.flush()

def tUpdateListener():
	while keepWorking:
		event = td_receive()
		if event:
			if event['@type'] == 'updateAuthorizationState':
				auth_state = event['authorization_state']

				if auth_state['@type'] == 'authorizationStateClosed':
					break

				if auth_state['@type'] == 'authorizationStateWaitTdlibParameters':
					td_send({'@type': 'setTdlibParameters', 'parameters': {
									'database_directory': 'tdlib',
									'use_message_database': True,
									'use_secret_chats': False,
									'api_id': api_id,
									'api_hash': api_hash,
									'system_language_code': 'en',
									'device_model': 'Desktop',
									'application_version': '0.1',
									'enable_storage_optimizer': True}})

				if auth_state['@type'] == 'authorizationStateWaitEncryptionKey':
					td_send({'@type': 'checkDatabaseEncryptionKey', 'encryption_key': ''})

				if auth_state['@type'] == 'authorizationStateWaitPhoneNumber':
					phone_number = input('Kindly let the app know your phone number:\n')
					td_send({'@type': 'setAuthenticationPhoneNumber', 'phone_number': phone_number})

				if auth_state['@type'] == 'authorizationStateWaitCode':
					code = input('Kindly enter the code your received:\n')
					td_send({'@type': 'checkAuthenticationCode', 'code': code})

				if auth_state['@type'] == 'authorizationStateWaitRegistration':
					first_name = input('Kindly enter your first name: ')
					last_name = input('Last name: ')
					td_send({'@type': 'registerUser', 'first_name':first_name, 'last_name': last_name})

				if auth_state['@type'] == 'authorizationStateWaitPassword':
					password = input('Kindly enter your 2fa password:\n')
					td_send({'@type': 'checkAuthenticationPassword', 'password': password})

				print(str(event).encode('utf-8'))
			if event['@type'] == 'updateChatFilters':
				changeChatFiltersState(event)
				printState()
				#print(str(event).encode('utf-8'))
			sys.stdout.flush()

tUpdateListenerThread = Thread(target = tUpdateListener)
tUpdateListenerThread.start()
while (True):
	""" updatesFilterLocal = input('@type = ')
	if updatesFilterLocal == "exit":
		keepWork = False
		quit() """
	line = input('teclionpy> ')
	if (line == 'exit'):
		keepWorking = False
		tUpdateListenerThread.join()
		quit()
	"""
	try:
		data = json.loads(line)
	except:
		print('Invalid json, try again.')
		continue

	data['@extra'] = 1
	_td_send(client_id, json.dumps(data).encode('utf-8'))"""
