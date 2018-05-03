from block_network import * 
import hashlib
import base64
from ecdsa import SigningKey, NIST384p, VerifyingKey, NIST256p

# kecikUser class
class KecikUser:

	# Constructor that takes in userid
	def __init__(self,userid):
		self.id = userid
		self.coins =  0
		self.blockindex = 0
		keys = self.publicprivateKeygen()
		self.privkey= str(keys[0])
		self.pubkey = str(keys[1])
	

	# RSA Key generator
	def publicprivateKeygen(self):
		prkey = SigningKey.generate(curve=NIST256p)
		prkey_string = prkey.to_pem()
		pubkey = prkey.get_verifying_key()
		pubkey_string = pubkey.to_pem()
		keys = (prkey_string,pubkey_string)
		return keys

	# Signing message with privkey function
	def sign_msg(self,msg):
		hashed_msg = hashlib.sha256(str(msg)).hexdigest()
		sign_key.from_pem(self.privkey,curve = NIST256p)
		return sign_key.sign(hashed_msg)

	# Decrypting message with pubkey function
	def unsign_msg(self,msg,sign,publickey):
		hashed_msg = hashlib.sha256(str(msg['from']) + str(msg['to']) + str(msg['amount'])).hexdigest()
		pubkey = VerifyingKey.from_pem(publickey,curve=NIST256p)
		return pubkey.verify(sign,msg)
