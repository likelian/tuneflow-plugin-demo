# debug.py

from plugin import MDX
from tuneflow_devkit import Debugger

if __name__ == "__main__":
    Debugger(plugin_class=MDX, bundle_file_path="bundle.json").start()
