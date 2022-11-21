from ctypes.util import find_library
from ctypes import *
import json
import sys

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
_td_receive.argtypes = [c_double]

_td_send = tdjson.td_send
_td_send.restype = None
_td_send.argtypes = [c_int, c_char_p]

_td_execute = tdjson.td_execute
_td_execute.restype = c_char_p
_td_execute.argtypes = [c_char_p]

log_message_callback_type = CFUNCTYPE(None, c_int, c_char_p)

_td_set_log_message_callback = tdjson.td_set_log_message_callback
_td_set_log_message_callback.restype = None
_td_set_log_message_callback.argtypes = [c_int, log_message_callback_type]

@log_message_callback_type
def on_log_message_callback(verbosity_level, message):
	if verbosity_level == 0:
		sys.exit('TDLib fatal error: %r' % message)

def td_execute(query):
	query = json.dumps(query).encode('utf-8')
	result=_td_execute(query)
	if result:
		result = json.loads(result.decode('utf-8'))
	return result

_td_set_log_message_callback(2, on_log_message_callback)

# setting TDLib log verbosity level to 1 (errors)
print(str(td_execute({'@type': 'setLogVerbosityLevel', 'new_verbosity_level': 1, '@extra': 1.01234})).encode('utf-8'))

client_id = _td_create_client_id()

def td_send(query):
	query = json.dumps(query).encode('utf-8')
	_td_send(client_id, query)
	
def td_receive():
	result = _td_receive(1.0)
	if result:
		result = json.loads(result.decode('utf-8'))
	return result 

td_send({'@type': 'getAuthorizationState', '@extra': 1.01234})

while True:
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
								'api_id': 5324500,
								'api_hash': '715c175c34436ba2cf204355ccaa4a48',
								'system_language_code': 'en',
								'device_model': 'Desktop',
								'application_version': '0.1',
								'enable_storage_optimizer': True}})

			if auth_state['@type'] == 'authorizationStateWaitEncryptionKey':
				td_send({'@type': 'checkDatabaseEncryptionKey', 'encryption_key': ''})

			if auth_state['@type'] == 'authorizationStateWaitPhoneNumber':
				phone_number = input('Kindly let the app know your phone number:\n')
				td_send({'type': 'setAuthenticationPhoneNumber', 'phone_number': phone_number})

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
		sys.stdout.flush()	