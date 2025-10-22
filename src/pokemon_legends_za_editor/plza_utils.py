"""
Utilitaires pour l'éditeur de sauvegarde Pokemon Legends Z-A
"""

import json
import os

class PLZAUtils:
    """Utilitaires pour Pokemon Legends Z-A"""
    
    @staticmethod
    def get_category_mapping():
        """Obtenir le mapping des catégories d'objets"""
        return {
            0: "Aucune",
            1: "Poké Balls",
            2: "Médicaments",
            3: "Baies", 
            4: "TM",
            5: "Objets",
            6: "Autres"
        }
    
    @staticmethod
    def get_mega_stones():
        """Obtenir la liste des méga-pierres"""
        mega_stones = []
        # Ces données seraient remplies depuis la base de données d'objets
        return mega_stones
    
    @staticmethod
    def validate_item_id(item_id, item_database):
        """Valider qu'un ID d'objet existe"""
        return str(item_id) in item_database
    
    @staticmethod
    def get_evolution_items():
        """Obtenir la liste des objets d'évolution"""
        evolution_items = [
            "Fire Stone", "Water Stone", "Thunder Stone", "Leaf Stone",
            "Moon Stone", "Sun Stone", "Shiny Stone", "Dusk Stone",
            "Dawn Stone", "Ice Stone", "King's Rock", "Metal Coat",
            "Dragon Scale", "Up-Grade", "Dubious Disc", "Protector",
            "Electirizer", "Magmarizer", "Razor Claw", "Razor Fang",
            "Oval Stone", "Deep Sea Tooth", "Deep Sea Scale", "Prism Scale",
            "Reaper Cloth", "Whipped Dream", "Sachet"
        ]
        return evolution_items
    
    @staticmethod
    def export_bag_to_json(bag_save, item_database, filename):
        """Exporter le contenu du sac vers JSON"""
        items = []
        for i, entry in enumerate(bag_save.entries):
            if entry.quantity > 0:
                item_name = item_database.get(str(i), {}).get("english_ui_name", f"Objet Inconnu ({i})")
                items.append({
                    "id": i,
                    "name": item_name,
                    "quantity": entry.quantity,
                    "category": entry.category if hasattr(entry.category, 'value') else entry.category
                })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def import_bag_from_json(filename):
        """Importer le contenu du sac depuis JSON"""
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def create_item_preset(name, items):
        """Créer un preset d'objets"""
        preset = {
            "name": name,
            "items": items,
            "created": "2025-10-19"
        }
        
        preset_dir = "presets"
        if not os.path.exists(preset_dir):
            os.makedirs(preset_dir)
            
        filename = os.path.join(preset_dir, f"{name.lower().replace(' ', '_')}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(preset, f, indent=2, ensure_ascii=False)
        
        return filename
    
    @staticmethod
    def load_item_preset(filename):
        """Charger un preset d'objets"""
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def get_item_presets():
        """Obtenir la liste des presets disponibles"""
        presets = []
        preset_dir = "presets"
        if os.path.exists(preset_dir):
            for filename in os.listdir(preset_dir):
                if filename.endswith('.json'):
                    try:
                        preset = PLZAUtils.load_item_preset(os.path.join(preset_dir, filename))
                        presets.append({
                            "filename": filename,
                            "name": preset.get("name", filename),
                            "items_count": len(preset.get("items", []))
                        })
                    except:
                        pass
        return presets

class PLZAConstants:
    """Constants pour Pokemon Legends Z-A"""
    
    # Limites
    MAX_ITEM_QUANTITY = 999
    MAX_MONEY = 999999
    MAX_PLAYER_NAME_LENGTH = 12
    
    # Types de Pokémon
    POKEMON_TYPES = [
        "Normal", "Feu", "Eau", "Électrik", "Plante", "Glace",
        "Combat", "Poison", "Sol", "Vol", "Psy", "Insecte",
        "Roche", "Spectre", "Dragon", "Ténèbres", "Acier", "Fée"
    ]
    
    # Natures de Pokémon
    POKEMON_NATURES = [
        "Hardi", "Prudent", "Relax", "Brave", "Docile", "Malin",
        "Pudique", "Lâche", "Sérieux", "Jovial", "Naive", "Modeste",
        "Doux", "Discret", "Malpoli", "Calme", "Gentil", "Rigide",
        "Foufou", "Pressé", "Timide", "Enjoué", "Bizarre", "Solo",
        "Robuste"
    ]
    
    # Statistiques
    POKEMON_STATS = ["PV", "Attaque", "Défense", "Att. Spé", "Déf. Spé", "Vitesse"]

class PLZAPresets:
    """Presets prédéfinis pour Pokemon Legends Z-A"""
    
    @staticmethod
    def get_starter_items():
        """Obtenir les objets de démarrage recommandés"""
        return [
            {"id": 1, "quantity": 10},   # Master Ball
            {"id": 2, "quantity": 50},   # Ultra Ball
            {"id": 3, "quantity": 99},   # Great Ball
            {"id": 4, "quantity": 99},   # Poke Ball
            {"id": 17, "quantity": 50},  # Potion (exemple)
        ]
    
    @staticmethod
    def get_competitive_items():
        """Obtenir les objets pour le jeu compétitif"""
        return [
        ]
    
    @staticmethod
    def get_all_tms():
        """Obtenir toutes les CTs/CS"""
        return [
            # Ce serait rempli avec toutes les CTs/CS du jeu
        ]
    
    @staticmethod
    def get_evolution_stones():
        """Obtenir toutes les pierres d'évolution"""
        return [
        ]

class PLZAFileManager:
    """Gestionnaire de fichiers pour l'éditeur"""
    
    @staticmethod
    def create_backup_folder():
        """Créer le dossier de sauvegarde"""
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        return backup_dir
    
    @staticmethod
    def create_export_folder():
        """Créer le dossier d'export"""
        export_dir = "exports"
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        return export_dir
    
    @staticmethod
    def get_safe_filename(filename):
        """Obtenir un nom de fichier sécurisé"""
        import re
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return safe_name
    
    @staticmethod
    def get_timestamp():
        """Obtenir un timestamp pour les noms de fichiers"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")

# Presets par défaut
DEFAULT_PRESETS = {
    "starter_pack": {
        "name": "Pack de Démarrage",
        "description": "Objets essentiels pour commencer l'aventure",
        "items": PLZAPresets.get_starter_items()
    },
    "competitive": {
        "name": "Pack Compétitif", 
        "description": "Objets pour le jeu compétitif",
        "items": PLZAPresets.get_competitive_items()
    }
}

def create_default_presets():
    """Créer les presets par défaut"""
    PLZAFileManager.create_backup_folder()
    preset_dir = "presets"
    if not os.path.exists(preset_dir):
        os.makedirs(preset_dir)
    
    for preset_id, preset_data in DEFAULT_PRESETS.items():
        filename = os.path.join(preset_dir, f"{preset_id}.json")
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(preset_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    create_default_presets()
    print("Presets par défaut créés!")