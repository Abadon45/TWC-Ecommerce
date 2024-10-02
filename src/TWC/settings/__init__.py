from .base import *
import os

try:
    # Try to load the local settings if it exists
    from .local import *
    print("Loaded local settings")
except ImportError as e:
    # Fallback to production settings if local.py is not available
    print(f"Local settings not found: {e}")
    from .production import *
