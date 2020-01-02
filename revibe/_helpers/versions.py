class Version:
    """
    every time there is a new API verion, increment the version dict and add the new string
    """
    all_versions = {
        1: 'v1'
    }

    def __init__(self, *args, **kwargs):
        m = max(self.all_versions.keys())
        self.latest = self.all_versions[m]