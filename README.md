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

As of now, the proof of work is simple enough such that it is easy to mine coins. This helps us to debug as we don't have to wait for a period of time to get a mined block. Obviously, in a real world blockchain, this is not the case!

Most of the networking done in this blockchain is done through socket programming on ip addresses and ports. All the messages are routed in TCP-packets to ensure reliability of connection.

This blockchain is developed by Nurul Atiqah Hamzah (hamzah3) and Izz Irfan (mohdfau2) [May 2018]

## Research and Future Additions That Could Have Been Added
----------

A lot of time and research had been put into deciding how this blockchain would turn out and this section would detail the security implementations that we learned about that we did not implement in our blockchain either due to time limitation, complexity or being beyond the scope of our project. 

### 1. Stealth Addresses
In our research, we came across a new implementation of public and private keys for transactions in Blockchain that implemented the Diffie-Hilman key exchange algorithm to generate a one time secret key for each transaction. Because the secret key is different for each transaction, this helps prevent anybody from being to trace the transactions of a specific user despite the blockchain being a public ledger.

### 2. RingCT
We came across MONERO coin that implemented ring signature based transactions in which a transaction from a certain user would actually be consisted of other transactions (from a group of users referred to as the ring). This way, it hides the transaction of the user from the other users when they scan the blockchain.


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

Once you start up another peer server on a different port by typing 'peer' into the console and designating the desired ip and port by entering $ip_addr:$port at the prompt, you can join the kecikCoin network by entering 'join' in the console.

The different commands that you can put into kecikCoinClient console is:
<ul>
<li>peer<br>Set up a new peer server</li>
  
<li>join<br>Once a peer server is set up, have the peer join the kecikCoin network</li>
  
<li>get_blocks<br>Get blocks from the server and print the content of each</li>
  
<li>funds<br>Get funds from the server and put into user class</li>

<li>mine<br>Mine a block from the server</li>

<li>transaction<br>Make a transaction to send funds to another user</li>

<li>exit/quit<br>Get out of the program</li>

<li>debug<br>Toggle networking debugging on and off. When turned on, since network working works on a different thread, don't worry if the kecikCoin console prompt appears elsewhere or glitchy, you can still enter commands</li>
</ul>

## Demo Pictures
----------
Running 'python block_client.py'<br>
![Screen](https://github.com/atiqahhhamzah/cs460_bchain/blob/master/demo_pics/Screen%20Shot%202018-05-02%20at%205.25.31%20PM.png)

Entering user id<br>
![Screen](https://github.com/atiqahhhamzah/cs460_bchain/blob/master/demo_pics/Screen%20Shot%202018-05-02%20at%205.25.45%20PM.png)

For first instance of program, answer 'y'<br>
![Screen](https://github.com/atiqahhhamzah/cs460_bchain/blob/master/demo_pics/Screen%20Shot%202018-05-02%20at%205.25.59%20PM.png)

Enter networking info in form of $ip:6000 for first instance<br>
![Screen](https://github.com/atiqahhhamzah/cs460_bchain/blob/master/demo_pics/Screen%20Shot%202018-05-02%20at%205.26.19%20PM.png)

A different instance of the client can be initiated with a different port and must be followed with 'join' to join network<br>
![Screen](https://github.com/atiqahhhamzah/cs460_bchain/blob/master/demo_pics/Screen%20Shot%202018-05-02%20at%205.39.57%20PM.png)

Mining a block<br>
![Screen](https://github.com/atiqahhhamzah/cs460_bchain/blob/master/demo_pics/Screen%20Shot%202018-05-02%20at%205.40.31%20PM.png)

Displaying blocks<br>
![Screen](https://github.com/atiqahhhamzah/cs460_bchain/blob/master/demo_pics/Screen%20Shot%202018-05-02%20at%205.40.44%20PM.png)

Making a transaction<br>
![Screen](https://github.com/atiqahhhamzah/cs460_bchain/blob/master/demo_pics/Screen%20Shot%202018-05-02%20at%205.41.00%20PM.png)

Checking funds of user<br>
![Screen](https://github.com/atiqahhhamzah/cs460_bchain/blob/master/demo_pics/Screen%20Shot%202018-05-02%20at%205.41.42%20PM.png)

## How it Works
----------
The following is a breakdown of what each aspect of the project accomplishes. 

### 1. block_client.py
------
This our main program that runs a while loop to prompt for commands. Most of the commands that are entered will then send an AES-encrypted message that is contained in json for easy parsing to the server (or peer machine). It acts as both a user client and peer client so it is not necessary to open up a peer machine in the client (unless you are port 6000). This is also the main code that handles user related functions such as signing up as a user, checking funds, making transactions and mining blocks.

### 2. block_user.py
----------
This contains our class declaration of kecikUser where funds and the last block index are recorded. The kecikUser has two functions for encrypting and decrypting the RSA encrypted signatures for transactions.

### 3. block_network.py
----------
This file contains our class declaration of KecikNode which contains the running commandListener server thread that handles all the incoming requests from peers and users. This class also holds user information in the form key,value dictionaries for userid and their public keys and also the network's list of peers. 

There is also a consensus function that prompts other nodes to send their blockchains and does a length comparison between their blockchains and node's current blockchain. Once, the longest blockchain is selected, it goes through a validation function that tests each block's hash to ensure that each block has a prev_hash that matches the hash of the block with an index below them. Once validation is completed, the blockchain is updated with the new blockchain.

If a user makes a transaction, the transactions are kept in a list contained within the node. However, the transactions do not become 'official' until the transactions are published in a block that has been mined.

If a user mines a block, all the transactions kept in the node are collected and a proof-of-work algorithm is ran to completion. Once the proof-of-work is done, the value that is output is recorded along with the current list of transactions inside the data section of the block that is newly mined. The new block is then added to the peer's blockchain. Lastly, the consensus function is called to ensure that all peers have the same blockchain.


### 4. block.py
----------
This contain the class declarations of Block and Blockchain which contain different functions for constructing the blockchain, block, printing it out, copying the block or blockchain and many other necessary functions.
