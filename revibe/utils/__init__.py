
def getattr_or_get(obj, ref, default=None):
    if isinstance(obj, dict):
        return obj.get(ref, default)
    else:
        return getattr(obj, ref, default)