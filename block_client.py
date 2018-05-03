from block_network import *
from block_user import *
import sys

# Sends the server a message to retrieve the blockchain and displays it
def getBlocks():

	# Setting up the request
	msg = encodeMsg({'request':'get_blocks'})
	try:
		sock = socket.create_connection(('127.0.0.1',6000))
	except:
		print "No such peer with host and port"
		return
	sock.sendall(msg)
	ack = sock.recv(4096)
	receivedchain = decodeMsg(ack)['ack']

	# Assemble blockchain from from blockchain dictionary list we received
	new_blockchain = []
	for b in receivedchain:
		new_block = Block(b['index'],b['timestamp'],b['data'],b['prev_hash'],copy = True, hashvalue = b['hash'])
		new_blockchain.append(Block(b['index'],b['timestamp'],b['data'],b['prev_hash'],copy=True,hashvalue=b['hash']))
		new_block.printBlock()


# Client function to send server a message requesting the total amount of funds for userid
def checkfunds(userid):
	# Set up fund request message
	msg = encodeMsg({'type':'client', 'request':'funds','body': str(userid)})
	try:
		sock = socket.create_connection(('127.0.0.1',6000))
	except:
		print "No such peer with host and port"
		return
	sock.sendall(msg)
	ack = sock.recv(4096)
	receivedmsg = decodeMsg(ack)['ack']

	# Get coins from tuple
	coins = int(receivedmsg[0])

	# Get index of last block scanned
	index = int(receivedmsg[1])

	# Display values to user
	print "User {} has {} coins\n".format(userid,coins)

	# Return coins and index as tuple
	return (coins,index)

# Mining Function to send server a message to mine 1 block and reward the user with it
def mine(mineraddr):

	# Prompt user for which peer to mine block at
	ipport =  raw_input("\nPlease list the ip and port of the peer you wish to mine at as ip:port :\n")
	ipport_list = ipport.split(":")
	msg = encodeMsg({'type':'client', 'request':'mine','body': str(mineraddr)})
	try:
		sock = socket.create_connection((ipport_list[0],int(ipport_list[1])))
	except:
		print "No such peer with host and port"
		return

	# Send the message
	sock.sendall(msg)
	ack = sock.recv(4096)

	# Decode Message
	receivedmsg = decodeMsg(ack)['ack']
	datamsg = receivedmsg['data']

	# Print out contents of mined block
	print "\nMINED BLOCK"
	print "Index:" +  str(receivedmsg['index'])
	print "Timestamp: " + str(receivedmsg['timestamp'])
	print "Data: "
	print "Proof of work: " + str(datamsg['proof_of_work'])
	print "Transactions: " + str(datamsg['transactions'])
	print "Hash: " + str(receivedmsg['hash']) + '\n'

# Mining Function to send server a message to record transaction of user
def transaction(user):

	# Prompt which peer to send transaction to and how much the user wants to send
	ipport =  raw_input("\nPlease list the ip and port of the peer you wish to make a transaction at as ip:port :\n")
	ipport_list = ipport.split(":")
	dst = raw_input("Enter recipient here: ")
	amount = raw_input("Enter amount here: ")
	print ''

	# Set up message request
	msg = encodeMsg({'type': 'client','request':'transaction','body': {'from': user.id, 'to': dst, 'amount': amount,'sign': str(user.sign_msg(str(user.id)
		+str(dst) + str(amount)))}})
	try:
		sock = socket.create_connection((ipport_list[0],int(ipport_list[1])))
	except:
		print "No such peer with host and port"
		return

	sock.sendall(msg)
	ack = sock.recv(1024)

	# Print status of transaction received froms server
	print '\n' + str(decodeMsg(ack)['ack'])	


