"""
Pokemon Legends Z-A Save Editor
Un éditeur de sauvegarde complet avec interface graphique pour Pokemon Legends Z-A

Fonctionnalités:
- Édition des objets du sac
- Modification des données du joueur
- Gestion des Pokémon
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
    from plaza.types import BagEntry, BagSave, CategoryType, CoreData
    from plaza.types.accessors import HashDBKeys
    from plaza.util.items import item_db
except ImportError as e:
    print(f"Erreur d'importation de la bibliothèque plaza: {e}")
    sys.exit(1)

SAVE_FILE_MAGIC = bytes([0x17, 0x2D, 0xBB, 0x06, 0xEA])

class PLZASaveEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokemon Legends Z-A Save Editor")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        self.save_data = None
        self.hash_db = None
        self.bag_save = None
        self.core_data = None
        self.save_file_path = None
        self.is_modified = False
        
        self.item_database = item_db
        
        self.create_widgets()
        self.update_status("Prêt - Chargez un fichier de sauvegarde pour commencer")
        
    def create_widgets(self):
        """Créer l'interface utilisateur principale"""
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
        ttk.Label(info_frame, text="Nom:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.player_name_var = tk.StringVar()
        self.player_name_entry = ttk.Entry(info_frame, textvariable=self.player_name_var, width=30)
        self.player_name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.player_name_entry.bind('<KeyRelease>', self.on_player_data_changed)
        
        # Genre
        ttk.Label(info_frame, text="Genre:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.gender_var = tk.StringVar()
        self.gender_combo = ttk.Combobox(info_frame, textvariable=self.gender_var, 
                                        values=["Masculin", "Féminin"], state="readonly")
        self.gender_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.gender_combo.bind('<<ComboboxSelected>>', self.on_player_data_changed)
        
        # ID du joueur
        ttk.Label(info_frame, text="ID:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.player_id_var = tk.StringVar()
        self.player_id_label = ttk.Label(info_frame, textvariable=self.player_id_var)
        self.player_id_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Statistiques de jeu
        stats_frame = ttk.LabelFrame(main_frame, text="Statistiques")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Argent
        ttk.Label(stats_frame, text="Argent:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.money_var = tk.StringVar()
        self.money_entry = ttk.Entry(stats_frame, textvariable=self.money_var, width=15)
        self.money_entry.grid(row=0, column=1, padx=5, pady=5)
        self.money_entry.bind('<KeyRelease>', self.on_player_data_changed)
        
        # Bouton pour maximiser l'argent
        ttk.Button(stats_frame, text="Max", command=self.max_money).grid(row=0, column=2, padx=5, pady=5)
        
        # Poussière stellaire (si applicable)
        ttk.Label(stats_frame, text="Méga Pouvoir:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.mega_power_var = tk.StringVar()
        self.mega_power_entry = ttk.Entry(stats_frame, textvariable=self.mega_power_var, width=15)
        self.mega_power_entry.grid(row=1, column=1, padx=5, pady=5)
        self.mega_power_entry.bind('<KeyRelease>', self.on_player_data_changed)
        
    def create_bag_tab(self):
        """Créer l'onglet du sac"""
        main_frame = ttk.Frame(self.bag_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(control_frame, text="Catégorie:").pack(side=tk.LEFT, padx=(0, 5))
        self.category_filter = ttk.Combobox(control_frame, values=["Toutes", "Médicaments", "Poké Balls", "Autres", "Pickup", "Objets Clés", "Baies", "CT", "Méga"], state="readonly")
        self.category_filter.set("Toutes")
        self.category_filter.pack(side=tk.LEFT, padx=(0, 10))
        self.category_filter.bind('<<ComboboxSelected>>', self.filter_items)
        
        ttk.Label(control_frame, text="Rechercher:").pack(side=tk.LEFT, padx=(10, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.filter_items)
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="Ajouter objet", command=self.add_item_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Supprimer", command=self.remove_selected_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Modifier", command=self.modify_selected_item).pack(side=tk.LEFT, padx=5)
        
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
        
    def create_pokemon_tab(self):
        """Créer l'onglet Pokémon"""
        main_frame = ttk.Frame(self.pokemon_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Note: Cette fonctionnalité sera étendue dans une version future
        info_label = ttk.Label(main_frame, text="Fonctionnalité Pokémon en développement\\n\\nCette section permettra de:\\n- Voir l'équipe Pokémon\\n- Modifier les statistiques\\n- Changer les niveaux\\n- Gérer les objets tenus", justify=tk.CENTER)
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
                # Si CoreData n'est pas disponible, créer des données par défaut
                self.core_data = None
                
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
        # Vider la liste actuelle
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
            
        if not self.bag_save:
            return
            
        # Ajouter les objets
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
        self.root.wait_window(dialog.dialog)  # Attendre que le dialogue se ferme
        
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
                    # Supprimer l'objet
                    entry = BagEntry()
                    entry.quantity = 0
                    entry.category = 0
                    self.bag_save.set_entry(item_id, entry)
                else:
                    # Modifier la quantité
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
        self.info_text.insert(1.0, "\\n".join(info))
        
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
                # Nom du joueur
                try:
                    player_name = self.player_name_var.get()
                    name_array = [0] * 13
                    for i, char in enumerate(player_name[:12]):
                        name_array[i] = ord(char)
                    self.core_data.name = name_array
                except:
                    pass
                    
                # Genre
                try:
                    self.core_data.sex = 0 if self.gender_var.get() == "Masculin" else 1
                except:
                    pass
                    
                # Méga pouvoir
                try:
                    self.core_data.mega_power = float(self.mega_power_var.get())
                except:
                    pass
                    
                # Mettre à jour les données dans hash_db
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
        about_text = """Pokemon Legends Z-A Save Editor
Version 1.0

Un éditeur de sauvegarde complet pour Pokemon Legends Z-A avec interface graphique.

Fonctionnalités:
• Édition des objets du sac
• Modification des données du joueur
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