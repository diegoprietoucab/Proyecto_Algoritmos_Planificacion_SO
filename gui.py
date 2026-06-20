import sys
import os

# Ensure the project root is always in sys.path and the CWD
_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT)
os.chdir(_ROOT)

from UI.gui.app import MainApp

if __name__ == '__main__':
    app = MainApp()
    app.mainloop()
