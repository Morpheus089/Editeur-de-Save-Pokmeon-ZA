"""
Configuration et données pour Pokemon Legends Z-A Save Editor

Basé sur les informations officielles de Pokemon Legends Z-A
"""

LUMIOSE_POKEDEX_COUNT = 232

MEGA_EVOLUTION_COUNT = 67

TOTAL_TM_COUNT = 107

NEW_MEGA_EVOLUTIONS = [
    "Mega Zeraora", "Mega Zoroark", "Mega Serperior", "Mega Emboar", 
    "Mega Samurott", "Mega Chesnaught", "Mega Delphox", "Mega Greninja"
]

ITEM_CATEGORIES = {
    0: {
        "name": "Aucune",
        "description": "Pas de catégorie définie",
        "color": "#808080"
    },
    1: {
        "name": "Poké Balls",
        "description": "Tous types de Poké Balls pour capturer les Pokémon",
        "color": "#808080"
    },
    2: {
        "name": "Médicaments",
        "description": "Objets de soin et potions",
        "color": "#808080"
    },
    3: {
        "name": "Baies",
        "description": "Baies diverses avec effets variés",
        "color": "#808080"
    },
    4: {
        "name": "CT/CS",
        "description": "Capacités Techniques et Capacités Secrètes",
        "color": "#808080"
    },
    5: {
        "name": "Objets",
        "description": "Objets divers et utilitaires",
        "color": "#808080"
    },
    6: {
        "name": "Méga-Pierres",
        "description": "Pierres nécessaires pour les méga-évolutions",
        "color": "#808080"
    },
    7: {
        "name": "Pierres d'évolution",
        "description": "Pierres pour faire évoluer les Pokémon",
        "color": "#808080"
    },
    8: {
        "name": "Objets de combat",
        "description": "Objets utilisables en combat",
        "color": "#808080"
    },
    9: {
        "name": "Objets précieux",
        "description": "Objets rares et précieux",
        "color": "#808080"
    }
}

PLZA_ITEM_PRESETS = {
    "mega_starter": {
        "name": "Pack Méga-Évolution Débutant",
        "description": "Méga-pierres pour commencer avec les mégas populaires",
        "items": [
            {"name": "Charizardite X", "quantity": 1},
            {"name": "Charizardite Y", "quantity": 1},
            {"name": "Venusaurite", "quantity": 1},
            {"name": "Blastoisinite", "quantity": 1},
            {"name": "Lucarionite", "quantity": 1},
            {"name": "Garchompite", "quantity": 1}
        ]
    },
    "competitive_setup": {
        "name": "Setup Compétitif",
        "description": "Objets essentiels pour le jeu compétitif",
        "items": [
            {"name": "Hyper Ball", "quantity": 99},
            {"name": "Master Ball", "quantity": 10},
            {"name": "Hyper Potion", "quantity": 50},
            {"name": "Total Soin", "quantity": 20},
            {"name": "PP Max", "quantity": 10}
        ]
    },
    "all_mega_stones": {
        "name": "Toutes les Méga-Pierres",
        "description": "Collection complète des 67 méga-pierres",
        "items": []
    },
    "all_tms": {
        "name": "Toutes les CT",
        "description": "Collection complète des 107 CT disponibles",
        "items": []
    },
    "lumiose_explorer": {
        "name": "Explorateur de Lumiose",
        "description": "Objets pour explorer efficacement Lumiose",
        "items": [
            {"name": "Super Ball", "quantity": 99},
            {"name": "Hyper Ball", "quantity": 50},
            {"name": "Potion", "quantity": 30},
            {"name": "Super Potion", "quantity": 20},
            {"name": "Antidote", "quantity": 10},
            {"name": "Anti-Para", "quantity": 10}
        ]
    }
}

UI_CONFIG = {
    "theme": {
        "primary_color": "#2196F3",
        "secondary_color": "#FFC107",
        "accent_color": "#FF5722",
        "background_color": "#f0f0f0",
        "text_color": "#333333"
    },
    "window": {
        "min_width": 1000,
        "min_height": 700,
        "default_width": 1200,
        "default_height": 800
    },
    "fonts": {
        "default": ("Segoe UI", 9),
        "heading": ("Segoe UI", 12, "bold"),
        "small": ("Segoe UI", 8)
    }
}

BACKUP_CONFIG = {
    "auto_backup": True,
    "backup_on_open": True,
    "backup_on_save": True,
    "max_backups": 10,
    "backup_extension": ".backup"
}

