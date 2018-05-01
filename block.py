import hashlib
import time
import sys
import thread
from uuid import getnode as get_mac

class Block:
	# This is the constructor for a new block which takes an index, the data, and the hash of a previous block
	def __init__(self,index, timestamp, data,prev_hash,copy = False,hashvalue = 0):
		self.index = index
		self.timestamp = timestamp
		self.data = data
		self.prev_hash = prev_hash
		if copy == False:
			self.hash = self.getBlockHash()
		else:
			self.hash = hashvalue

	# This will be the hashing function for our block
	def getBlockHash(self):
		return hashlib.sha256(str(self.index)+str(self.data)+str(self.timestamp)+str(self.prev_hash)).hexdigest()
		
	def printBlock(self):
		print "BLOCK #{}".format(self.index)
		print "Index : {}".format(self.index)
		print "Data : {}".format(self.data)
		print "Timestamp : {}".format(self.timestamp)
		print "Hash : {}".format(self.hash)


class Blockchain:

	# This is the constructor for our blockchain, which is just a list
	def __init__(self):
		self.blockchain = []
		self.length = 0

	def populateBlockChain(self):
		self.blockchain.append(self.genesisBlockInit())
		self.length = 1

	# The first block, called the genesis block, which will hash our mac address, so you where it originates
	def genesisBlockInit(self):
		return Block(0,0,{'proof_of_work':1, 'transactions':[]},get_mac())

	def updateBlockChain(self,new_blockchain):
		self.blockchain = new_blockchain
		self.length = len(new_blockchain)

	def getBlockChain(self):
		return self.blockchain

	# Get current block function
	def getCurrBlock(self):
		return self.blockchain[self.length - 1]

	# Appending a block with data parameter onto the chain
	def addBlock(self,data):
		prev_index = self.blockchain[self.length - 1].index
		prev_hash = self.blockchain[self.length  - 1].hash
		self.blockchain.append(Block(prev_index + 1, time.time(),data, prev_hash))
		self.length += 1

	# Chain validation
	def validateChain(self):
		for i in range(self.length - 1):
			currentHash = self.blockchain[i]
			next_block_prevHash = self.blockchain[i+1].prev_hash
			if currentHash != next_block_prevHash:
				return False;
		return True;

