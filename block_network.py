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

# AES key
key = ['b', '1', '\xc7', '&', '\xf2', '\xc4', 'Z', 'J', '8', '\x08', '&', '\x85', '\x85', '\x92', '\xfc', '=']

# AES 16-byte IV
iv = ['J', '\x8c', '\x00', '\xa4', '\x17', '\xab', 'n', '\x82', '\x92', ':', '[', '\x0f', 'K', '\xc2', '\x88', '\xbf']
aes_key = ''.join(key)
aes_iv = ''.join(iv)

# Padding function and padding to be 16-byte modulus
pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

# Message encoder that first encodes it as JSON and then encrypts with AES
def encodeMsg(msg):
	retmsg = json.JSONEncoder().encode(msg)
	aes_msg = AES.new(aes_key, AES.MODE_CBC, aes_iv).encrypt(pad(retmsg))
	return aes_msg

# Message decoder that decrypts the AES-encrypted message and decode the JSON dictionary
def decodeMsg(msg):
	aes_msg = unpad(AES.new(aes_key, AES.MODE_CBC,aes_iv).decrypt(msg))
	received = json.loads(aes_msg)
	return received

# Mining address for peer that includes the port
def getMiningAddress(host = '',port = ''):
	sha = hashlib.sha256()
	sha.update(str(get_mac()) + str(host) + str(port))
	return str(sha.hexdigest())

# Simple proof-of-work
def proofOfWork(prev_proof):
	i = prev_proof + 1
	while((i % 12 == 0 and i % prev_proof == 0) == 0):
		i+= 1
	return i

