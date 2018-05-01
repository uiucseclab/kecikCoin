import hashlib
import json
import socket
import time
from block import *
import sys
import argparse
from uuid import getnode as get_mac
import threading

def encodeMsg(msg):
		retmsg = json.JSONEncoder().encode(msg)
		return retmsg
	# decode the recieved string into a json dict
def decodeMsg(msg):
		received = json.loads(msg)
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
		self.kecik_addr = getMiningAddress(host = host, port = port)
		self.alive = True
		self.peers = dict()
		self.node_transactions = []
		self.blockchain = Blockchain()
		self.blockchain.populateBlockChain()
		print "\nGenesis block #{} initialized at {}:{}".format(self.blockchain.getCurrBlock().index, self.host, self.port)	
		print "Hash: {}\n".format(self.blockchain.getCurrBlock().hash)


	def commandHandler(self, client, addr):
		while True:
			# Decode command msg
			command = client.recv(1024)
			commandMsg = decodeMsg(command)

			#Check if client is in peer list or peer wants to join
			clientHostName = socket.gethostbyaddr(addr[0])[0]
			found = 0
			for key,value in self.peers.iteritems():
				print key
				if key.find(clientHostName) != -1:
					found+=1
			if found == 0 and (commandMsg['request'] != 'join' and commandMsg['type'] == 'peer'):
				print >>sys.stderr, "%s not in peer list" %clientHostName
				client.close()
				return

			#Print out command entries
			print >>sys.stderr, "Received message from %s: %s\n" % (addr[0], commandMsg)

			#if received join command, add to peer list and send blocks
			if(commandMsg['type'] == 'peer'):
				if (commandMsg['request'] == 'join'):
					client.send(encodeMsg("OK"))
					client.close()
					return
				elif(commandMsg['request'] == 'consensus'):
					client.send("OK")
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
					client.send(encodeMsg("OK"))
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


def consensus():
	global blockchain
	cur_longest_chain = blockchain.getBlockChain()

	peer_chains = []
	for peer in peer_list():
		req_response = requests.get("https://%s/blockchain" % peer)
		if (req_response.status_code == requests.codes.ok):
			print "Blocks from peer {}: {}\n".format(peer,req_response.content())
			peer_chains.append(json.loads(req_response.content()))

	for chain in peer_chains:
		if len(peer_chain) > cur_longest_chain:
			cur_longest_chain = peer_chain

	if(cur_longest_chain != blockchain.getBlockChain()):
		new_blockchain = []
		for block in cur_longest_chain:
			new_blockchain.append(Block(block['index'],block['timestamp'],block['prev_hash'],block['hash']))

		if blockchain.validateChain(new_blockchain) == True:
			blockchain.updateBlockChain(new_blockchain)

	return blockchain.getBlockChain()


def addPeer():
	if request.method == 'GET':
		host = request.get_json()['host']
		port = request.get_json()['port']
		peer_list.append(str(host + ':' + port))
		print "Added {} as peer".format(host)

def mine():
	if(request.method == 'GET'):
		prev_block = blockchain.getCurrBlock()
		prev_proof = prev_block.data['proof_of_work']
		new_proof = proofOfWork(prev_proof)
		node_transactions.append({'from':'network','to': miner_address,'amount':1})
		new_block_data = {'proof_of_work': new_proof,'transactions':list(node_transactions)}
		new_block_index = prev_block.index + 1
		node_transactions[:] = []
		blockchain.addBlock(new_block_data)
		mined_block = blockchain.getCurrBlock()
		return json.dumps({
		"index": new_block_index,
		"timestamp": mined_block.timestamp,
		"data": new_block_data,
		"prev_hash" : mined_block.prev_hash,
		"hash": mined_block.hash
		}) + '\n'









