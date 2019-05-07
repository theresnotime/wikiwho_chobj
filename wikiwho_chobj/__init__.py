import pkg_resources
name = "wikiwho_chobj"
try:
    __version__ = pkg_resources.require(name)[0].version
except:
    __version__ = None


from .chobj import Chobjer
from . import utils