from block_network import *
import sys

def main():

	mineraddr = getMiningAddress()
	print "\nWelcome to the kecikCoin Client, your miner address is : "
	print str(mineraddr) + '\n'

	while True:

		cmd = raw_input("kecikCoinClient> ")

		if(cmd == "exit" or cmd == "quit"):
			#Close up peer if possible
			exit(0)

		elif(cmd == "peer"):
			#ipport =  raw_input("Please list the ip and port of the machine you are using as ip:port :\n")
			#ipport_list = ipport.split(":")
			peer = kecikNode('127.0.0.1',6000)
			#peer = kecikNode(ipport_list[0],int(ipport_list[1]))

			peer_listener = threading.Thread(target = peer.commandListener)
			peer_listener.daemon = True
			peer_listener.start()

			#Start block_network class
		elif(cmd == "mine"):
			#ipport =  raw_input("Please list the ip and port of the peer you wish to mine at as ip:port :\n")
			#ipport_list = ipport.split(":")
			msg = encodeMsg({'type':'client', 'request':'mine','body': str(mineraddr)})
			sock = socket.create_connection(('127.0.0.1',6000))
			#sock = socket.create_connection((ipport_list[0],int(ipport_list[1])))
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

			#mine stuff
		elif(cmd == "transaction"):
			#ipport =  raw_input("Please list the ip and port of the peer you wish to make a transaction at as ip:port :\n")
			#ipport_list = ipport.split(":")
			dst = raw_input("Enter recipient here: ")
			amount = raw_input("Enter amount here: ")
			print ''
			msg = encodeMsg({'type': 'client','request':'transaction','body': {'from': str(mineraddr), 'to': dst, 'amount': amount}})
			sock = socket.create_connection(('127.0.0.1',6000))
			#sock = socket.create_connection((ipport_list[0],int(ipport_list[1])))
			sock.sendall(msg)
			ack = sock.recv(1024)
			print '\n' + str(decodeMsg(ack)['ack'])

		else: continue;

if __name__ == "__main__":
    main()
