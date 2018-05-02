import hashlib
import json
import socket
import time
from block import *
import sys
import argparse
from uuid import getnode as get_mac
import threading
from Crypto.Cipher import AES
import random

key = ['b', '1', '\xc7', '&', '\xf2', '\xc4', 'Z', 'J', '8', '\x08', '&', '\x85', '\x85', '\x92', '\xfc', '=']
iv = ['J', '\x8c', '\x00', '\xa4', '\x17', '\xab', 'n', '\x82', '\x92', ':', '[', '\x0f', 'K', '\xc2', '\x88', '\xbf']
aes_key = ''.join(key)
aes_iv = ''.join(iv)
pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

def encodeMsg(msg):
	retmsg = json.JSONEncoder().encode(msg)
	aes_msg = AES.new(aes_key, AES.MODE_CBC, aes_iv).encrypt(pad(retmsg))
	return aes_msg
	# decode the recieved string into a json dict
def decodeMsg(msg):
	aes_msg = unpad(AES.new(aes_key, AES.MODE_CBC,aes_iv).decrypt(msg))
	received = json.loads(aes_msg)
	return received

def getMiningAddress(host = '',port = ''):
	sha = hashlib.sha256()
	sha.update(str(get_mac()) + str(host) + str(port))
	return str(sha.hexdigest())


def proofOfWork(prev_proof):
	i = prev_proof + 1
	while((i % 12 == 0 and i % prev_proof == 0) == 0):
		i+= 1
	return i

