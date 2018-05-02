from block_network import *
import socket
import random
import threading
import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import thread
import hashlib


class KecikUser:

	def __init__(self,userid):
		self.id = userid
		self.coins =  0
		self.blockindex = 0
		keys = self.publicprivateKeygen()
		self.pubkey = keys[1]
		self.privkey = keys[0]

	def publicprivateKeygen(self):
		random_gen = Random.new().read
		key = RSA.generate(1024, random_gen)
		keys = (key, key.publickey().exportKey('PEM'))
		return keys

	def sign_msg(self,msg):
		hashed_msg = hashlib.sha256(str(msg)).hexdigest()
		return self.privkey.encrypt(hashed_msg,32)

	def unsign_msg(self,msg,sign,publickey):
		hashed_msg = hashlib.sha256(str(msg['from']) + str(msg['to']) + str(msg['amount'])).hexdigest()
		pubkey = RSA.importKey(publickey,passphrase="PEM")
		if publickey.decrypt(sign) == hashed_msg:
			return True
		else:
			return False
