"""
Pokemon Legends Z-A Save Editor avec Onglet Pokédex
Un éditeur de sauvegarde complet avec interface graphique pour Pokemon Legends Z-A

Fonctionnalités:
- Édition des objets du sac
- Modification des données du joueur
- Gestion du Pokédex (Nouvel onglet)
- Interface graphique intuitive
- Sauvegarde sécurisée
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
import sys
import threading
from typing import Dict, Any, Optional
import shutil

plaza_path = os.path.join(os.path.dirname(__file__), "..")
if plaza_path not in sys.path:
    sys.path.insert(0, plaza_path)

try:
    from plaza.crypto import HashDB, SwishCrypto
    from plaza.types import BagEntry, BagSave, CategoryType, CoreData, PokedexSaveDataAccessor, PokedexCoreData
    from plaza.types.accessors import HashDBKeys
    from plaza.util.items import item_db
except ImportError as e:
    print(f"Erreur d'importation de la bibliothèque plaza: {e}")
    sys.exit(1)

SAVE_FILE_MAGIC = bytes([0x17, 0x2D, 0xBB, 0x06, 0xEA])

# Base de données des Pokémon (réduite pour l'exemple)
POKEMON_DATA = {
    1: "Bulbasaur", 2: "Ivysaur", 3: "Venusaur", 4: "Charmander", 5: "Charmeleon",
    6: "Charizard", 7: "Squirtle", 8: "Wartortle", 9: "Blastoise", 13: "Weedle",
    14: "Kakuna", 15: "Beedrill", 16: "Pidgey", 17: "Pidgeotto", 18: "Pidgeot",
    23: "Ekans", 24: "Arbok", 25: "Pikachu", 26: "Raichu", 35: "Clefairy", 36: "Clefable",
    63: "Abra", 64: "Kadabra", 65: "Alakazam", 66: "Machop", 67: "Machoke", 68: "Machamp",
    69: "Bellsprout", 70: "Weepinbell", 71: "Victreebel", 79: "Slowpoke", 80: "Slowbro",
    92: "Gastly", 93: "Haunter", 94: "Gengar", 95: "Onix", 115: "Kangaskhan",
    120: "Staryu", 121: "Starmie", 123: "Scyther", 127: "Pinsir", 129: "Magikarp",
    130: "Gyarados", 133: "Eevee", 134: "Vaporeon", 135: "Jolteon", 136: "Flareon",
    142: "Aerodactyl", 147: "Dratini", 148: "Dragonair", 149: "Dragonite", 150: "Mewtwo",
    152: "Chikorita", 153: "Bayleef", 154: "Meganium", 158: "Totodile", 159: "Croconaw",
    160: "Feraligatr", 167: "Spinarak", 168: "Ariados", 172: "Pichu", 173: "Cleffa",
    179: "Mareep", 180: "Flaaffy", 181: "Ampharos", 196: "Espeon", 197: "Umbreon",
    199: "Slowking", 208: "Steelix", 212: "Scizor", 214: "Heracross", 225: "Delibird",
    227: "Skarmory", 228: "Houndour", 229: "Houndoom", 246: "Larvitar", 247: "Pupitar",
    248: "Tyranitar", 280: "Ralts", 281: "Kirlia", 282: "Gardevoir", 302: "Sableye",
    303: "Mawile", 304: "Aron", 305: "Lairon", 306: "Aggron", 307: "Meditite",
    308: "Medicham", 309: "Electrike", 310: "Manectric", 315: "Roselia", 318: "Carvanha",
    319: "Sharpedo", 322: "Numel", 323: "Camerupt", 333: "Swablu", 334: "Altaria",
    353: "Shuppet", 354: "Banette", 359: "Absol", 361: "Snorunt", 362: "Glalie",
    371: "Bagon", 372: "Shelgon", 373: "Salamence", 374: "Beldum", 375: "Metang",
    376: "Metagross", 406: "Budew", 407: "Roserade", 427: "Buneary", 428: "Lopunny",
    443: "Gible", 444: "Gabite", 445: "Garchomp", 447: "Riolu", 448: "Lucario",
    449: "Hippopotas", 450: "Hippowdon", 459: "Snover", 460: "Abomasnow", 470: "Leafeon",
    471: "Glaceon", 475: "Gallade", 478: "Froslass", 498: "Tepig", 499: "Pignite",
    500: "Emboar", 504: "Patrat", 505: "Watchog", 511: "Pansage", 512: "Simisage",
    513: "Pansear", 514: "Simisear", 515: "Panpour", 516: "Simipour", 529: "Drilbur",
    530: "Excadrill", 531: "Audino", 543: "Venipede", 544: "Whirlipede", 545: "Scolipede",
    551: "Sandile", 552: "Krokorok", 553: "Krookodile", 559: "Scraggy", 560: "Scrafty",
    568: "Trubbish", 569: "Garbodor", 582: "Vanillite", 583: "Vanillish", 584: "Vanilluxe",
    587: "Emolga", 602: "Tynamo", 603: "Eelektrik", 604: "Eelektross", 607: "Litwick",
    608: "Lampent", 609: "Chandelure", 618: "Stunfisk", 650: "Chespin", 651: "Quilladin",
    652: "Chesnaught", 653: "Fennekin", 654: "Braixen", 655: "Delphox", 656: "Froakie",
    657: "Frogadier", 658: "Greninja", 659: "Bunnelby", 660: "Diggersby", 661: "Fletchling",
    662: "Fletchinder", 663: "Talonflame", 664: "Scatterbug", 665: "Spewpa", 666: "Vivillon",
    667: "Litleo", 668: "Pyroar", 669: "Flabébé", 670: "Floette", 671: "Florges",
    672: "Skiddo", 673: "Gogoat", 674: "Pancham", 675: "Pangoro", 676: "Furfrou",
    677: "Espurr", 678: "Meowstic", 679: "Honedge", 680: "Doublade", 681: "Aegislash",
    682: "Spritzee", 683: "Aromatisse", 684: "Swirlix", 685: "Slurpuff", 686: "Inkay",
    687: "Malamar", 688: "Binacle", 689: "Barbaracle", 690: "Skrelp", 691: "Dragalge",
    692: "Clauncher", 693: "Clawitzer", 694: "Helioptile", 695: "Heliolisk", 696: "Tyrunt",
    697: "Tyrantrum", 698: "Amaura", 699: "Aurorus", 700: "Sylveon", 701: "Hawlucha",
    702: "Dedenne", 703: "Carbink", 704: "Goomy", 705: "Sliggoo", 706: "Goodra",
    707: "Klefki", 708: "Phantump", 709: "Trevenant", 710: "Pumpkaboo", 711: "Gourgeist",
    712: "Bergmite", 713: "Avalugg", 714: "Noibat", 715: "Noivern", 716: "Xerneas",
    717: "Yveltal", 718: "Zygarde", 719: "Diancie", 720: "Hoopa", 721: "Volcanion",
    780: "Drampa", 870: "Falinks"
}

POKEMON_IDS = sorted(POKEMON_DATA.keys())

class PLZASaveEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokemon Legends Z-A Save Editor - Interface Graphique Simple")
        self.root.geometry("1200x800")
        self.root.configure(bg="#34495e")
        
        self.save_data = None
        self.hash_db = None
        self.bag_save = None
        self.core_data = None
        self.pokedex_accessor = None
        self.save_file_path = None
        self.is_modified = False
        
        self.item_database = item_db
        
        # Variables pour le Pokédex
        self.pokemon_vars = {}
        self.selected_file = None
        
        # Variables pour la pagination
        self.pokemon_current_page = 0
        self.pokemon_items_per_page = 25
        self.pokemon_total_pages = (len(POKEMON_IDS) + self.pokemon_items_per_page - 1) // self.pokemon_items_per_page
        
        self.create_widgets()
        self.update_status("Prêt - Chargez un fichier de sauvegarde pour commencer")
        
    def get_best_font(self, size=9, style="normal"):
        """Sélectionne la meilleure police disponible pour les caractères français"""
        try:
            import tkinter.font as tkFont
            
            # Liste des polices dans l'ordre de préférence pour les caractères français
            preferred_fonts = [
                # Polices système modernes
                "Segoe UI", "Segoe UI Emoji", "Segoe UI Symbol",
                # Polices Ubuntu/Linux
                "Ubuntu", "Ubuntu Mono", "DejaVu Sans", "DejaVu Sans Mono",
                # Polices Windows
                "Arial Unicode MS", "Lucida Sans Unicode",
                # Polices macOS
                "SF Pro Text", "Helvetica Neue", "Apple Color Emoji",
                # Polices standards
                "Arial", "Helvetica", "Tahoma", "Verdana", "Trebuchet MS",
                # Polices système génériques
                "system-ui", "sans-serif", "Sans"
            ]
            
            # Vérifier quelles polices sont disponibles
            available_fonts = list(tkFont.families())
            
            # Trouver la première police disponible
            for font_name in preferred_fonts:
                if font_name in available_fonts:
                    return (font_name, size, style)
            
            # Si aucune police préférée n'est trouvée, utiliser une police système par défaut
            return ("system-ui", size, style)
            
        except Exception as e:
            print(f"Erreur lors de la sélection de police: {e}")
            return ("Arial", size, style)  # Fallback sur Arial
    
    def setup_ttk_styles(self):
        """Configuration des styles ttk personnalisés avec polices compatibles"""
        try:
            # Configuration des styles pour les boutons
            style = ttk.Style()
            
            # Sélectionner la meilleure police pour les boutons
            button_font = self.get_best_font(9, "bold")
            label_font = self.get_best_font(9)
            
            # Style pour les boutons d'action (bleu)
            style.configure("Accent.TButton", 
                           foreground="black", 
                           background="#2980b9",
                           borderwidth=2,
                           relief="raised",
                           font=button_font)
            
            # Style pour les boutons de succès (vert)
            style.configure("Success.TButton", 
                           foreground="black", 
                           background="#27ae60",
                           borderwidth=2,
                           relief="raised",
                           font=button_font)
            
            # Style pour les boutons standard (gris)
            style.configure("TButton",
                           borderwidth=2,
                           relief="raised",
                           font=button_font)
            
            # Style pour les checkboxes (texte blanc)
            style.configure("TCheckbutton",
                           font=label_font,
                           foreground="white",
                           background=self.root.cget("bg"))
            
            # Style pour les labels (texte blanc)
            style.configure("TLabel",
                           font=label_font,
                           foreground="white",
                           background=self.root.cget("bg"))
            
            # Style pour les frames
            style.configure("TFrame",
                           background=self.root.cget("bg"))
            
            # Style pour l'onglet notebook
            style.configure("TNotebook", 
                           background=self.root.cget("bg"),
                           borderwidth=0)
            
            style.configure("TNotebook.Tab",
                           foreground="black",
                           background="#7f8c8d",
                           padding=[10, 5],
                           font=label_font)
            
        except Exception as e:
            print(f"Erreur lors de la configuration des styles ttk: {e}")
            # Continuer sans styles personnalisés si erreur
            pass
        
    def create_widgets(self):
        """Créer l'interface utilisateur principale"""
        # Configuration des styles ttk
        self.setup_ttk_styles()
        
        # Barre de menu
        self.create_menu()
        
        # Frame principal avec onglets
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Onglet Informations du joueur
        self.player_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.player_frame, text="Joueur")
        self.create_player_tab()
        
        # Onglet Sac (Objets)
        self.bag_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.bag_frame, text="Sac")
        self.create_bag_tab()
        
        # Nouvel Onglet Pokédex
        self.pokedex_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pokedex_frame, text="Pokédex")
        self.create_pokedex_tab()
        
        # Onglet Pokémon
        self.pokemon_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pokemon_frame, text="Pokémon")
        self.create_pokemon_tab()
        
        # Onglet Outils
        self.tools_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tools_frame, text="Outils")
        self.create_tools_tab()
        
        # Barre de statut
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_menu(self):
        """Créer la barre de menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Ouvrir", command=self.open_save_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Sauvegarder", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Sauvegarder sous...", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Créer sauvegarde", command=self.create_backup)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.quit_app)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Édition", menu=edit_menu)
        edit_menu.add_command(label="Réinitialiser le sac", command=self.reset_bag)
        edit_menu.add_command(label="Ajouter tous les objets", command=self.add_all_items)
        edit_menu.add_command(label="Maximiser l'argent", command=self.max_money)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self.show_about)
        
        self.root.bind('<Control-o>', lambda e: self.open_save_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        
    def create_player_tab(self):
        """Créer l'onglet des informations du joueur"""
        main_frame = ttk.Frame(self.player_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Informations de base
        info_frame = ttk.LabelFrame(main_frame, text="Informations du joueur")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Nom du joueur
        ttk.Label(info_frame, text="Nom:", font=self.get_best_font(9)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.player_name_var = tk.StringVar()
        self.player_name_entry = ttk.Entry(info_frame, textvariable=self.player_name_var, width=30, font=self.get_best_font(9))
        self.player_name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.player_name_entry.bind('<KeyRelease>', self.on_player_data_changed)
        
        # Genre
        ttk.Label(info_frame, text="Genre:", font=self.get_best_font(9)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.gender_var = tk.StringVar()
        self.gender_combo = ttk.Combobox(info_frame, textvariable=self.gender_var, 
                                        values=["Masculin", "Féminin"], state="readonly", font=self.get_best_font(9))
        self.gender_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.gender_combo.bind('<<ComboboxSelected>>', self.on_player_data_changed)
        
        # ID du joueur
        ttk.Label(info_frame, text="ID:", font=self.get_best_font(9)).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.player_id_var = tk.StringVar()
        self.player_id_label = ttk.Label(info_frame, textvariable=self.player_id_var, font=self.get_best_font(9))
        self.player_id_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Statistiques de jeu
        stats_frame = ttk.LabelFrame(main_frame, text="Statistiques")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Argent
        ttk.Label(stats_frame, text="Argent:", font=self.get_best_font(9)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.money_var = tk.StringVar()
        self.money_entry = ttk.Entry(stats_frame, textvariable=self.money_var, width=15, font=self.get_best_font(9))
        self.money_entry.grid(row=0, column=1, padx=5, pady=5)
        self.money_entry.bind('<KeyRelease>', self.on_player_data_changed)
        
        # Bouton pour maximiser l'argent
        ttk.Button(stats_frame, text="Max", command=self.max_money, style="TButton").grid(row=0, column=2, padx=5, pady=5)
        
        # Poussière stellaire (si applicable)
        ttk.Label(stats_frame, text="Méga Pouvoir:", font=self.get_best_font(9)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.mega_power_var = tk.StringVar()
        self.mega_power_entry = ttk.Entry(stats_frame, textvariable=self.mega_power_var, width=15, font=self.get_best_font(9))
        self.mega_power_entry.grid(row=1, column=1, padx=5, pady=5)
        self.mega_power_entry.bind('<KeyRelease>', self.on_player_data_changed)
        
    def create_bag_tab(self):
        """Créer l'onglet du sac"""
        main_frame = ttk.Frame(self.bag_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(control_frame, text="Catégorie:", font=self.get_best_font(9)).pack(side=tk.LEFT, padx=(0, 5))
        self.category_filter = ttk.Combobox(control_frame, values=["Toutes", "Médicaments", "Poké Balls", "Autres", "Pickup", "Objets Clés", "Baies", "CT", "Méga"], state="readonly", font=self.get_best_font(9))
        self.category_filter.set("Toutes")
        self.category_filter.pack(side=tk.LEFT, padx=(0, 10))
        self.category_filter.bind('<<ComboboxSelected>>', self.filter_items)
        
        ttk.Label(control_frame, text="Rechercher:", font=self.get_best_font(9)).pack(side=tk.LEFT, padx=(10, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=30, font=self.get_best_font(9))
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.filter_items)
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="Ajouter objet", command=self.add_item_dialog, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Supprimer", command=self.remove_selected_item, style="Success.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Modifier", command=self.modify_selected_item, style="TButton").pack(side=tk.LEFT, padx=5)
        
        tree_container = ttk.Frame(main_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Nom", "Quantité", "Catégorie")
        self.items_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=20)
        
        self.items_tree.heading("ID", text="ID")
        self.items_tree.heading("Nom", text="Nom")
        self.items_tree.heading("Quantité", text="Quantité")
        self.items_tree.heading("Catégorie", text="Catégorie")
        
        self.items_tree.column("ID", width=80)
        self.items_tree.column("Nom", width=300)
        self.items_tree.column("Quantité", width=100)
        self.items_tree.column("Catégorie", width=150)
        
        v_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.items_tree.yview)
        h_scroll = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.items_tree.xview)
        self.items_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.items_tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        self.items_tree.bind('<Double-1>', lambda e: self.modify_selected_item())
        
    def create_pokedex_tab(self):
        """Créer l'onglet Pokédex avec interface inspirée de l'éditeur original"""
        main_frame = ttk.Frame(self.pokedex_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barre d'outils supérieure
        top_bar = ttk.Frame(main_frame)
        top_bar.pack(fill=tk.X, side=tk.TOP)
        
        ttk.Label(top_bar, text="Pokédex Editor", font=self.get_best_font(15, 'bold')).pack(side=tk.LEFT, padx=12, pady=12)
        self.pokedex_status_label = ttk.Label(top_bar, text="Aucun fichier chargé", font=self.get_best_font(9))
        self.pokedex_status_label.pack(side=tk.RIGHT, padx=12)
        
        # Barre d'outils de chargement/sauvegarde
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, padx=8, pady=(8, 6))
        
        left = ttk.Frame(toolbar)
        left.pack(side=tk.LEFT)
        
        ttk.Button(left, text="Charger Save", command=self.load_pokedex_save, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(left, text="Sauvegarder Modifications", command=self.save_pokedex_modifications,
                  style="Success.TButton").pack(side=tk.LEFT, padx=4)
        
        # Options de sauvegarde
        opts = ttk.Frame(toolbar)
        opts.pack(side=tk.RIGHT)
        
        self.backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts, text="Créer Sauvegarde", variable=self.backup_var,
                       style="TCheckbutton").pack(side=tk.RIGHT, padx=6)
        
        # Actions groupées
        bulk = ttk.Frame(main_frame)
        bulk.pack(fill=tk.X, padx=8, pady=(0, 6))
        
        ttk.Label(bulk, text="Actions Groupées:", font=self.get_best_font(9, 'bold')).pack(side=tk.LEFT, padx=(0, 6))
        
        self.all_captured_var = tk.BooleanVar()
        self.all_battled_var = tk.BooleanVar()
        
        ttk.Checkbutton(bulk, text="Capturé", variable=self.all_captured_var,
                       command=self.toggle_all_captured, style="TCheckbutton").pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(bulk, text="Combattu", variable=self.all_battled_var,
                       command=self.toggle_all_battled, style="TCheckbutton").pack(side=tk.LEFT, padx=4)
        
        # Recherche
        search = ttk.Frame(main_frame)
        search.pack(fill=tk.X, padx=8, pady=(0, 6))
        
        ttk.Label(search, text="Rechercher:").pack(side=tk.LEFT, padx=(0, 6))
        
        self.pokemon_search_var = tk.StringVar()
        self.pokemon_search_var.trace_add('write', self.filter_pokemon)
        
        search_entry = ttk.Entry(search, textvariable=self.pokemon_search_var, font=self.get_best_font(9))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3, ipadx=6)
        
        # Compteur et pagination
        pagination_frame = ttk.Frame(search)
        pagination_frame.pack(side=tk.RIGHT, padx=6)
        
        self.pokemon_count_label = ttk.Label(pagination_frame, text="Modifiés: 0", font=self.get_best_font(9, 'bold'))
        self.pokemon_count_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Boutons de navigation
        ttk.Button(pagination_frame, text="◀ Précédent", command=lambda: self.change_pokemon_page(-1)).pack(side=tk.LEFT, padx=2)
        self.page_label = ttk.Label(pagination_frame, text="Page 1/1", font=self.get_best_font(9))
        self.page_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(pagination_frame, text="Suivant ▶", command=lambda: self.change_pokemon_page(1)).pack(side=tk.LEFT, padx=2)
        
        # Container pour la liste scrollable des Pokémon
        list_container = ttk.Frame(main_frame)
        list_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        
        # Configure grid pour que le container s'expande
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(0, weight=1)
        
        # Scrollable Frame pour la liste des Pokémon
        self.canvas = tk.Canvas(list_container, bg='#ecf0f1', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Frame contenu scrollable
        self.pokemon_list_frame = tk.Frame(self.canvas, bg='#ecf0f1')
        self.canvas.create_window((0, 0), window=self.pokemon_list_frame, anchor="nw")
        
        # Configuration du scrolling
        def _configure_canvas(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.pokemon_list_frame.bind('<Configure>', _configure_canvas)
        
        # Liaison de la molette de souris
        def _on_mousewheel(e):
            if getattr(e, "delta", 0):
                self.canvas.yview_scroll(int(-e.delta/120), "units")
            else:
                self.canvas.yview_scroll(-3 if e.num == 4 else 3, "units")
        
        def _bind_wheel(_):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
            self.canvas.bind_all("<Button-4>", _on_mousewheel)
            self.canvas.bind_all("<Button-5>", _on_mousewheel)
        
        def _unbind_wheel(_):
            self.canvas.unbind_all("<MouseWheel>")
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        
        self.canvas.bind("<Enter>", _bind_wheel)
        self.canvas.bind("<Leave>", _unbind_wheel)
        
        # Créer la liste des Pokémon
        self.create_pokemon_list()
        
    def create_pokemon_list(self):
        """Créer la liste moderne des Pokémon dans l'onglet Pokédex"""
        # Supprimer les widgets existants
        for w in self.pokemon_list_frame.winfo_children():
            w.destroy()
            
        # En-tête moderne
        header_frame = tk.Frame(self.pokemon_list_frame, bg='#3498db', height=35)
        header_frame.pack(fill=tk.X, padx=8, pady=(8, 12))
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Pokédex", font=self.get_best_font(14, 'bold'), 
                fg='white', bg='#3498db').pack(side=tk.LEFT, padx=15, pady=8)
        
        tk.Label(header_frame, text="", bg='#3498db').pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Légende des couleurs
        legend_frame = tk.Frame(header_frame, bg='#3498db')
        legend_frame.pack(side=tk.RIGHT, padx=15, pady=8)
        
        # BadgeCapturé
        captured_badge = tk.Frame(legend_frame, bg='#27ae60', relief='flat', bd=2)
        captured_badge.pack(side=tk.LEFT, padx=4)
        tk.Label(captured_badge, text="●", fg='#ffffff', bg='#27ae60', 
                font=self.get_best_font(10, 'bold')).pack(side=tk.LEFT, padx=4, pady=2)
        tk.Label(captured_badge, text="Capturé", fg='white', bg='#27ae60', 
                font=self.get_best_font(8)).pack(side=tk.LEFT, padx=(0, 6), pady=2)
        
        # Badge Non-capturé
        not_captured_badge = tk.Frame(legend_frame, bg='#95a5a6', relief='flat', bd=2)
        not_captured_badge.pack(side=tk.LEFT, padx=4)
        tk.Label(not_captured_badge, text="○", fg='#ffffff', bg='#95a5a6', 
                font=self.get_best_font(10, 'bold')).pack(side=tk.LEFT, padx=4, pady=2)
        tk.Label(not_captured_badge, text="Non capturé", fg='white', bg='#95a5a6', 
                font=self.get_best_font(8)).pack(side=tk.LEFT, padx=(0, 6), pady=2)
        
        # Calculer les Pokémon à afficher (paginé)
        start_idx = self.pokemon_current_page * self.pokemon_items_per_page
        end_idx = min(start_idx + self.pokemon_items_per_page, len(POKEMON_IDS))
        current_page_pokemon = POKEMON_IDS[start_idx:end_idx]
        
        # Créer les cartes pour les Pokémon de la page courante
        for idx, pid in enumerate(current_page_pokemon):
            self.create_pokemon_card(pid, idx)
            
        # Mise à jour du canvas
        self.pokemon_list_frame.update_idletasks()
        
        # Mettre à jour le label de page
        self.page_label.config(text=f"Page {self.pokemon_current_page + 1}/{self.pokemon_total_pages}")
        
        # Désactiver les boutons selon la page
        self.update_pagination_buttons()
    
    def change_pokemon_page(self, direction):
        """Changer de page dans la liste des Pokémon"""
        new_page = self.pokemon_current_page + direction
        
        if 0 <= new_page < self.pokemon_total_pages:
            self.pokemon_current_page = new_page
            self.create_pokemon_list()
    
    def update_pagination_buttons(self):
        """Mettre à jour l'état des boutons de pagination"""
        # Cette fonction sera appelée après avoir créé les widgets de pagination
        pass
        
    def create_pokemon_card(self, pid, index):
        """Créer une carte moderne pour un Pokémon"""
        # Déterminer si le Pokémon est capturé (par défaut)
        is_captured = hasattr(self, 'pokemon_vars') and pid in self.pokemon_vars and \
                     self.pokemon_vars[pid]['captured'].get()
        
        # Couleur de fond basée sur le statut
        if is_captured:
            bg_color = '#d5f4e6'  # Vert clair pour les capturés
            border_color = '#27ae60'
            status_color = '#27ae60'
            status_icon = "●"
        else:
            bg_color = '#f8f9fa'  # Gris très clair pour les non-capturés
            border_color = '#e9ecef'
            status_color = '#6c757d'
            status_icon = "○"
        
        # Frame principal de la carte
        card_frame = tk.Frame(self.pokemon_list_frame, bg=bg_color, relief='solid', bd=1)
        card_frame.pack(fill=tk.X, padx=8, pady=4)
        
        # Stocker l'ID du Pokémon comme attribut pour le filtrage
        card_frame.pokemon_id = pid
        
        # Frame interne avec padding
        inner_frame = tk.Frame(card_frame, bg=bg_color)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
        
        # Initialiser les variables si nécessaire
        if not hasattr(self, 'pokemon_vars'):
            self.pokemon_vars = {}
            
        if pid not in self.pokemon_vars:
            self.pokemon_vars[pid] = {
                'captured': tk.BooleanVar(),
                'battled': tk.BooleanVar()
            }
            # Associer les variables aux changements
            for v in self.pokemon_vars[pid].values():
                v.trace_add('write', lambda *_: self.update_pokemon_count())
        
        # Section gauche - ID et nom
        left_frame = tk.Frame(inner_frame, bg=bg_color)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # ID avec badge de couleur
        id_frame = tk.Frame(left_frame, bg=bg_color)
        id_frame.pack(fill=tk.X)
        
        status_badge = tk.Label(id_frame, text=status_icon, fg=status_color, bg=bg_color,
                               font=self.get_best_font(12, 'bold'))
        status_badge.pack(side=tk.LEFT)
        
        id_label = tk.Label(id_frame, text=f"#{pid:03d}", fg='#2c3e50', bg=bg_color,
                           font=self.get_best_font(10, 'bold'))
        id_label.pack(side=tk.LEFT, padx=(8, 0))
        
        # Nom du Pokémon
        name_label = tk.Label(left_frame, text=POKEMON_DATA[pid], fg='#2c3e50', bg=bg_color,
                             font=self.get_best_font(11))
        name_label.pack(fill=tk.X, pady=(2, 0))
        
        # Section droite - Checkboxes
        right_frame = tk.Frame(inner_frame, bg=bg_color)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Checkbox Capturé
        captured_frame = tk.Frame(right_frame, bg=bg_color)
        captured_frame.pack(anchor='e', pady=2)
        
        tk.Label(captured_frame, text="Capturé:", fg='#2c3e50', bg=bg_color,
                font=self.get_best_font(9)).pack(side=tk.LEFT, padx=(0, 8))
        
        captured_checkbox = ttk.Checkbutton(captured_frame, variable=self.pokemon_vars[pid]['captured'])
        captured_checkbox.pack(side=tk.LEFT)
        
        # Checkbox Combattu
        battled_frame = tk.Frame(right_frame, bg=bg_color)
        battled_frame.pack(anchor='e', pady=2)
        
        tk.Label(battled_frame, text="Combattu:", fg='#2c3e50', bg=bg_color,
                font=self.get_best_font(9)).pack(side=tk.LEFT, padx=(0, 8))
        
        battled_checkbox = ttk.Checkbutton(battled_frame, variable=self.pokemon_vars[pid]['battled'])
        battled_checkbox.pack(side=tk.LEFT)
        
        # Ajouter un effet hover
        def on_enter(event):
            card_frame.configure(bg='#e8f5e8' if is_captured else '#f1f3f4', relief='raised', bd=2)
            
        def on_leave(event):
            card_frame.configure(bg=bg_color, relief='solid', bd=1)
        
        card_frame.bind("<Enter>", on_enter)
        card_frame.bind("<Leave>", on_leave)
        
    def filter_pokemon(self, *_):
        """Filtrer les Pokémon selon le terme de recherche"""
        term = self.pokemon_search_var.get().lower()
        
        # Parcourir toutes les cartes et les masquer d'abord
        for card_widget in self.pokemon_list_frame.winfo_children():
            # Vérifier si c'est une carte Pokémon (a l'attribut pokemon_id)
            if hasattr(card_widget, 'pokemon_id'):
                card_widget.pack_forget()
        
        # Afficher les cartes correspondant au terme de recherche
        for card_widget in self.pokemon_list_frame.winfo_children():
            if hasattr(card_widget, 'pokemon_id'):
                pid = card_widget.pokemon_id
                name = POKEMON_DATA[pid].lower()
                matches = (not term or  # Si pas de terme de recherche, afficher tout
                          term in name or 
                          f"{pid}" == term or 
                          f"#{pid:03d}" == term or
                          f"{pid:03d}" == term)
                
                if matches:
                    card_widget.pack(fill=tk.X, padx=8, pady=4)
                    
        # Remettre à jour le canvas
        self.pokemon_list_frame.update_idletasks()
        
    def update_pokemon_count(self):
        """Mettre à jour le compteur de Pokémon modifiés"""
        count = sum(1 for pid in POKEMON_IDS
                   if any(self.pokemon_vars[pid][k].get() for k in ('captured', 'battled')))
        self.pokemon_count_label.config(text=f"Modifiés: {count}")
        
    def toggle_all_captured(self):
        """Activer/désactiver tous les Pokémon comme capturés"""
        v = self.all_captured_var.get()
        for pid in POKEMON_IDS:
            self.pokemon_vars[pid]['captured'].set(v)
            
    def toggle_all_battled(self):
        """Activer/désactiver tous les Pokémon comme combattus"""
        v = self.all_battled_var.get()
        for pid in POKEMON_IDS:
            self.pokemon_vars[pid]['battled'].set(v)
            
    def load_pokedex_save(self):
        """Charger les données de sauvegarde pour le Pokédex"""
        # Utilise la même fonction que le chargement principal
        self.open_save_file()
        
    def save_pokedex_modifications(self):
        """Sauvegarder les modifications du Pokédex"""
        if not self.save_file_path:
            messagebox.showerror("Erreur", "Veuillez charger un fichier de sauvegarde d'abord")
            return
            
        selected = []
        for pid in POKEMON_IDS:
            c = self.pokemon_vars[pid]['captured'].get()
            b = self.pokemon_vars[pid]['battled'].get()
            if c or b:
                selected.append({
                    'id': pid,
                    'is_captured': c,
                    'is_battled': b,
                    'capture_count': 1
                })
                
        if not selected:
            messagebox.showwarning("Attention", "Aucun Pokémon sélectionné")
            return
            
        try:
            self.process_pokedex_save_file(selected)
            messagebox.showinfo("Succès", f"Fichier de sauvegarde mis à jour !\n{len(selected)} Pokémon modifiés.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la sauvegarde:\n{e}")
            
    def process_pokedex_save_file(self, pokemon_entries):
        """Traiter les modifications du Pokédex et sauvegarder"""
        if not self.hash_db or not self.pokedex_accessor:
            raise ValueError("Aucune donnée de pokédex chargée")
            
        input_path = os.path.abspath(self.save_file_path)
        in_dir = os.path.dirname(input_path)
        in_name = os.path.basename(input_path)
        
        output_path = os.path.join(in_dir, "main")
        backup_path = os.path.join(in_dir, in_name + "_old")
        
        # Créer une sauvegarde
        if self.backup_var.get():
            if os.path.exists(backup_path):
                os.remove(backup_path)
            shutil.copy2(input_path, backup_path)
            
        # Appliquer les modifications
        for entry in pokemon_entries:
            dev_no = int(entry["id"])
            if self.pokedex_accessor.is_pokedex_data_out_of_range(dev_no):
                continue
                
            core = self.pokedex_accessor.get_pokedex_data(dev_no)
            core.set_captured(0, bool(entry["is_captured"]))
            core.set_battled(0, bool(entry["is_battled"]))
            self.pokedex_accessor.set_pokedex_data(dev_no, core)
            
        # Mettre à jour les données dans hash_db
        if hasattr(HashDBKeys, 'PokeDex'):
            dex_block = self.hash_db[HashDBKeys.PokeDex]
            dex_block.change_data(self.pokedex_accessor.to_bytes())
        else:
            # Si PokeDex n'existe pas dans HashDBKeys, l'ajouter dynamiquement
            from plaza.crypto.fnvhash import FnvHash
            poke_dex_key = FnvHash.hash_fnv1a_32("POKEDEX_SAVE_DATA")
            dex_block = self.hash_db[poke_dex_key]
            dex_block.change_data(self.pokedex_accessor.to_bytes())
            
        # Sauvegarder
        encrypted = SwishCrypto.encrypt(self.hash_db.blocks)
        with open(output_path, "wb") as f:
            f.write(encrypted)
            
        self.is_modified = True
        self.update_status(f"Pokédex sauvegardé - {len(pokemon_entries)} modifications")
        
    def create_pokemon_tab(self):
        """Créer l'onglet Pokémon (en développement)"""
        main_frame = ttk.Frame(self.pokemon_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        info_label = ttk.Label(main_frame, text="Fonctionnalité Pokémon en développement\n\nCette section permettra de:\n- Voir l'équipe Pokémon\n- Modifier les statistiques\n- Changer les niveaux\n- Gérer les objets tenus", justify=tk.CENTER)
        info_label.pack(expand=True)
        
    def create_tools_tab(self):
        """Créer l'onglet Outils"""
        main_frame = ttk.Frame(self.tools_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        repair_frame = ttk.LabelFrame(main_frame, text="Outils de réparation")
        repair_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(repair_frame, text="Réparer le sac", command=self.repair_bag).pack(pady=5)
        ttk.Button(repair_frame, text="Vérifier l'intégrité", command=self.check_integrity).pack(pady=5)
        
        quick_frame = ttk.LabelFrame(main_frame, text="Modifications rapides")
        quick_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(quick_frame, text="Tous les objets x999", command=self.add_all_items).pack(pady=5)
        ttk.Button(quick_frame, text="Réinitialiser le sac", command=self.reset_bag).pack(pady=5)
        ttk.Button(quick_frame, text="Argent maximum", command=self.max_money).pack(pady=5)
        
        info_frame = ttk.LabelFrame(main_frame, text="Informations")
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        self.info_text = tk.Text(info_frame, wrap=tk.WORD, height=10)
        info_scroll = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scroll.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def update_status(self, message: str):
        """Mettre à jour la barre de statut"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def on_player_data_changed(self, event=None):
        """Marquer les données comme modifiées"""
        self.is_modified = True
        self.update_status("Données modifiées - N'oubliez pas de sauvegarder")
        
    def open_save_file(self):
        """Ouvrir un fichier de sauvegarde"""
        file_path = filedialog.askopenfilename(
            title="Ouvrir un fichier de sauvegarde PLZA",
            filetypes=[("Fichiers de sauvegarde", "*"), ("Tous les fichiers", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            self.update_status("Chargement du fichier...")
            
            with open(file_path, "rb") as f:
                data = f.read()
                
            if not data.startswith(SAVE_FILE_MAGIC):
                messagebox.showerror("Erreur", "Ce fichier n'est pas une sauvegarde PLZA valide")
                return
                
            # Décrypter les données
            blocks = SwishCrypto.decrypt(data)
            self.hash_db = HashDB(blocks)
            
            # Charger les données du sac
            try:
                self.bag_save = BagSave.from_bytes(self.hash_db[HashDBKeys.BagSave].data)
            except KeyError:
                messagebox.showerror("Erreur", "Impossible de trouver les données du sac")
                return
                
            # Charger les données du joueur
            try:
                core_data_block = self.hash_db[HashDBKeys.CoreData]
                self.core_data = CoreData.from_bytes(core_data_block.data)
            except (KeyError, AttributeError):
                self.core_data = None
                
            # Charger les données du Pokédex
            try:
                from plaza.crypto.fnvhash import FnvHash
                poke_dex_key = FnvHash.hash_fnv1a_32("POKEDEX_SAVE_DATA")
                dex_block = self.hash_db[poke_dex_key]
                self.pokedex_accessor = PokedexSaveDataAccessor.from_bytes(dex_block.data)
                
                # Initialiser les variables de Pokémon
                for pid in POKEMON_IDS:
                    if not self.pokedex_accessor.is_pokedex_data_out_of_range(pid):
                        core = self.pokedex_accessor.get_pokedex_data(pid)
                        
                        # Créer les variables si elles n'existent pas encore
                        if pid not in self.pokemon_vars:
                            self.pokemon_vars[pid] = {
                                'captured': tk.BooleanVar(),
                                'battled': tk.BooleanVar()
                            }
                        
                        # Initialiser avec les données de sauvegarde
                        self.pokemon_vars[pid]['captured'].set(core.is_captured(0))
                        self.pokemon_vars[pid]['battled'].set(core.is_battled(0))
                    else:
                        # Créer les variables même si hors portée (par défaut False)
                        if pid not in self.pokemon_vars:
                            self.pokemon_vars[pid] = {
                                'captured': tk.BooleanVar(),
                                'battled': tk.BooleanVar()
                            }
                        
                self.pokedex_status_label.config(text=f"Chargé: {os.path.basename(file_path)}", foreground='#2ecc71')
                
            except (KeyError, AttributeError):
                self.pokedex_accessor = None
                self.pokedex_status_label.config(text="Aucune donnée Pokédex trouvée", foreground='#e74c3c')
                
            self.save_file_path = file_path
            self.save_data = data
            self.is_modified = False
            
            # Mettre à jour l'interface
            self.update_ui_with_save_data()
            self.update_status(f"Fichier chargé: {os.path.basename(file_path)}")
            
            messagebox.showinfo("Succès", "Fichier de sauvegarde chargé avec succès!")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {str(e)}")
            self.update_status("Erreur lors du chargement")
            
    def update_ui_with_save_data(self):
        """Mettre à jour l'interface avec les données de sauvegarde"""
        if self.core_data:
            try:
                player_name = ""
                for char_code in self.core_data.name:
                    if char_code == 0:
                        break
                    player_name += chr(char_code)
                self.player_name_var.set(player_name)
            except:
                self.player_name_var.set("Inconnu")
                
            try:
                self.gender_var.set("Masculin" if self.core_data.sex == 0 else "Féminin")
            except:
                self.gender_var.set("Masculin")
                
            try:
                self.player_id_var.set(str(self.core_data.id))
            except:
                self.player_id_var.set("0")
                
            try:
                self.mega_power_var.set(str(self.core_data.mega_power))
            except:
                self.mega_power_var.set("0.0")
        else:
            self.player_name_var.set("Non disponible")
            self.gender_var.set("Masculin")
            self.player_id_var.set("Non disponible")
            self.mega_power_var.set("Non disponible")
            
        self.money_var.set("999999")
        self.update_items_list()
        self.update_file_info()
        
    def update_items_list(self):
        """Mettre à jour la liste des objets dans le sac"""
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
            
        if not self.bag_save:
            return
            
        for i, entry in enumerate(self.bag_save.entries):
            if entry.quantity > 0:
                item_name = self.get_item_name(i)
                category_name = self.get_category_name(entry.category)
                
                self.items_tree.insert("", "end", values=(
                    i,
                    item_name,
                    entry.quantity,
                    category_name
                ))
                
    def get_item_name(self, item_id: int) -> str:
        """Obtenir le nom d'un objet par son ID"""
        if item_id in self.item_database:
            return self.item_database[item_id]["english_ui_name"]
        return f"Objet Inconnu ({item_id})"
        
    def get_category_name(self, category) -> str:
        """Obtenir le nom d'une catégorie"""
        try:
            category_value = category if isinstance(category, int) else category.value
            category_names = {
                -1: "Corrompu",
                0: "Médicaments", 
                1: "Poké Balls",
                2: "Autres",
                3: "Pickup",
                4: "Objets Clés",
                5: "Baies",
                6: "CT",
                7: "Méga"
            }
            return category_names.get(category_value, f"Catégorie {category_value}")
        except:
            return "Inconnue"
            
    def filter_items(self, event=None):
        """Filtrer les objets par catégorie et recherche"""
        if not self.bag_save:
            return
            
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
            
        category_filter = self.category_filter.get()
        search_term = self.search_var.get().lower()
        
        for i, entry in enumerate(self.bag_save.entries):
            if entry.quantity > 0:
                item_name = self.get_item_name(i)
                category_name = self.get_category_name(entry.category)
                
                if category_filter != "Toutes" and category_name != category_filter:
                    continue
                    
                if search_term and search_term not in item_name.lower():
                    continue
                    
                self.items_tree.insert("", "end", values=(
                    i,
                    item_name,
                    entry.quantity,
                    category_name
                ))
                
    def add_item_dialog(self):
        """Dialogue pour ajouter un objet"""
        if not self.bag_save:
            messagebox.showwarning("Attention", "Aucun fichier de sauvegarde chargé")
            return
            
        dialog = ItemAddDialog(self.root, self.item_database)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            item_id, quantity = dialog.result
            try:
                self.add_item(item_id, quantity)
                self.update_items_list()
                self.is_modified = True
                self.update_status(f"Objet ajouté: {self.get_item_name(item_id)} x{quantity}")
                messagebox.showinfo("Succès", f"{self.get_item_name(item_id)} x{quantity} ajouté au sac!")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'ajout: {str(e)}")
                
    def add_item(self, item_id: int, quantity: int):
        """Ajouter un objet au sac"""
        if not self.bag_save:
            raise ValueError("Aucune donnée de sac chargée")
            
        if item_id not in self.item_database:
            raise ValueError(f"Objet ID {item_id} non trouvé dans la base de données")
            
        expected_category = self.item_database[item_id]["expected_category"]
        
        entry = BagEntry()
        entry.quantity = quantity
        entry.category = expected_category
        
        self.bag_save.set_entry(item_id, entry)
        
    def modify_selected_item(self):
        """Modifier l'objet sélectionné"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un objet")
            return
            
        item = self.items_tree.item(selection[0])
        item_id = int(item['values'][0])
        current_quantity = int(item['values'][2])
        
        new_quantity = simpledialog.askinteger(
            "Modifier la quantité",
            f"Nouvelle quantité pour {item['values'][1]}:",
            initialvalue=current_quantity,
            minvalue=0,
            maxvalue=999
        )
        
        if new_quantity is not None:
            try:
                if new_quantity == 0:
                    entry = BagEntry()
                    entry.quantity = 0
                    entry.category = 0
                    self.bag_save.set_entry(item_id, entry)
                else:
                    entry = self.bag_save.entries[item_id]
                    entry.quantity = new_quantity
                    self.bag_save.set_entry(item_id, entry)
                    
                self.update_items_list()
                self.is_modified = True
                self.update_status("Objet modifié")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la modification: {str(e)}")
                
    def remove_selected_item(self):
        """Supprimer l'objet sélectionné"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un objet")
            return
            
        item = self.items_tree.item(selection[0])
        item_name = item['values'][1]
        
        if messagebox.askyesno("Confirmer", f"Supprimer {item_name} ?"):
            item_id = int(item['values'][0])
            try:
                entry = BagEntry()
                entry.quantity = 0
                entry.category = 0
                self.bag_save.set_entry(item_id, entry)
                
                self.update_items_list()
                self.is_modified = True
                self.update_status("Objet supprimé")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")
                
    def reset_bag(self):
        """Réinitialiser le sac (supprimer tous les objets)"""
        if not self.bag_save:
            messagebox.showwarning("Attention", "Aucun fichier de sauvegarde chargé")
            return
            
        if messagebox.askyesno("Confirmer", "Supprimer tous les objets du sac ?"):
            try:
                for i in range(len(self.bag_save.entries)):
                    entry = BagEntry()
                    entry.quantity = 0
                    entry.category = 0
                    self.bag_save.set_entry(i, entry)
                    
                self.update_items_list()
                self.is_modified = True
                self.update_status("Sac réinitialisé")
                messagebox.showinfo("Succès", "Sac réinitialisé")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {str(e)}")
                
    def add_all_items(self):
        """Ajouter tous les objets avec quantité maximale"""
        if not self.bag_save:
            messagebox.showwarning("Attention", "Aucun fichier de sauvegarde chargé")
            return
            
        if messagebox.askyesno("Confirmer", "Ajouter tous les objets avec quantité x999 ?"):
            try:
                added_count = 0
                for item_id, item_data in self.item_database.items():
                    expected_category = item_data["expected_category"]
                    
                    entry = BagEntry()
                    entry.quantity = 999
                    entry.category = expected_category
                    self.bag_save.set_entry(item_id, entry)
                    added_count += 1
                    
                self.update_items_list()
                self.is_modified = True
                self.update_status(f"{added_count} objets ajoutés")
                messagebox.showinfo("Succès", f"{added_count} objets ajoutés")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {str(e)}")
                
    def max_money(self):
        """Maximiser l'argent"""
        self.money_var.set("999999")
        self.is_modified = True
        self.update_status("Argent maximisé")
        
    def repair_bag(self):
        """Réparer le sac (corriger les catégories)"""
        if not self.bag_save:
            messagebox.showwarning("Attention", "Aucun fichier de sauvegarde chargé")
            return
            
        try:
            repaired_count = 0
            for i, entry in enumerate(self.bag_save.entries):
                if entry.quantity > 0:
                    if i in self.item_database:
                        expected_category = self.item_database[i]["expected_category"]
                        if entry.category != expected_category:
                            entry.category = expected_category
                            self.bag_save.set_entry(i, entry)
                            repaired_count += 1
                    else:
                        entry.quantity = 0
                        entry.category = 0
                        self.bag_save.set_entry(i, entry)
                        repaired_count += 1
                        
            self.update_items_list()
            if repaired_count > 0:
                self.is_modified = True
                self.update_status(f"{repaired_count} objets réparés")
                messagebox.showinfo("Succès", f"{repaired_count} objets réparés")
            else:
                messagebox.showinfo("Info", "Aucune réparation nécessaire")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {str(e)}")
            
    def check_integrity(self):
        """Vérifier l'intégrité du fichier"""
        if not self.save_data:
            messagebox.showwarning("Attention", "Aucun fichier de sauvegarde chargé")
            return
            
        try:
            is_valid = SwishCrypto.get_is_hash_valid(self.save_data)
            status = "Valide" if is_valid else "Invalide"
            messagebox.showinfo("Intégrité", f"Hash du fichier: {status}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la vérification: {str(e)}")
            
    def update_file_info(self):
        """Mettre à jour les informations du fichier"""
        if not self.hash_db:
            return
            
        info = []
        info.append(f"Fichier: {os.path.basename(self.save_file_path) if self.save_file_path else 'Non chargé'}")
        info.append(f"Nombre de blocs: {len(self.hash_db.blocks)}")
        
        if self.bag_save:
            item_count = sum(1 for entry in self.bag_save.entries if entry.quantity > 0)
            info.append(f"Objets dans le sac: {item_count}")
            
        if self.core_data:
            info.append(f"ID du joueur: {self.core_data.id}")
            
        try:
            is_valid = SwishCrypto.get_is_hash_valid(self.save_data) if self.save_data else False
            info.append(f"Hash valide: {'Oui' if is_valid else 'Non'}")
        except:
            info.append("Hash valide: Erreur de vérification")
            
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "\n".join(info))
        
    def save_file(self):
        """Sauvegarder le fichier actuel"""
        if not self.save_file_path:
            self.save_file_as()
            return
            
        self.save_to_file(self.save_file_path)
        
    def save_file_as(self):
        """Sauvegarder sous un nouveau nom"""
        if not self.hash_db:
            messagebox.showwarning("Attention", "Aucun fichier de sauvegarde chargé")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Sauvegarder le fichier",
            defaultextension="",
            filetypes=[("Fichiers de sauvegarde", "*"), ("Tous les fichiers", "*.*")]
        )
        
        if file_path:
            self.save_to_file(file_path)
            
    def save_to_file(self, file_path: str):
        """Sauvegarder dans un fichier spécifique"""
        try:
            # Appliquer les modifications des données du joueur
            if self.core_data:
                try:
                    player_name = self.player_name_var.get()
                    name_array = [0] * 13
                    for i, char in enumerate(player_name[:12]):
                        name_array[i] = ord(char)
                    self.core_data.name = name_array
                except:
                    pass
                    
                try:
                    self.core_data.sex = 0 if self.gender_var.get() == "Masculin" else 1
                except:
                    pass
                    
                try:
                    self.core_data.mega_power = float(self.mega_power_var.get())
                except:
                    pass
                    
                self.hash_db[HashDBKeys.CoreData].change_data(self.core_data.to_bytes())
                
            # Mettre à jour les données du sac
            if self.bag_save:
                self.hash_db[HashDBKeys.BagSave].change_data(self.bag_save.to_bytes())
                
            # Créer une sauvegarde
            self.create_backup()
            
            # Chiffrer et sauvegarder
            encrypted_data = SwishCrypto.encrypt(self.hash_db.blocks)
            with open(file_path, "wb") as f:
                f.write(encrypted_data)
                
            self.is_modified = False
            self.save_file_path = file_path
            self.update_status(f"Sauvegardé: {os.path.basename(file_path)}")
            messagebox.showinfo("Succès", "Fichier sauvegardé avec succès!")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
            
    def create_backup(self):
        """Créer une sauvegarde du fichier original"""
        if not self.save_file_path or not os.path.exists(self.save_file_path):
            return
            
        backup_path = self.save_file_path + ".backup"
        if not os.path.exists(backup_path):
            try:
                shutil.copy2(self.save_file_path, backup_path)
                self.update_status(f"Sauvegarde créée: {os.path.basename(backup_path)}")
            except Exception as e:
                print(f"Erreur lors de la création de la sauvegarde: {e}")
                
    def quit_app(self):
        """Quitter l'application"""
        if self.is_modified:
            result = messagebox.askyesnocancel(
                "Sauvegarder",
                "Des modifications non sauvegardées existent. Voulez-vous sauvegarder avant de quitter ?"
            )
            if result is None:  # Annuler
                return
            elif result:  # Oui, sauvegarder
                self.save_file()
                
        self.root.quit()
        
    def show_about(self):
        """Afficher les informations de l'application"""
        about_text = """Pokemon Legends Z-A Save Editor avec Pokédex
Version 1.0

Un éditeur de sauvegarde complet pour Pokemon Legends Z-A avec interface graphique.

Fonctionnalités:
• Édition des objets du sac
• Modification des données du joueur
• Édition du Pokédex (Nouvel onglet)
• Outils de réparation
• Interface intuitive
• Sauvegarde sécurisée

Développé par MiniMax Agent

Basé sur la bibliothèque plaza
Merci aux mainteneurs de PKHeX pour SwishCrypto"""

        messagebox.showinfo("À propos", about_text)


class ItemAddDialog:
    """Dialogue pour ajouter un objet"""
    def __init__(self, parent, item_database):
        self.result = None
        self.item_database = item_database
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Ajouter un objet")
        self.dialog.geometry("600x400")
        self.dialog.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Recherche
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Rechercher:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        self.search_entry.bind('<KeyRelease>', self.filter_items)
        
        # Liste des objets
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Nom", "Catégorie")
        self.items_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        self.items_tree.heading("ID", text="ID")
        self.items_tree.heading("Nom", text="Nom")
        self.items_tree.heading("Catégorie", text="Catégorie")
        
        self.items_tree.column("ID", width=80)
        self.items_tree.column("Nom", width=300)
        self.items_tree.column("Catégorie", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Quantité
        quantity_frame = ttk.Frame(main_frame)
        quantity_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(quantity_frame, text="Quantité:").pack(side=tk.LEFT)
        self.quantity_var = tk.IntVar(value=1)
        quantity_spinbox = ttk.Spinbox(quantity_frame, from_=1, to=999, textvariable=self.quantity_var, width=10)
        quantity_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Ajouter", command=self.add_item).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Annuler", command=self.cancel).pack(side=tk.RIGHT)
        
        # Remplir la liste
        self.populate_items()
        
        # Double-clic pour ajouter
        self.items_tree.bind('<Double-1>', lambda e: self.add_item())
        
    def populate_items(self):
        """Remplir la liste des objets"""
        for item_id, item_data in sorted(self.item_database.items(), key=lambda x: x[0]):
            category_names = {
                -1: "Corrompu",
                0: "Médicaments",
                1: "Poké Balls",
                2: "Autres",
                3: "Pickup",
                4: "Objets Clés",
                5: "Baies",
                6: "CT",
                7: "Méga"
            }
            
            expected_category = item_data.get("expected_category")
            # Récupérer la valeur de l'enum si c'est un CategoryType
            if hasattr(expected_category, 'value'):
                cat_value = expected_category.value
            else:
                cat_value = expected_category if expected_category is not None else 0
                
            category_name = category_names.get(cat_value, f"Catégorie {cat_value}")
            
            self.items_tree.insert("", "end", values=(
                item_id,
                item_data["english_ui_name"],
                category_name
            ))
            
    def filter_items(self, event=None):
        """Filtrer les objets par nom"""
        search_term = self.search_var.get().lower()
        
        # Vider la liste
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
            
        # Repeupler avec les objets filtrés
        for item_id, item_data in sorted(self.item_database.items(), key=lambda x: x[0]):
            if search_term in item_data["english_ui_name"].lower():
                category_names = {
                    -1: "Corrompu",
                    0: "Médicaments",
                    1: "Poké Balls",
                    2: "Autres",
                    3: "Pickup",
                    4: "Objets Clés",
                    5: "Baies",
                    6: "CT",
                    7: "Méga"
                }
                
                expected_category = item_data.get("expected_category")
                # Récupérer la valeur de l'enum si c'est un CategoryType
                if hasattr(expected_category, 'value'):
                    cat_value = expected_category.value
                else:
                    cat_value = expected_category if expected_category is not None else 0
                    
                category_name = category_names.get(cat_value, f"Catégorie {cat_value}")
                
                self.items_tree.insert("", "end", values=(
                    item_id,
                    item_data["english_ui_name"],
                    category_name
                ))
                
    def add_item(self):
        """Ajouter l'objet sélectionné"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un objet")
            return
            
        item = self.items_tree.item(selection[0])
        item_id = int(item['values'][0])
        quantity = self.quantity_var.get()
        
        self.result = (item_id, quantity)
        self.dialog.destroy()
        
    def cancel(self):
        """Annuler"""
        self.dialog.destroy()


def main():
    """Fonction principale"""
    root = tk.Tk()
    app = PLZASaveEditor(root)
    
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()