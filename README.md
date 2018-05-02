# kecikCoin for CS460
----------
The main purpose of kecikCoin blockchain is to emulate a small scale non-persistent peer-to-peer blockchain program using Python 2.7. There is a blockchain client, user, and node in which users can send different instructions to mine, make a transaction, look at the blocks and look at their funds through the client. The security features of this blockchain are:
<ul>
  <li>Consensus algorithm among blockchain peers</li>
  <li>Proof-of-work algorithm</li>
  <li>AES encrypted network traffic</li>
  <li>SHA256 Hash pointers for the blocks in the blockchain for blockchain validation</li>
  <li>RSA signed transactions</li>
</ul>

This blockchain is developed by Nurul Atiqah Hamzah (hamzah3) and Izz Irfan (mohdfau2) [May 2018]

## Installation Dependencies
----------
Pycrypto <br>
Python 2.7

## Usage
------
The blockchain can operate with a maximum of five machines, in which each of the five machines are designated with a specific user and can become a peer machine. For easy debugging or simulation purposes, you can just bring up all machines on localhost and designate each peer with a different port.

This blockchain requires bring up a peer with port 6000 open as this peer will be the introducer node that can bring other nodes and users into the kecikCoin network. 

Each machine can start each node by running:<br>
python block_client.py

To make port 6000 a peer: <br>
At the kecikCoin console: type 'peer'<br>
Once prompted, put in: $ip_addr:6000


## How it Works
------
The following is a breakdown of what each aspect of the project accomplishes. 

### 1. client.py
------
This is the front-end tool that allows users to send and recieve messages from the server. Upon recieving the message from the server, the client will compare the hashes of the sent and recieved messages to ensure integrity. 


a) AES Encrypt via Node 3's AES Key the following: [message + Node3_IP]

b) RSA Encrypt Node 3's AES Key with Node 3's public RSA key: [Node3_AESKey]

c) Concatenate the two encrypted messages - this is the inner most layer and the process will repeat two more times.

By the end of the encryption scheme, the following is the result:

_Layer 1_: AES[message + DestinationIP] + RSA[Node3_AESKey]

_Layer 2_: AES[AES[message + DesinationIP] + RSA[Node3_AESKey] + Node3_IP] + RSA[Node2_AESKey]

_Layer 3_: AES[AES[AES[message + DestinationIP] + RSA[Node3_AESKey] + Node2_IP] + RSA[Node2_AESKey] + Node1_IP] + RSA[Node1_AESKey]

It is the each node's responsibility to unwrap each layer via its RSA private key and continue to send the message along.

### 2. directory.py
------
The directory node is designed to send the client (upon request) the list of node IP's and their corresponding public RSA keys. Before the client can make a valid request to the directory node, each onion routing node must first send its IP and its RSA public key to the directory - this is an initialization phase.

### 3. node.py
------
This represents each onion routing node (and has cases for both entrance and exit nodes) and must unwrap one layer of encryption and send the message along. The decryption occurs as follows:

_Message Sent to Node_: AES[AES[message + DesinationIP] + RSA[Node3_AESKey] + Node3_IP] + RSA[Node2_AESKey]

Node 2 uses its private RSA key to obtain the AES Key, and then uses that AES Key to decrypt the remaining contents and obtain the next node's IP. The result is:

_Message Node 2 Sends to Node 3_: AES[message + DesinationIP] + RSA[Node3_AESKey]

### 4. server.py
------
The purpose of server is to simply recieve messages and send the hashed version of the message back to the original exit node. 
