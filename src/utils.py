import os
import hashlib
from datetime import datetime

def get_timestamp():
    """Get the current date and time.
    """
    return "{:%d %b %Y %H:%M:%S}".format(datetime.now())

def hexdigest(message):
    return hashlib.sha256(message).hexdigest()

##############################################################################
#
# OS PATH UTILS
#
##############################################################################
def get_dir_path():
    """Get the current dir path
    """
    return os.path.abspath(os.path.dirname(__file__))

def get_module_path():
    """Get the module path
    """
    dir_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.dirname(dir_path)

def get_resources_dir():
    """Get the resources dir. This is where the db file
    is located.
    """
    resource_dir = os.path.join(get_module_path(), "resources")
    if not os.path.exists(resource_dir):
        os.makedirs(resource_dir)
    return resource_dir