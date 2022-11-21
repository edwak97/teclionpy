from ctypes import *
import json
import sys
import math
import readline

tdjson_path = 'td/tdlib/lib/libtdjson.so.1.8.4'
if tdjson_path is None:
	sys.exit('Failed to find the TDLib')
tdjson = CDLL(tdjson_path)

_td_create_client_id = tdjson.td_create_client_id
_td_create_client_id.restype = c_int
_td_create_client_id.argtypes = []

_td_receive = tdjson.td_receive
_td_receive.restype = c_char_p
_td_receive.argtypes = [c_double]

_td_send = tdjson.td_send
_td_send.restype = None
_td_send.argtypes = [c_int, c_char_p]

client_id = _td_create_client_id()

###		Main cycle

while True:

	line = input('json> ')
	
	try:

		data = json.loads(line)
	
	except:

		print('Invalid json, try again.')

		continue

	data['@extra'] = 1

	_td_send(client_id, json.dumps(data).encode('utf-8'))

	while True:

		msg = _td_receive(math.inf).decode('utf-8')

		data = json.loads(msg.encode('utf-8'))
		
		if  ("@extra" in data):

			if data['@extra'] == 1:
				
				print(("{}:\n{}".format("Look up for @extra", msg)))

				break
