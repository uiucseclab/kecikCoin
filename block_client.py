from block_network import *
from block_user import *
import sys

def getBlocks():
	msg = encodeMsg({'request':'get_blocks'})
	try:
		#sock = socket.create_connection((ipport_list[0],int(ipport_list[1])))
		sock = socket.create_connection(('127.0.0.1',6000))
	except:
		print "No such peer with host and port"
		return
	sock.sendall(msg)
	ack = sock.recv(4096)
	receivedchain = decodeMsg(ack)['ack']
	new_blockchain = []
	for b in receivedchain:
		new_block = Block(b['index'],b['timestamp'],b['data'],b['prev_hash'],copy = True, hashvalue = b['hash'])
		new_blockchain.append(Block(b['index'],b['timestamp'],b['data'],b['prev_hash'],copy=True,hashvalue=b['hash']))
		new_block.printBlock()


def checkfunds(userid):
	msg = encodeMsg({'type':'client', 'request':'funds','body': str(userid)})
	try:
		#sock = socket.create_connection((ipport_list[0],int(ipport_list[1])))
		sock = socket.create_connection(('127.0.0.1',6000))
	except:
		print "No such peer with host and port"
		return
	sock.sendall(msg)
	ack = sock.recv(1024)
	receivedmsg = decodeMsg(ack)['ack']
	coins = int(receivedmsg[0])
	index = int(receivedmsg[1])
	print "User {} has {} coins\n".format(userid,coins)
	return (coins,index)


def mine(mineraddr):
	ipport =  raw_input("Please list the ip and port of the peer you wish to mine at as ip:port :\n")
	ipport_list = ipport.split(":")
	msg = encodeMsg({'type':'client', 'request':'mine','body': str(mineraddr)})
	try:
		sock = socket.create_connection((ipport_list[0],int(ipport_list[1])))
		#sock = socket.create_connection(('127.0.0.1',6000))
	except:
		print "No such peer with host and port"
		return
	sock.sendall(msg)
	ack = sock.recv(1024)
	receivedmsg = decodeMsg(ack)['ack']
	datamsg = receivedmsg['data']
	print "MINED BLOCK"
	print "Index:" +  str(receivedmsg['index'])
	print "Timestamp: " + str(receivedmsg['timestamp'])
	print "Data: "
	print "Proof of work: " + str(datamsg['proof_of_work'])
	print "Transactions: " + str(datamsg['transactions'])
	print "Hash: " + str(receivedmsg['hash']) + '\n'


def transaction(user):
	ipport =  raw_input("Please list the ip and port of the peer you wish to make a transaction at as ip:port :\n")
	ipport_list = ipport.split(":")
	dst = raw_input("Enter recipient here: ")
	amount = raw_input("Enter amount here: ")
	print ''

	msg = encodeMsg({'type': 'client','request':'transaction','body': {'from': user.id, 'to': dst, 'amount': amount,'sign': str(user.sign_msg(str(user.id)
		+str(dst) + str(amount)))}})
	try:
		sock = socket.create_connection((ipport_list[0],int(ipport_list[1])))
		#sock = socket.create_connection(('127.0.0.1',6000))
	except:
		print "No such peer with host and port"
		return
	sock.sendall(msg)
	ack = sock.recv(1024)
	print '\n' + str(decodeMsg(ack)['ack'])	


def main():

	mineraddr = getMiningAddress()
	print "\nWelcome to the kecikCoin Client, your miner address is : "
	print str(mineraddr) + '\n'
	userid =  raw_input("Please input you intended user id: ")
	user = KecikUser(userid)
	print "Public and private keys have been generated for user {}\n".format(userid)
	print "Caution, please open peer with port 6000 to open more peers and users\n"

	yes = raw_input("Will this client use port 6000? Y/n? ") 
	if yes != 'y' and yes != 'Y':
		msg = encodeMsg({'type': 'client','request':'add_user','body': {'user': str(userid),'pubkey':user.pubkey}})
		try:
			sock = socket.create_connection(('127.0.0.1',6000))
		except:
			print "No such peer with host and port"
			return
		sock.sendall(msg)

	while True:

		cmd = raw_input("kecikCoinClient> ")

		if(cmd == "exit" or cmd == "quit"):
			#Close up peer if possible
			exit(0)

		elif(cmd == "peer"):
			ipport =  raw_input("Please list the ip and port of the machine you are using as ip:port :\n")
			ipport_list = ipport.split(":")
			#peer = kecikNode('127.0.0.1',6000)
			peer = kecikNode(ipport_list[0],int(ipport_list[1]))

			peer.users[userid] = user.pubkey

			peer_listener = threading.Thread(target = peer.commandListener)
			peer_listener.daemon = True
			peer_listener.start()

			while True:

				peer_cmd = raw_input("kecikCoinClient> ")

				if(peer_cmd == "get_blocks"):
					getBlocks()
					continue

				elif(peer_cmd == "exit" or peer_cmd == "quit"):
					#Close up peer if possible
					exit(0)

				elif(peer_cmd == "mine"):
					mine(user.id)
					continue

				elif(peer_cmd == "join"):
					if(peer.port == 6000):
					#HANDLE THIS EY
						print "Port 6000 is the default the introducer peer. Other peers will join you"
						continue
					else:
						msg = encodeMsg({'type': 'peer','request':'join','body': {'addr': str(peer.kecik_addr),'ipport':(peer.ip,peer.port)}})
						try:
							sock = socket.create_connection(('127.0.0.1',6000))
						except:
							print "No such peer with host and port"
							return
						#sock = socket.create_connection((ipport_list[0],int(ipport_list[1])))
						sock.sendall(msg)
						ack = decodeMsg(sock.recv(1024))
						for k,v in ack['peers'].iteritems():
							peer.peers[str(k)] = v
							msg = encodeMsg({'type': 'peer','request':'join_r2','body':{'peer':{'addr': str(peer.kecik_addr),'ipport':(peer.ip,peer.port)}}})
							try:
								sock = socket.create_connection(v)
							except:
								print "No such peer with host and port"
								return
							sock.sendall(msg)
						for k,v in ack['users'].iteritems():
							peer.users[k] = v
						print "Successfully joined peer group"
						continue

				elif(peer_cmd == "transaction"):
					transaction(user)
					continue

				elif(peer_cmd == "close"):
					peer.alive = False
					break

				elif(peer_cmd == "funds"):
					tup = checkfunds(user.id)
					user.coins = tup[0]
					user.blockindex = tup[1]
					continue

			continue


		elif(cmd == "funds"):
			tup = checkfunds(user.id)
			user.coins = tup[0]
			user.blockindex = tup[1]
			continue

		elif(cmd == "get_blocks"):
			getBlocks()
			continue

		elif(cmd == "mine"):
			mine(user.id)
			continue

			#mine stuff
		elif(cmd == "transaction"):
			transaction(user)
			continue

		else: continue;



if __name__ == "__main__":
    main()
