from ctypes.util import find_library
from ctypes import *
from os import system, name

import json
import sys

tdjson_path = 'td/tdlib/lib/libtdjson.so.1.8.4'#todo alter code for Windows case
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

client_id = _td_create_client_id()
def td_send(query):
	query = json.dumps(query).encode('utf-8')
	_td_send(client_id, query)
	
def td_receive():
	result = _td_receive(tdlib_timeout)
	if result:
		result = json.loads(result.decode('utf-8'))
	return result

def initTDLib():
	api_id = 0
	api_hash = 0
	done = False
	with open('teclionpy.config', 'r') as configFile:#todo rewrite so that lines order doesn't matter 
		configFileLines = configFile.readlines()
		api_id_line = (configFileLines[0].strip()).split(' ')
		api_hash_line = (configFileLines[1].strip()).split(' ')
		if api_id_line[0] == 'api_id' and api_hash_line[0] == 'api_hash':
			api_id = api_id_line[1]
			api_hash = api_hash_line[1]
			done = True
	if not done:
		sys.exit('Broken config file.')

	td_send({'@type': 'setLogVerbosityLevel', 'new_verbosity_level': 1})
	
	td_send({'@type': 'setLogStream', 'log_stream': {
					'@type': 'logStreamFile',
					'path': 'teclionpy.log',
					'max_file_size': 104857600,
					'redirect_stderr': True}})

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

initTDLib() 
