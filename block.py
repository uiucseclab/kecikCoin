import hashlib
import time
import sys
from uuid import getnode as get_mac

class Block:
	def __init__(self,index,data,prev_hash):
			self.index = index
			self.data = data
			self.time = time.localtime()
			self.prev_hash = prev_hash
			self.hash = self.block_hash()

	def block_hash(self):
		sha = hashlib.sha256()
		sha.update(str(self.index)+str(self.data)+str(self.time)+str(self.prev_hash))
		return sha.hexdigest()


def genesis_block_init():
	return Block(0,"Genesis Block",get_mac())

def add_block(current_block, data):
	return Block(current_block.index + 1, data, current_block.hash)

def main(args):
	blockchain = [genesis_block_init()]
	print "Genesis block #{} initialized".format(blockchain[0].index)
	print "Hash: {}\n".format(blockchain[0].hash)
	prev_block = blockchain[0]
	for i in range(10):
		new_block = add_block(prev_block,"Hi i am block" + str(i + 1))
		blockchain.append(new_block)
		prev_block = new_block
		print "Block #{} has been added to the blockchain!".format(new_block.index)
  		print "Hash: {}\n".format(new_block.hash) 



if __name__ == "__main__":
    main(sys.argv)
