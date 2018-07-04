
# Cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Local imports
from . import database

class Wallet(object):
	""" Wallet holds the private and public keys of an owner.
	These keys are generated using RSA encryption algorithm.
	Private key is encrypted with a password provided by the user.
	"""
	@classmethod
	def generate(cls, owner, password,
					public_exponent=65537, key_size=1024, backend=None):
		"""Generates a new pair of private and public key using RSA
		encryption algorithm and initializes a Wallet instance.

		If the owner already has a wallet in the database, the keys are
		retrieved from the database.

		Args:
			owner str: Name of the owner who owns the wallet. 
				This name must be unique.
			password str: Password to encrypt the private key before
				storing in the database. The user has to remember this
				password to decrypt the private key.

		Returns:
			:obj:`Wallet`
		"""
		# check if the owner is unique
		if not database.is_unique_name(owner):
			return Wallet.load_from_database(owner)

		if backend == None:
			backend = default_backend()

		# generate RSA key
		private_key = rsa.generate_private_key(
			public_exponent=public_exponent,
			key_size=key_size,
			backend=default_backend()
		)

		# encrypt private key with password
		# this will be stored in the database
		encrypted_private_key = private_key.private_bytes(
			encoding=serialization.Encoding.PEM,
			format=serialization.PrivateFormat.PKCS8,
			encryption_algorithm=serialization.BestAvailableEncryption(
				bytes(password))
			)

		public_bytes = private_key.public_key().public_bytes(
			encoding=serialization.Encoding.PEM,
			format=serialization.PublicFormat.SubjectPublicKeyInfo
			)

		# add it to the database
		database.add_wallet(owner, public_bytes, encrypted_private_key)

		return cls(owner, encrypted_private_key)

	@classmethod
	def load_from_database(cls, owner):
		""" Fetches the entry from the database and returns a wallet 
		instance.
	
		Args:
			owner str: Name of the owner who owns the wallet. 

		Returns:
			:obj:`Wallet`
		"""
		db_entry = database.get_wallet(owner)
		if not db_entry:
			return None
		return cls(db_entry[0], str(db_entry[2]))

	def __init__(self, owner, encrypted_private_key):
		self.__owner = owner
		self.__encrypted_private_key = encrypted_private_key
		self.__public_key = self._load_pem_public_key()

	@property
	def owner(self):
		return self.__owner

	@property
	def public_key(self):
		return self.__public_key

	def get_serialized_public_key(self):
		""" Serialize public key
		"""
		return self.__public_key.public_bytes(
			encoding=serialization.Encoding.PEM,
			format=serialization.PublicFormat.SubjectPublicKeyInfo
			)

	def get_serialized_private_key(self):
		""" serialize encrypted private key
		"""
		return self.__encrypted_private_key

	def _decrypt_private_key(self, password, backend=None):
		if backend == None:
			backend = default_backend()

		return serialization.load_pem_private_key(
			self.__encrypted_private_key,
			password=bytes(password),
			backend=default_backend())

	def _load_pem_public_key(self):
		db_entry = database.get_wallet(self.__owner)
		if not db_entry:
			return None
		return serialization.load_pem_public_key(
			str(db_entry[1]),
			backend=default_backend())
