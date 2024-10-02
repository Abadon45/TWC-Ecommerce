from .base import *
import os

try:
    # Try to load the local settings if it exists
    from .local import *
    print("Loaded local settings")
except ImportError:
    # Fallback to production settings if local.py is not available
    from .production import *
    print("Loaded production settings")
