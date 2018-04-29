from flask import Flask as flask
from flask import request
from block import Block
from block import Blockchain
node = flask(__name__)

node_transactions = []
miner_list = []
blockchain = []
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

@node.route('/add_peer',methods = ['GET'])
	host = request.args
	

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
		"hash": mined_block.hash
		}) + '\n'
	


def main(args):
	blockchain = Blockchain()
	print "Genesis block #{} initialized".format(blockchain[0].index)
	print "Hash: {}\n".format(blockchain[0].hash)
	node = flask(__name__)
	node.run

if __name__ == "__main__":
    main(sys.argv)