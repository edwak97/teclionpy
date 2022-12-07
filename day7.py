lines = []
with open('input.txt', 'r') as file_origin: 
		lines = file_origin.readlines()
lines = [line.strip() for line in lines]

class Node:
	def __init__(self, node_type, name, childNodes = None, parentNode = None, size = None):
		
		self.parent = parentNode
		self.type = node_type # 0 -- files, 1 -- dirs
		self.name = name
		self.size = None if size == None else int(size)

currentDir = None
def changewd(dirname):
	print(f'Directory changed to {dirname}')

def readls(args):
	for arg in args:
		print(f'{arg}\n')

def cmdRead(linearr):
	cmdarr = linearr.split(' ')
	switch = {
		'ls': readls,
		#'pwd': readwd,
	}
	res = switch.get(cmdarr[0],0)
	if res != 0:
		return res
	switch = {
		'cd': changewd,
		#'rm': rmvfi
	}
	res = switch.get(cmdarr[0], 0)
	if res != 0:
		res(cmdarr[1])
	else:
		print(f'It is not recognized: {res} args {cmdarr[1]}')
def getOutend(lines, i):
	res = []
	k = i+1
	while k < len(lines):
		if lines[k][0] == '$':
			break
		res[len(res):] = [lines[k]]
		k+=1
	return (res, k)

#### Reading Input ####
testlines = [
	'$ cd /',
	'$ cd lmao',
	'$ ls',
	'123123123 a.txt',
	'4567 b.txt',
	'dir joseph',
	'$ cd fuckthat/loveme',
	'$ cd iworkalot',
	'$ ls',
	'qweqwe',
	'dsdsdsd',
	'$ cd end',
	]
def beginRead(lines):
		i = 0
		while i < len(lines):
			if lines[i][0] == '$':
				applyf = cmdRead(lines[i][2:])
				if applyf:
					args = getOutend(lines, i)
					applyf(args[0])
					i = args[1]
					continue
			i+=1
beginRead(testlines)
