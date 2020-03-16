"""
Created: 16 Mar. 2020
Author: Jordan Prechac
"""

# -----------------------------------------------------------------------------

def truncate_string(string, chars=50):
    if len(string) <= chars:
        return string
    
    return string[:chars] + "..."
