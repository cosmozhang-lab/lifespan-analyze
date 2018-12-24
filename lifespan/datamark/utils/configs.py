from configparser import SafeConfigParser

class MarkConfig:
    def __init__(self, filepath=None):
        if filepath is None:
            import os
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = os.path.join(BASE_DIR, "config.conf")
        cp = SafeConfigParser()
        cp.read(filepath)
        self.outdir = cp.get("mark", "outdir")
