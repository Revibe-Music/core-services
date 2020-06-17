"""
Created: 17 June 2020
"""

# -----------------------------------------------------------------------------

def generate_canonical_identifier(platform, obj_type, id):
    return f"{platform}:{obj_type}:{id}"