GAME_LIMITS = {
    "max_money": 999999,
    "max_item_quantity": 999,
    "max_player_name_length": 12,
    "max_pokemon_level": 100,
    "max_pokemon_in_party": 6,
    "max_pokemon_in_box": 30,
    "total_boxes": 32
}

HELP_MESSAGES = {
    "bag_editor": """
    Éditeur de Sac:
    - Double-cliquez sur un objet pour modifier sa quantité
    - Utilisez les filtres pour trouver rapidement des objets
    - Les objets avec quantité 0 sont automatiquement supprimés
    - Les méga-pierres ne peuvent avoir qu'une quantité de 1
    """,
    
    "player_editor": """
    Éditeur de Joueur:
    - Le nom du joueur est limité à 12 caractères
    - L'ID du joueur est généré automatiquement
    - Le méga-pouvoir affecte la puissance des méga-évolutions
    """,
    
    "tools": """
    Outils:
    - "Réparer le sac" corrige les catégories d'objets invalides
    - "Vérifier l'intégrité" valide le hash du fichier
    - Créez toujours une sauvegarde avant les modifications importantes
    """
}

MEGA_EVOLUTION_CONFIG = {
    "mega_power_system": True,
    "mega_power_affects_duration": True,
    "max_mega_power": 100.0,
    "mega_power_increment": 0.1,
    "sync_moves_available": True
}

LUMIOSE_AREAS = [
    "Centre-ville", "Quartier Nord", "Quartier Sud", "Quartier Est", 
    "Quartier Ouest", "Zone Industrielle", "Parc Central", "Port",
    "Gare", "Tour Prismatique", "Laboratoire", "Université"
]

FUTURE_FEATURES = {
    "pokemon_editor": {
        "enabled": False,
        "description": "Édition complète des Pokémon (stats, niveaux, capacités)"
    },
    "box_manager": {
        "enabled": False,
        "description": "Gestion des boîtes PC et organisation des Pokémon"
    },
    "mega_sync_editor": {
        "enabled": False,
        "description": "Édition des capacités de synchronisation méga"
    },
    "fashion_editor": {
        "enabled": False,
        "description": "Édition des vêtements et accessoires du joueur"
    }
}

def validate_item_quantity(quantity, item_name=""):
    """Valider la quantité d'un objet"""
    if not isinstance(quantity, int):
        return False, "La quantité doit être un nombre entier"
    
    if quantity < 0:
        return False, "La quantité ne peut pas être négative"
        
    if quantity > GAME_LIMITS["max_item_quantity"]:
        return False, f"La quantité maximale est {GAME_LIMITS['max_item_quantity']}"
    
    # Vérification spéciale pour les méga-pierres
    if "ite" in item_name.lower() and "mega" in item_name.lower():
        if quantity > 1:
            return False, "Les méga-pierres ne peuvent avoir qu'une quantité de 1"
    
    return True, ""

def validate_player_name(name):
    """Valider le nom du joueur"""
    if not isinstance(name, str):
        return False, "Le nom doit être une chaîne de caractères"
    
    if len(name) == 0:
        return False, "Le nom ne peut pas être vide"
        
    if len(name) > GAME_LIMITS["max_player_name_length"]:
        return False, f"Le nom ne peut pas dépasser {GAME_LIMITS['max_player_name_length']} caractères"
    
    import re
    if not re.match(r'^[a-zA-Z0-9 \-]+$', name):
        return False, "Le nom contient des caractères non autorisés"
    
    return True, ""

def validate_money(amount):
    """Valider le montant d'argent"""
    if not isinstance(amount, int):
        return False, "L'argent doit être un nombre entier"
    
    if amount < 0:
        return False, "L'argent ne peut pas être négatif"
        
    if amount > GAME_LIMITS["max_money"]:
        return False, f"Le montant maximum est {GAME_LIMITS['max_money']}"
    
    return True, ""

# Export des configurations principales
__all__ = [
    'LUMIOSE_POKEDEX_COUNT',
    'MEGA_EVOLUTION_COUNT', 
    'TOTAL_TM_COUNT',
    'NEW_MEGA_EVOLUTIONS',
    'ITEM_CATEGORIES',
    'PLZA_ITEM_PRESETS',
    'UI_CONFIG',
    'BACKUP_CONFIG',
    'GAME_LIMITS',
    'HELP_MESSAGES',
    'MEGA_EVOLUTION_CONFIG',
    'LUMIOSE_AREAS',
    'FUTURE_FEATURES',
    'validate_item_quantity',
    'validate_player_name',
    'validate_money'
]