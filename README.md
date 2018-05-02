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
----------
Caution: It was developed on MacOS so for a smoother experience, use a mac terminal to run this.

The blockchain can operate with a maximum of five machines, in which each of the five machines are designated with a specific user and can become a peer machine. For easy debugging or simulation purposes, you can just bring up all machines on localhost and designate each peer with a different port.

This blockchain requires that peer with port 6000 open is up at all times as this peer will be the introducer node that can bring other nodes and users into the kecikCoin network. 

Each machine can start each node by running:<br>
python block_client.py

To make port 6000 a peer: <br>
At the kecikCoin console: type 'peer'<br>
Once prompted, put in: $ip_addr:6000

The different commands that you can put into kecikCoinClient console is:

###get_blocks
####Get blocks from the server and print the content of each

###funds
####Get funds from the server and put into user class

###mine
####Mine a block from the server

###transaction
####Make a transaction to send funds to another user


## How it Works
------
The following is a breakdown of what each aspect of the project accomplishes. 

### 1. block_client.py
------


### 2. block_user.py
------


### 3. block_network.py
------


### 4. block.py
------
 
