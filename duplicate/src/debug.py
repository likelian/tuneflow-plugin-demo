# debug.py

from plugin import Duplicate
from tuneflow_devkit import Debugger

if __name__ == "__main__":
    Debugger(plugin_class=Duplicate, bundle_file_path="bundle.json").start()
