import base64

# Cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

# Local imports
from . import database
from ..logger import LOG

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
            LOG.info("Found an existing wallet with this name. So returning it.")
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
        LOG.debug("A new wallet is generated and added to the database.")

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
            LOG.error("Wallet not found. Please generate one.")
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
        """ Returns serialized public key
        """
        return self.__public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

    def get_serialized_private_key(self):
        """ Returns serialized encrypted private key
        """
        return self.__encrypted_private_key

    def sign(self, message, password):
        """Private key is used to sign a message.
        This allows anyone with the public key to verify that the
        message was created by someone who possesses the corresponding
        private key.

        Args:
            message str: Message to be signed
            password str: Password to decrypt the private key

        Returns:
            str : signature
        """
        pvt_key = self._decrypt_private_key(password)
        if pvt_key == None:
            return None

        signature = pvt_key.sign(message,
            padding.PSS( mgf=padding.MGF1( hashes.SHA256() ),
                        salt_length=padding.PSS.MAX_LENGTH ),
            hashes.SHA256()
            )

        return base64.b64encode(signature)

    def verify(self, message, signature):
        """Public key is used to verify if the signature
        was generated using the associated private key.

        Args:
            message str: Message to be verified.
            signature str: Signature generated using sender's private key.

        Returns:
            bool : True if verification passed.
        """

        try:
            decoded_signature = base64.b64decode(signature)

            self.public_key.verify(decoded_signature, message,
                padding.PSS( mgf=padding.MGF1( hashes.SHA256() ),
                             salt_length=padding.PSS.MAX_LENGTH ),
                hashes.SHA256()
                )
        except InvalidSignature:
            LOG.error("Verification failed. Invalid Signature.")
            return False

        LOG.info("Verification successful!")
        return True

    ##########################################################################
    #
    # Internal helper methods
    #
    ##########################################################################
    def _decrypt_private_key(self, password, backend=None):
        if backend == None:
            backend = default_backend()

        private_key = None

        try:
            private_key = serialization.load_pem_private_key(
                self.__encrypted_private_key,
                password=bytes(password),
                backend=default_backend())
        except ValueError:
            LOG.error("Failed to decrypt the private key. Please check the password.")
            pass

        return private_key

    def _load_pem_public_key(self):
        db_entry = database.get_wallet(self.__owner)
        if not db_entry:
            LOG.error("Wallet not found. Please generate one.")
            return None
        return serialization.load_pem_public_key(
            str(db_entry[1]),
            backend=default_backend())


##############################################################################
#
# Helpers
#
##############################################################################
def generate_wallet(name, password):
    return Wallet.generate(name, password)
