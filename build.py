import subprocess
import sys
import os
import shutil

def build_exe():
    print("="*60)
    print("Pokemon Legends Z-A Editor - Compilation")
    print("="*60)
    
    if os.path.exists("dist"):
        print("Nettoyage du dossier dist...")
        shutil.rmtree("dist")
    
    if os.path.exists("build"):
        print("Nettoyage du dossier build...")
        shutil.rmtree("build")
    
    print("\nDebut de la compilation avec PyInstaller...")
    print("-" * 60)
    
    cmd = [sys.executable, "-m", "PyInstaller", "pokemon_legends_za_editor.spec", "--clean", "-y"]
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print("\n" + "="*60)
        print("COMPILATION REUSSIE!")
        print("="*60)
        print("\nL'executable se trouve dans le dossier 'dist/'")
        print("Fichier: dist/Pokemon_Legends_ZA_Save_Editor.exe")
        return True
    else:
        print("\n" + "="*60)
        print("ERREUR DE COMPILATION")
        print("="*60)
        return False

if __name__ == "__main__":
    success = build_exe()
    if not success:
        sys.exit(1)
