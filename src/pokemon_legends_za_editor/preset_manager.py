"""
Gestionnaire de Presets pour Pokemon Legends Z-A Save Editor
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class PresetManager:
    """Gestionnaire des presets d'objets"""
    
    def __init__(self, preset_dir="presets"):
        self.preset_dir = preset_dir
        self.ensure_preset_dir()
        self.create_default_presets()
    
    def ensure_preset_dir(self):
        """S'assurer que le répertoire des presets existe"""
        if not os.path.exists(self.preset_dir):
            os.makedirs(self.preset_dir)
    
    def create_default_presets(self):
        """Créer les presets par défaut"""
        default_presets = {
            "starter_pack": {
                "name": "Pack de Démarrage",
                "description": "Objets essentiels pour commencer l'aventure dans Lumiose",
                "author": "MiniMax Agent",
                "created": "2025-10-19",
                "items": [
                    {"id": 1, "name": "Master Ball", "quantity": 5},
                    {"id": 2, "name": "Ultra Ball", "quantity": 30},
                    {"id": 3, "name": "Great Ball", "quantity": 50},
                    {"id": 4, "name": "Poké Ball", "quantity": 99},
                    {"id": 17, "name": "Potion", "quantity": 20},
                    {"id": 18, "name": "Super Potion", "quantity": 15},
                    {"id": 19, "name": "Hyper Potion", "quantity": 10},
                    {"id": 20, "name": "Potion Max", "quantity": 5}
                ]
            },
            
            "mega_collection": {
                "name": "Collection Méga-Évolution",
                "description": "Toutes les méga-pierres principales pour débuter avec les mégas",
                "author": "MiniMax Agent", 
                "created": "2025-10-19",
                "items": [
                    # Méga-pierres des starters de Kalos
                    {"id": 658, "name": "Charizardite X", "quantity": 1},
                    {"id": 659, "name": "Charizardite Y", "quantity": 1},
                    {"id": 660, "name": "Venusaurite", "quantity": 1},
                    {"id": 661, "name": "Blastoisinite", "quantity": 1},
                    
                    # Mégas populaires
                    {"id": 662, "name": "Lucarionite", "quantity": 1},
                    {"id": 663, "name": "Garchompite", "quantity": 1},
                    {"id": 664, "name": "Méwtwoïte X", "quantity": 1},
                    {"id": 665, "name": "Méwtwoïte Y", "quantity": 1},
                    {"id": 666, "name": "Rayquazite", "quantity": 1},
                    
                    # Nouvelles mégas de Z-A
                    {"id": 700, "name": "Zeroarite", "quantity": 1},
                    {"id": 701, "name": "Zoroarkite", "quantity": 1},
                    {"id": 702, "name": "Serperiorite", "quantity": 1},
                    {"id": 703, "name": "Emboarite", "quantity": 1}
                ]
            },
            
            "competitive_setup": {
                "name": "Setup Compétitif",
                "description": "Objets essentiels pour le jeu compétitif et les combats sérieux",
                "author": "MiniMax Agent",
                "created": "2025-10-19", 
                "items": [
                    # Pokéballs de qualité
                    {"id": 1, "name": "Master Ball", "quantity": 10},
                    {"id": 2, "name": "Ultra Ball", "quantity": 99},
                    {"id": 12, "name": "Premier Ball", "quantity": 50},
                    
                    # Soins
                    {"id": 19, "name": "Hyper Potion", "quantity": 50},
                    {"id": 20, "name": "Potion Max", "quantity": 30},
                    {"id": 21, "name": "Total Soin", "quantity": 20},
                    {"id": 22, "name": "Rappel", "quantity": 10},
                    {"id": 23, "name": "Rappel Max", "quantity": 5},
                    
                    # Objets de combat
                    {"id": 50, "name": "Poké Poupée", "quantity": 10},
                    {"id": 51, "name": "Fluide Fuite", "quantity": 10},
                    
                    # PP et stats
                    {"id": 60, "name": "Huile", "quantity": 10},
                    {"id": 61, "name": "Huile Max", "quantity": 5},
                    {"id": 62, "name": "PP Plus", "quantity": 10},
                    {"id": 63, "name": "PP Max", "quantity": 5}
                ]
            },
            
            "tm_collection": {
                "name": "Collection CT Essentielle", 
                "description": "Les CT les plus utiles pour l'entraînement",
                "author": "MiniMax Agent",
                "created": "2025-10-19",
                "items": [
                    # CT de base populaires (IDs approximatifs)
                    {"id": 328, "name": "CT001 Charge", "quantity": 1},
                    {"id": 329, "name": "CT002 Griffe Dragon", "quantity": 1},
                    {"id": 330, "name": "CT003 Psykoud'Boul", "quantity": 1},
                    {"id": 331, "name": "CT004 Roulade", "quantity": 1},
                    {"id": 332, "name": "CT005 Boue-Bombe", "quantity": 1},
                    {"id": 350, "name": "CT025 Façade", "quantity": 1},
                    {"id": 360, "name": "CT035 Repos", "quantity": 1},
                    {"id": 380, "name": "CT055 Ébullition", "quantity": 1},
                    {"id": 400, "name": "CT075 Danse-Lames", "quantity": 1},
                    {"id": 420, "name": "CT095 Telluriforce", "quantity": 1}
                ]
            },
            
            "lumiose_explorer": {
                "name": "Explorateur de Lumiose",
                "description": "Tout ce qu'il faut pour explorer efficacement la région de Lumiose",
                "author": "MiniMax Agent",
                "created": "2025-10-19",
                "items": [
                    # Capture variée
                    {"id": 2, "name": "Ultra Ball", "quantity": 50},
                    {"id": 3, "name": "Great Ball", "quantity": 99},
                    {"id": 4, "name": "Poké Ball", "quantity": 99},
                    {"id": 6, "name": "Filet Ball", "quantity": 30},
                    {"id": 7, "name": "Scuba Ball", "quantity": 20},
                    {"id": 8, "name": "Faiblo Ball", "quantity": 30},
                    {"id": 10, "name": "Chrono Ball", "quantity": 30},
                    {"id": 13, "name": "Sombre Ball", "quantity": 30},
                    {"id": 15, "name": "Rapide Ball", "quantity": 30},
                    
                    # Soins complets
                    {"id": 17, "name": "Potion", "quantity": 30},
                    {"id": 18, "name": "Super Potion", "quantity": 25},
                    {"id": 19, "name": "Hyper Potion", "quantity": 20},
                    {"id": 24, "name": "Antidote", "quantity": 15},
                    {"id": 25, "name": "Anti-Para", "quantity": 15},
                    {"id": 26, "name": "Anti-Brûle", "quantity": 15},
                    {"id": 27, "name": "Anti-Gel", "quantity": 15},
                    {"id": 28, "name": "Réveil", "quantity": 15},
                    
                    # Utilitaires d'exploration
                    {"id": 80, "name": "Corde Sortie", "quantity": 10},
                    {"id": 81, "name": "Repousse", "quantity": 20},
                    {"id": 82, "name": "Super Repousse", "quantity": 15},
                    {"id": 83, "name": "Max Repousse", "quantity": 10}
                ]
            },
            
            "berry_garden": {
                "name": "Jardin de Baies",
                "description": "Collection de baies utiles pour les soins et effets spéciaux",
                "author": "MiniMax Agent",
                "created": "2025-10-19", 
                "items": [
                    # Baies de soin de base
                    {"id": 149, "name": "Baie Oran", "quantity": 50},
                    {"id": 150, "name": "Baie Pêcha", "quantity": 30},
                    {"id": 151, "name": "Baie Fraive", "quantity": 30},
                    {"id": 152, "name": "Baie Willia", "quantity": 30},
                    {"id": 153, "name": "Baie Mépo", "quantity": 30},
                    {"id": 154, "name": "Baie Résin", "quantity": 30},
                    
                    # Baies spéciales
                    {"id": 155, "name": "Baie Sitrus", "quantity": 20},
                    {"id": 156, "name": "Baie Figuy", "quantity": 15},
                    {"id": 157, "name": "Baie Wiki", "quantity": 15},
                    {"id": 158, "name": "Baie Mago", "quantity": 15},
                    {"id": 159, "name": "Baie Gowav", "quantity": 15},
                    {"id": 160, "name": "Baie Papaya", "quantity": 15},
                    
                    # Baies rares
                    {"id": 168, "name": "Baie Enigma", "quantity": 5},
                    {"id": 169, "name": "Baie Micle", "quantity": 5},
                    {"id": 170, "name": "Baie Selve", "quantity": 5}
                ]
            }
        }
        
        # Créer les fichiers de presets s'ils n'existent pas
        for preset_id, preset_data in default_presets.items():
            filename = os.path.join(self.preset_dir, f"{preset_id}.json")
            if not os.path.exists(filename):
                self.save_preset(preset_data, filename)
    
    def save_preset(self, preset_data: Dict[str, Any], filename: str = None):
        """Sauvegarder un preset"""
        if filename is None:
            preset_name = preset_data.get("name", "preset").lower().replace(" ", "_")
            filename = os.path.join(self.preset_dir, f"{preset_name}.json")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(preset_data, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def load_preset(self, filename: str) -> Dict[str, Any]:
        """Charger un preset"""
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_presets(self) -> List[Dict[str, Any]]:
        """Lister tous les presets disponibles"""
        presets = []
        
        if not os.path.exists(self.preset_dir):
            return presets
        
        for filename in os.listdir(self.preset_dir):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(self.preset_dir, filename)
                    preset = self.load_preset(filepath)
                    presets.append({
                        "filename": filename,
                        "filepath": filepath,
                        "name": preset.get("name", filename),
                        "description": preset.get("description", "Aucune description"),
                        "author": preset.get("author", "Inconnu"),
                        "created": preset.get("created", "Date inconnue"),
                        "items_count": len(preset.get("items", []))
                    })
                except Exception as e:
                    print(f"Erreur lors du chargement de {filename}: {e}")
        
        return sorted(presets, key=lambda x: x["name"])
    
    def create_custom_preset(self, name: str, description: str, items: List[Dict[str, Any]], author: str = "Utilisateur"):
        """Créer un preset personnalisé"""
        preset_data = {
            "name": name,
            "description": description,
            "author": author,
            "created": datetime.now().strftime("%Y-%m-%d"),
            "items": items
        }
        
        filename = self.save_preset(preset_data)
        return filename
    
    def delete_preset(self, filename: str) -> bool:
        """Supprimer un preset"""
        filepath = os.path.join(self.preset_dir, filename)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception as e:
            print(f"Erreur lors de la suppression de {filename}: {e}")
        return False
    
    def export_bag_to_preset(self, bag_items: List[Dict[str, Any]], name: str, description: str = ""):
        """Exporter le contenu du sac vers un nouveau preset"""
        return self.create_custom_preset(name, description, bag_items)
    
    def get_preset_categories(self) -> Dict[str, List[str]]:
        """Obtenir les catégories de presets"""
        categories = {
            "Démarrage": ["starter_pack.json"],
            "Combat": ["competitive_setup.json", "mega_collection.json"],
            "Exploration": ["lumiose_explorer.json"],
            "Collection": ["tm_collection.json", "berry_garden.json"],
            "Personnalisé": []
        }
        
        all_presets = self.list_presets()
        default_files = [item for sublist in categories.values() for item in sublist]
        
        for preset in all_presets:
            if preset["filename"] not in default_files:
                categories["Personnalisé"].append(preset["filename"])
        
        return categories

def create_sample_presets():
    """Créer des presets d'exemple pour la démonstration"""
    manager = PresetManager()
    
    print("Gestionnaire de Presets initialisé!")
    print(f"Presets créés dans le dossier: {manager.preset_dir}")
    
    # Lister les presets disponibles
    presets = manager.list_presets()
    print(f"\nPresets disponibles ({len(presets)}):")
    for preset in presets:
        print(f"  • {preset['name']} - {preset['items_count']} objets")
        print(f"    {preset['description']}")
        print(f"    Auteur: {preset['author']} | Créé: {preset['created']}")
        print()

if __name__ == "__main__":
    create_sample_presets()