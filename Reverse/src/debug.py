# debug.py

from plugin import Reverse
from tuneflow_devkit import Debugger

if __name__ == "__main__":
    Debugger(plugin_class=Reverse, bundle_file_path="bundle.json").start()