# Front end client function for kecikCoin
def main():

	# Set up miner address (hash of mac-address) of current user and display
	mineraddr = getMiningAddress()
	print "\nWelcome to the kecikCoin Client, your miner address is : "
	print str(mineraddr) + '\n'

	# Obtain userid from user
	userid =  raw_input("Please input you intended user id: ")

	# Make new user
	user = KecikUser(userid)

	# Display warnings and necessary requirements
	print "Public and private keys have been generated for user {}\n".format(userid)
	print "Caution, please open peer with port 6000 to open more peers and users\n"

	# Prompt user if they will open port 6000
	yes = raw_input("Will this client use port 6000? Y/n? ") 

	# If not port 6000, contact port 6000 to add user to the network
	if yes != 'y' and yes != 'Y':
		msg = encodeMsg({'type': 'client','request':'add_user','body': {'user': str(userid),'pubkey':user.pubkey}})
		try:
			sock = socket.create_connection(('127.0.0.1',6000))
		except:
			print "No such peer with host and port"
			return
		sock.sendall(msg)

	#Main front end while loop
	while True:

		# Console prompt
		cmd = raw_input("\nkecikCoinClient> ")

		# If exit is prompted, quit
		if(cmd == "exit" or cmd == "quit"):
			exit(0)

		# Open up kecikNode
		elif(cmd == "peer"):

			# List host ip address and port you wish to have as receiving port
			ipport =  raw_input("\nPlease list the ip and port of the machine you are using as ip:port :\n")
			ipport_list = ipport.split(":")

			# Instantiate peer
			peer = kecikNode(ipport_list[0],int(ipport_list[1]))

			# Put user into network
			peer.users[userid] = user.pubkey

			# Open up command listening thread for the peer
			peer_listener = threading.Thread(target = peer.commandListener)
			peer_listener.daemon = True
			peer_listener.start()

			# Peer console controller
			while True:

				peer_cmd = raw_input("kecikCoinClient> ")

				# Toggling debug to either show or hide network messages
				if(peer_cmd == "debug"):
					if(peer.debug == False):
						peer.debug = True
						print "Network debugging turned on\n"
					else:
						peer.debug = False
						print "Network debugging turned off\n"

				# Get and display blocks in terminal
				elif(peer_cmd == "get_blocks"):
					getBlocks()
					continue

				# Exit from program
				elif(peer_cmd == "exit" or peer_cmd == "quit"):
					#Close up peer if possible
					exit(0)

				# Mine from chosen peer
				elif(peer_cmd == "mine"):
					mine(user.id)
					continue

				# Join a kecikCoin network
				elif(peer_cmd == "join"):

					# Peer 6000 is introducer
					if(peer.port == 6000):
						print "Port 6000 is the default the introducer peer. Other peers will join you"
						continue
					else:

						#Set up message and send ip and port to signal to 6000 to get peer list
						msg = encodeMsg({'type': 'peer','request':'join','body': {'addr': str(peer.kecik_addr),'ipport':(peer.ip,peer.port)}})
						try:
							sock = socket.create_connection(('127.0.0.1',6000))
						except:
							print "No such peer with host and port"
							return

						sock.sendall(msg)
						ack = decodeMsg(sock.recv(4096))

						# Once receive peer dictionary list, parse
						for k,v in ack['peers'].iteritems():

							#Add peer to network
							peer.peers[str(k)] = v

							# Send your own peer network and info in another message all peers in the list received from 6000
							msg = encodeMsg({'type': 'peer','request':'join_r2','body':{'peer':{'addr': str(peer.kecik_addr),'ipport':(peer.ip,peer.port)}}})
							try:
								sock = socket.create_connection(v)
							except:
								print "No such peer with host and port"
								return
							sock.sendall(msg)

						# Parse through received user list and add users to user list
						for k,v in ack['users'].iteritems():
							peer.users[k] = v

						print "Successfully joined peer group"
						continue

				# User with peer command for transactions
				elif(peer_cmd == "transaction"):
					transaction(user)
					continue

				# Close peer
				elif(peer_cmd == "close"):
					peer.alive = False
					break

				# User with peer command for funds
				elif(peer_cmd == "funds"):
					tup = checkfunds(user.id)
					user.coins = tup[0]
					user.blockindex = tup[1]
					continue

			continue

		# User only command for funds
		elif(cmd == "funds"):
			tup = checkfunds(user.id)
			user.coins = tup[0]
			user.blockindex = tup[1]
			continue

		# User only command to display blocks
		elif(cmd == "get_blocks"):
			getBlocks()
			continue

		# User only command to mine blocks
		elif(cmd == "mine"):
			mine(user.id)
			continue

		# User only command to make transactions
		elif(cmd == "transaction"):
			transaction(user)
			continue

		else: continue;



if __name__ == "__main__":
    main()
