"""
Created: 20 Mar. 2020
Author: Jordan Prechac
"""

# -----------------------------------------------------------------------------

def default_repr(self):
    return f"<{self.__class__.__name__} ({self.__str__()})>"