# kecikNode peer class declaration
class kecikNode:

	# Set up all necessary variables for the node
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

		# Set up blockchain and initialize the genesis block
		self.blockchain = Blockchain()
		self.blockchain.populateBlockChain()

		# Debug flag
		self.debug = False

		print "\nGenesis block #{} initialized at {}:{}".format(self.blockchain.getCurrBlock().index, self.host, self.port)	
		print "Hash: {}\n".format(self.blockchain.getCurrBlock().hash)

	# Toggle debug flag
	def setDebug():
		self.debug = True

	# Handles incoming tcp packets received through defined port
	def commandHandler(self, client, addr):
		while True:
			# Decode command msg
			command = client.recv(4096)
			commandMsg = decodeMsg(command)

			#Check if client is in peer list or peer wants to join
			clientHostName = socket.gethostbyaddr(addr[0])[0]

			#Print out command entries
			if(self.debug): print >>sys.stderr, "\nReceived message from %s: %s\n" % (addr[0], commandMsg)

			#if received join command, add to peer list and send blocks
			if(commandMsg['request'] == 'get_blocks'):
				self.consensus()
				msg = {'ack':self.blockchain.blockChainToDictList()}
				client.send(encodeMsg(msg))
				client.close()
				return

			# Return funds for specified user
			elif (commandMsg['request'] == 'funds'):

				# Run consensus to get correct blockchain
				self.consensus()

				# Set up default coins for userid to 0
				userid = str(commandMsg['body'])
				coins = 0

				# Scan through updated blockchain to finds allocated to and from user
				for b in self.blockchain.getBlockChain():
					for t in b.data['transactions']:
						if t['to'] == userid:
							coins += t['amount']
						elif t['from'] == userid:
							coins -= t['amount']

				# Send back desired info
				msg = {'ack': (coins, len(self.blockchain.blockchain) - 1)}
				client.send(encodeMsg(msg))
				client.close()
				return

			# Receive command to add peer to network
			elif(commandMsg['type'] == 'peer'):

				# First round for join sends back to peer the membership list
				if (commandMsg['request'] == 'join'):
					ackMsg = encodeMsg({'peers':self.peers,'users':self.users})
					client.send(ackMsg)
					client.close()
					return

				# Second round, the peer is finally recorded in peer list
				elif(commandMsg['request'] == 'join_r2'):
					self.peers[str(commandMsg['body']['peer']['addr'])] = commandMsg['body']['peer']['ipport']
					self.consensus()
					client.close()
					return

				# First round of consensus, send own blockchain
				elif(commandMsg['request'] == 'consensus'):
					msg = {'ack':self.blockchain.blockChainToDictList()}
					client.send(encodeMsg(msg))
					client.close()
					return

				# Second round of consensus, receive the longest blockchain determined through initial consensus round
				elif(commandMsg['request'] == 'consensus_r2'):
					new_blockchain = []
					for b in commandMsg['body']:
						new_blockchain.append(Block(b['index'],b['timestamp'],b['data'],b['prev_hash'],copy=True,hashvalue=b['hash']))
					if self.blockchain.validateChain(new_blockchain) == True:
						self.blockchain.updateBlockChain(new_blockchain)
						if(self.debug): print "Updated blockchain with longest chain"
					client.close()
					return

			# User commands
			elif (commandMsg['type'] == 'client'):

				# Add user transaction to list of transactions processed
				if(commandMsg['request'] == 'transaction'):
					new_transaction = commandMsg['body']
					node_transactions.append(new_transaction)
					if(self.debug):
						print "New transaction"
						print "FROM : {}".format(new_transaction['from'])
						print "TO: {}".format(new_transaction['to'])
						print "AMOUNT: {}".format(new_transaction['amount'])
					client.send(encodeMsg({'ack':"Transaction submission successful"}))
					client.close()
					return

				# Mine a block and add it blockchain
				elif(commandMsg['request'] == 'mine'):

					# Get current block information
					prev_block = self.blockchain.getCurrBlock()
					prev_proof = prev_block.data['proof_of_work']
					new_proof = proofOfWork(prev_proof)

					# Append mining reward transaction to list
					self.node_transactions.append({'from':'network','to': str(commandMsg['body']),'amount':1})

					# Set up new block inputs
					new_block_data = {'proof_of_work': new_proof,'transactions':list(self.node_transactions)}
					new_block_index = prev_block.index + 1

					# Clear up processing transactions
					self.node_transactions[:] = []

					# Add mined block
					self.blockchain.addBlock(new_block_data)

					# Send back block as a dictionary
					mined_block = self.blockchain.getCurrBlock()
					msg = {'ack':{'index': new_block_index, 'timestamp': mined_block.timestamp, 'data': new_block_data, 
								  'prev_hash': mined_block.prev_hash, 'hash': mined_block.hash}}
					client.send(encodeMsg(msg))

					# Run consensus algorithm
					self.consensus()
					client.close()
					return

				# Add new user in body to user list
				elif(commandMsg['request'] == 'add_user'):
					self.users[commandMsg['body']['user']] = commandMsg['body']['pubkey']
					client.close()
					return

		if(self.debug): print >>sys.stderr, "Unknown command message"
		client.close()


	# Command listener threads for kecikCoin Server
	def commandListener(self):
		try:
			# Set up listening socket
			self.listener = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.listener.bind((self.ip, self.port))
			if(self.debug):print >>sys.stderr,"Starting to listen for commands on port %s"%self.port

		except socket.error as e:
			raise Exception("Unable to set up listener : %s" %e)
			return

		# Limit 5 packets to receive at once
		self.listener.listen(5)

		# Branch out into different thread once receive a packet
		while self.alive == True:
			clientSock, remoteAddr = self.listener.accept()
			thread.start_new_thread(self.commandHandler,(clientSock, remoteAddr))
		self.listener.close()
		if(self.debug):print >>sys.stderr, ("Closing up command listener")

	# Consensus algorithm to ensure funginess and coherency of blockchain
	def consensus(self):
		if(self.debug):print "Starting consensus algorithm"

		# Set up your own blockchain as longest chain
		longest_chain = self.blockchain.getBlockChain()
		peer_chains = []

		# Send request for others blockchain
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

		# Get longest chain from list of chains
		for chain in peer_chains:
			if(len(chain) > len(longest_chain)):
				longest_chain = chain

		# Make an actual blockchain for the dictionary list received
		if(longest_chain != self.blockchain.getBlockChain()):
			new_blockchain = []
			for b in longest_chain:
				new_block = Block(b['index'],b['timestamp'],b['data'],b['prev_hash'],copy = True, hashvalue = b['hash'])
				new_blockchain.append(Block(b['index'],b['timestamp'],b['data'],b['prev_hash'],copy=True,hashvalue=b['hash']))

			# Validate the new blockchain
			if self.blockchain.validateChain(new_blockchain) == True:
				self.blockchain.updateBlockChain(new_blockchain)
				if(self.debug):print "Updated blockchain with longest chain"

		# Send out the longest chain to have everyone update
		for key,peer in self.peers.iteritems():
			if key != self.kecik_addr:
				msg = encodeMsg({'type': 'peer','request':'consensus_r2','body': self.blockchain.blockChainToDictList()})
				try:
					sock = socket.create_connection(peer)
				except:
					print "No such peer with host and port"
					return
				sock.sendall(msg)