class kecikNode:

	def __init__(self, host, port):
		self.host = host
		self.ip = host
		self.port = port
		self.timestamp = time.time()
		self.kecik_addr = getMiningAddress(host = host, port = port)
		self.alive = True
		self.peers = dict()
		self.peers[self.kecik_addr] = (self.ip,self.port)
		self.users = dict()
		self.node_transactions = []
		self.blockchain = Blockchain()
		self.blockchain.populateBlockChain()
		print "\nGenesis block #{} initialized at {}:{}".format(self.blockchain.getCurrBlock().index, self.host, self.port)	
		print "Hash: {}\n".format(self.blockchain.getCurrBlock().hash)


	def commandHandler(self, client, addr):
		while True:
			# Decode command msg
			command = client.recv(4096)
			commandMsg = decodeMsg(command)

			#Check if client is in peer list or peer wants to join
			clientHostName = socket.gethostbyaddr(addr[0])[0]

			#Print out command entries
			print >>sys.stderr, "Received message from %s: %s\n" % (addr[0], commandMsg)

			#if received join command, add to peer list and send blocks
			if(commandMsg['request'] == 'get_blocks'):
				self.consensus()
				msg = {'ack':self.blockchain.blockChainToDictList()}
				client.send(encodeMsg(msg))
				client.close()
				return
			elif (commandMsg['request'] == 'funds'):
				self.consensus()
				userid = str(commandMsg['body'])
				coins = 0
				for b in self.blockchain.getBlockChain():
					for t in b.data['transactions']:
						if t['to'] == userid:
							coins += t['amount']
						elif t['from'] == userid:
							coins -= t['amount']
				msg = {'ack': (coins, len(self.blockchain.blockchain) - 1)}
				client.send(encodeMsg(msg))
				client.close()
				return
			elif(commandMsg['type'] == 'peer'):
				if (commandMsg['request'] == 'join'):
					ackMsg = encodeMsg({'peers':self.peers,'users':self.users})
					client.send(ackMsg)
					client.close()
					return
				elif(commandMsg['request'] == 'join_r2'):
					self.peers[str(commandMsg['body']['peer']['addr'])] = commandMsg['body']['peer']['ipport']
					self.consensus()
					client.close()
					return
				elif(commandMsg['request'] == 'consensus'):
					msg = {'ack':self.blockchain.blockChainToDictList()}
					client.send(encodeMsg(msg))
					client.close()
					return
				elif(commandMsg['request'] == 'consensus_r2'):
					new_blockchain = []
					for b in commandMsg['body']:
						new_blockchain.append(Block(b['index'],b['timestamp'],b['data'],b['prev_hash'],copy=True,hashvalue=b['hash']))
					if self.blockchain.validateChain(new_blockchain) == True:
						self.blockchain.updateBlockChain(new_blockchain)
						print "Updated blockchain with longest chain"
					client.close()
					return
			elif (commandMsg['type'] == 'client'):
				if(commandMsg['request'] == 'transaction'):
					new_transaction = commandMsg['body']
					print "New transaction"
					print "FROM : {}".format(new_transaction['from'])
					print "TO: {}".format(new_transaction['to'])
					print "AMOUNT: {}".format(new_transaction['amount'])
					client.send(encodeMsg({'ack':"Transaction submission successful"}))
					client.close()
					return

				elif(commandMsg['request'] == 'mine'):
					prev_block = self.blockchain.getCurrBlock()
					prev_proof = prev_block.data['proof_of_work']
					new_proof = proofOfWork(prev_proof)
					self.node_transactions.append({'from':'network','to': str(commandMsg['body']),'amount':1})
					new_block_data = {'proof_of_work': new_proof,'transactions':list(self.node_transactions)}
					new_block_index = prev_block.index + 1
					self.node_transactions[:] = []
					self.blockchain.addBlock(new_block_data)
					mined_block = self.blockchain.getCurrBlock()
					msg = {'ack':{'index': new_block_index, 'timestamp': mined_block.timestamp, 'data': new_block_data, 
								  'prev_hash': mined_block.prev_hash, 'hash': mined_block.hash}}
					client.send(encodeMsg(msg))
					self.consensus()
					client.close()
					return
				elif(commandMsg['request'] == 'add_user'):
					self.users[commandMsg['body']['user']] = commandMsg['body']['pubkey']
					client.close()
					return

		print >>sys.stderr, "Unknown command message"
		client.close()


	# Command listener threads for kecikCoin Server
	def commandListener(self):
		try:
			self.listener = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.listener.bind((self.ip, self.port))
			print >>sys.stderr,"Starting to listen for commands on port %s"%self.port

		except socket.error as e:
			raise Exception("Unable to set up listener : %s" %e)
			return

		self.listener.listen(5)

		while self.alive == True:
			clientSock, remoteAddr = self.listener.accept()
			thread.start_new_thread(self.commandHandler,(clientSock, remoteAddr))
		self.listener.close()
		print >>sys.stderr, ("Closing up command listener")

	def consensus(self):
		print "Starting consensus algorithm"
		longest_chain = self.blockchain.getBlockChain()
		peer_chains = []
		for key,peer in self.peers.iteritems():
			if key != self.kecik_addr:
				msg = encodeMsg({'type': 'peer','request':'consensus'})
				try:
					sock = socket.create_connection(peer)
				except:
					print "No such peer with host and port"
					return
				sock.sendall(msg)
				ack = decodeMsg(sock.recv(4096))
				peer_chains.append(ack['ack'])

		for chain in peer_chains:
			if(len(chain) > len(longest_chain)):
				longest_chain = chain

		if(longest_chain != self.blockchain.getBlockChain()):
			new_blockchain = []
			for b in longest_chain:
				new_block = Block(b['index'],b['timestamp'],b['data'],b['prev_hash'],copy = True, hashvalue = b['hash'])
				new_blockchain.append(Block(b['index'],b['timestamp'],b['data'],b['prev_hash'],copy=True,hashvalue=b['hash']))

			if self.blockchain.validateChain(new_blockchain) == True:
				self.blockchain.updateBlockChain(new_blockchain)
				print "Update blockchain with longest chain"

		for key,peer in self.peers.iteritems():
			if key != self.kecik_addr:
				msg = encodeMsg({'type': 'peer','request':'consensus_r2','body': self.blockchain.blockChainToDictList()})
				try:
					sock = socket.create_connection(peer)
				except:
					print "No such peer with host and port"
					return
				sock.sendall(msg)


def proofOfWork(prev_proof):
	i = prev_proof + 1
	while((i % 12 == 0 and i % prev_proof == 0) == 0):
		i+= 1
	return i

def getOtherBlocks():
	if request.method == 'GET':
		updatedBlockChain = consensus()
		block_dictlist = []
		for b in updatedBlockChain:
			block_dictlist.append(
			{
			"index": b.index,
			"timestamp": b.timestamp,
			"data": b.data,
			"prev_hash": b.prev_hash,
			"hash": b.hash
			})
			return json.dumps(blockchain_dictlist)









