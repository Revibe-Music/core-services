"""
Created: 02 June 2020
Author: Jordan Prechac
"""

import os

# -----------------------------------------------------------------------------

def custom_file_upload(instance, filename):
    root_path = os.path.join("images", instance.__class__.__name__)

    path = os.path.join(root_path, filename)

    return path
