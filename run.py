"""
Point d'entrée principal pour Pokemon Legends Z-A Save Editor
"""

import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from pokemon_legends_za_editor.main import main

if __name__ == "__main__":
    main()