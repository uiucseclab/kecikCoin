from flask import Flask as flask
from flask import request
import requests
from block import Block
from block import Blockchain
node = flask(__name__)

node_transactions = []
blockchain = Blockchain()
peer_list = []
miner_address = getMiningAddress()

def getMiningAddress():
	sha = hashlib.sha256()
	sha.update(get_mac())
	return str(sha.hexdigest())

@node.route('/transaction',methods = ['POST'])
def transaction():
	if request.method == 'POST':
		new_transaction = request.get_json()
		node_transactions.append(new_transaction)
		print "New transaction"
		print "FROM : {}".format(new_transaction['from'])
		print "TO: {}".format(new_transaction['to'])
		print "AMOUNT: {}".format(new_transaction['amount'])
		return "Transaction submission successful\n"

def proofOfWork(prev_proof):
	i = prev_proof + 1
	while(!(i % 12 == 0 and i % prev_proof == 0)):
		i+= 1
	return i

@node.route('/blockchain', methods = ['GET'])
def getOtherBlocks():
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
		if len(peer_chain) > cur_longest_chain
			cur_longest_chain = peer_chain

	if(cur_longest_chain != blockchain.getBlockChain()):
		new_blockchain = []
		for block in cur_longest_chain:
			new_blockchain.append(Block(block['index'],block['timestamp'],block['prev_hash'],block['hash']))

		if blockchain.validateChain(new_blockchain) == True:
			blockchain.updateBlockChain(new_blockchain)

	return blockchain.getBlockChain()



@node.route('/add_peer',methods = ['GET'])
def addPeer():
	host = request.get_json()['host']
	port = request.get_json()['port']
	peer_list.append(str(host + ':' + port))
	print "Added {} as peer".format(host)
	return()


@node.route('/mine',methods = ['GET'])
def mine():
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
		"prev_hash" : mined_block.prev_hash
		"hash": mined_block.hash
		}) + '\n'
	


def main(args):

	blockchain.populateBlockChain()
	print "Genesis block #{} initialized".format(blockchain.getCurrBlock().index)
	print "Hash: {}\n".format(blockchain.getCurrBlock().hash)
	node = flask(__name__)
	node.run

if __name__ == "__main__":
    main(sys.argv)