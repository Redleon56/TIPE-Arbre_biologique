import os
import numpy as np
import matplotlib.pyplot as plt
import random as rd
import tkinter as tk
import tkinter.messagebox as tkmsg
import tkinter.filedialog as tkfil

from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from matplotlib import style
from mpl_toolkits.mplot3d import Axes3D
from set_axes_equal import set_axes_equal

import data as data

from branches import branche
from feuilles import feuille
from fonctions_lectures import *
from fonctions_calculs import limite_r, distance

#=====================================================
class arbre:
        #──────────────────────────────────────────────
        def __init__(self,name='fenêtre',seed = None):
                
                self.dico_arbre = data.dico_depart

                #Fonction pour tracer la distribution gaussienne.
                self.gauss = lambda x: (1/np.sqrt(2*np.pi*self.dico_arbre['sigma']**2))*np.exp(-x**2/(2*self.dico_arbre['sigma']**2)) if self.dico_arbre['sigma'] != 0 else (1 if x == 0 else 0)
                
                        #=============
                #Création de la fenêtre graphique.
                self.root = tk.Tk()
                self.root.geometry("800x835+790+0")
                self.root.title(name)

                #Création d'un menu lié à la fenêtre.
                menubar = tk.Menu(self.root)

                #Ajout des fontions liées à l'Arbre:
                menufichier = tk.Menu(menubar,tearoff=0)
                menufichier.add_command(label='Ouvrir',command=self.ouvrir_arbre)
                menufichier.add_command(label='Enregistrer',command=self.enregistrer_arbre)
                menufichier.add_command(label='Enregistrer sous...',command=self.enregistrer_sous_arbre)

                menubar.add_cascade(label="Arbre", menu= menufichier)
                
                    #─────────────────────
                #Ajout des fonctions liées aux paramètres:
                menufichier = tk.Menu(menubar,tearoff=0)
                menufichier.add_command(label='Ouvrir',command=self.ouvrir_parametres)
                menufichier.add_command(label='Enregistrer',command=self.enregistrer_parametres)
                menufichier.add_command(label='Enregistrer sous...',command=self.enregistrer_sous_parametres)

                menubar.add_cascade(label="Paramètres", menu= menufichier)
                
                    #─────────────────────
                self.root.config(menu=menubar)
                
                        #=============
                self.emplacement_arbre = ''
                self.emplacement_parametres = ''
                
                           #──────
                #Gestion de l'aléatoire via une seed.
                self.seed = seed
                if not(self.seed is None): rd.seed(self.seed)

                self.decompte = 0

                #Création de l'arbre de départ.
                self.arbre = branche(position_pere = (0,0,0), 
                                     degre = 90, 
                                     dico_arbre = self.dico_arbre, 
                                     var_degre = 90., 
                                     inclinaison = 0., 
                                     position = (0,0,self.dico_arbre["longueur élémentaire de croissance"]))

                #Initialisation du graphique de l'énergie:
                self.arbre.energie = self.dico_arbre["energie arbre départ"]
                self.energie_arb = [self.arbre.energie]
                self.time = [0]
                
                        #=============
                #Ajout de scrollbar pour permettre le déplacement au sein de la fenêtre:
                self.droite_gauche = tk.Scrollbar(self.root, orient='horizontal')
                self.droite_gauche.grid(row=1,column=0,sticky=tk.E+tk.W)
                self.haut_bas = tk.Scrollbar(self.root, orient='vertical')
                self.haut_bas.grid(row=0,column=1,sticky=tk.N+tk.S)

                self.c = tk.Canvas(self.root, yscrollcommand = self.haut_bas.set, xscrollcommand = self.droite_gauche.set )
                self.c.grid(row=0,column=0,sticky=tk.N+tk.E+tk.S+tk.W)
                self.droite_gauche.config(command=self.c.xview)
                self.haut_bas.config(command=self.c.yview)

                self.root.grid_rowconfigure(0, weight=1)
                self.root.grid_columnconfigure(0, weight=1)

                #Création de la frame de travail:
                self.frame = tk.Frame(self.c)

                #Ajout des différents widgets:
                self.champ_iter_var = tk.IntVar()
                self.champ_iter = tk.Checkbutton(self.frame,text = 'Simulation',variable = self.champ_iter_var)

                self.parametre = ttk.Combobox(self.frame, value= data.liste_nom_var, state= 'readonly')
                self.parametre.current(0)

                self.parametre.bind('<<ComboboxSelected>>',self.modifie_var)

                self.variable = tk.StringVar()
                self.saisie = tk.Entry(self.frame,textvariable= self.variable)

                self.modifie_var(0)

                #Création de la liste des différents Label pour suivre la variation des paramètres:
                self.label = [tk.Label(self.frame,text = i) for i in data.liste_nom_var]
                self.valeur = {}
                for i in data.liste_nom_var:
                    self.valeur[i] = tk.StringVar()
                    self.valeur[i].set(self.dico_arbre[i])

                self.label_value = [tk.Label(self.frame,textvariable= self.valeur[i]) for i in data.liste_nom_var]

                self.clock_value = tk.StringVar()
                self.clock = tk.Label(self.frame, textvariable= self.clock_value)
                self.clock_value.set("temps: {}".format(self.time[-1]))

                style.use("ggplot")

                self.fig = Figure(figsize=(7, 7), dpi=112)

                self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
                
                #Création des trois zones contenant respectivement l'arbre, l'énergie et la distrubution gaussienne.
                self.axe = self.fig.add_subplot(10,10,(1,70),projection='3d')
                self.axe2 = self.fig.add_subplot(10,10,(88,100))
                self.proba = self.fig.add_subplot(10,10,(81,96))

                self.axe._axis3don = False
                        #=============
                
                self.anim = FuncAnimation(self.fig, self.actualisation, interval=self.dico_arbre['delta t'])
                
                #Initialisation de l'affichage de la fenêtre graphique.
                self.afficher()

        #=============================================
        def recreer_arbre(self, tab, pere = (0,0,0)):
            #Fonction récursive permettant de recréer un arbre à partir d'un tableau contenant les bonnes informations.
            #Création d'un dictionnaire pour faciliter la récupération des données.
            dico_aux = {'position' : None,
                        'var_degre' : None,
                        'inclinaison' : None,
                        'pourcent_nouvelle_br' : None,
                        'nb_max_branche' : None,
                        'energie' : None,
                        'feuilles' : None,
                        'fils' : None}
            
            #Sécurité si des informations sont désordonnées.
            for i in tab:
                if i[0] in dico_aux:
                    dico_aux[i[0]] = i[1]

            #Création de la branche.
            arbre = branche(position_pere = pere,
                            position = (dico_aux['position'][0], dico_aux['position'][1], dico_aux['position'][2]),
                            var_degre = dico_aux['var_degre'],
                            inclinaison = dico_aux['inclinaison'],
                            pourcent_nouvelle_br = dico_aux['pourcent_nouvelle_br'],
                            nb_max_branche = dico_aux['nb_max_branche'],
                            energie = dico_aux['energie'], 
                            dico_arbre = self.dico_arbre)
            
            #Récupération de la feuille:
            if not(dico_aux['feuilles'] is None):
                arbre.feuilles = feuille(vie = dico_aux['feuilles'], dico = self.dico_arbre)
                arbre.bool_feuille = arbre.feuilles is None

            #Récupération des sous-branches:
            for i in dico_aux['fils']:
                arbre.fils.append(self.recreer_arbre(i,(dico_aux['position'][0], dico_aux['position'][1], dico_aux['position'][2])))

            return arbre

        #────────────────────────────────
        def ouvrir_arbre(self):
            #Fonction pour convertir un fichier txt contenant les bonnes informations en un arbre
            emplacement = tkfil.askopenfilename(parent= self.root)
            if emplacement != '':
                self.emplacement_arbre = emplacement

                with open(emplacement,'r') as fichier:
                    self.arbre = self.recreer_arbre(lecture(ligne(fichier.read())))
                    
                    self.axe.clear()
                    self.axe2.clear()

                    self.energie_arb = []
                    self.time = []

                    self.affichage()

        #────────────────────────────────
        def arbre_text(self,arbre, iterat = 0, profondeur = 0):
            #Fonction de convertion d'un arbre en string
            text = '{'
            text += "position: {};".format(arbre.position)
            text += '\n' + ' '*8*profondeur
            text += "var_degre: {};".format(arbre.var_degre)
            text += '\n' + ' '*8*profondeur
            text += "inclinaison: {};".format(arbre.inclinaison)
            text += '\n' + ' '*8*profondeur
            text += "pourcent_nouvelle_br: {};".format(arbre.pourcent_nouvelle_br)
            text += '\n' + ' '*8*profondeur
            text += "nb_max_branche: {};".format(arbre.nb_max_branche)
            text += '\n' + ' '*8*profondeur
            text += "energie: {};".format(arbre.energie)
            text += '\n' + ' '*8*profondeur
            text += "feuilles: {};".format(arbre.feuilles.longevite if not(arbre.feuilles is None) else None)
            text += '\n' + ' '*8*profondeur
            text += "fils: ["
            
            n = len(arbre.fils)
            for i,fils in enumerate(arbre.fils):
                text += self.arbre_text(fils,(n-i-1),profondeur + 1)
            
            text += ']}' if iterat == 0 else (']};\n' + ' '*(8*profondeur - 1 ))

            return text 

        #────────────────────────────────
        def enregistrer_arbre(self):
            #Fonction pour sauvegarder sous fichier txt un arbre.
            if self.emplacement_arbre == '':
                self.enregistrer_sous_arbre()
            else:
                with open(self.emplacement_arbre,'w') as files:
                    files.write(self.arbre_text(self.arbre))

        #────────────────────────────────
        def enregistrer_sous_arbre(self):
            self.emplacement_arbre = tkfil.asksaveasfilename(parent= self.root)
            if self.emplacement_arbre != '':
                if not(self.emplacement_arbre.endswith('.txt')):
                    self.emplacement_arbre += '.txt'
                self.enregistrer_arbre()

        #===============
        def ouvrir_parametres(self):
            #Fonction pour attribuer les paramètres d'un fichier txt contenant les bonnes informations.
            emplacement = tkfil.askopenfilename(parent=self.root)
            if emplacement != '':
                self.emplacement_parametres = emplacement

                with open(emplacement,'r') as fichier:
                    txt = fichier.read().split('\n')
                    for i in txt:
                        tab = i.split(':')
                        if tab[0] in self.dico_arbre:
                            if tab[0] in data.liste_entier:
                                self.dico_arbre[tab[0]] = int(tab[1])
                            else:
                                self.dico_arbre[tab[0]] = float(tab[1])

                            self.valeur[tab[0]].set(self.dico_arbre[tab[0]])
                    self.modifie_var(0)

        #────────────────────────────────
        def enregistrer_parametres(self):
            #Fonction pour sauvegarder les paramètres en fichier txt.
            if self.emplacement_parametres == '':
                self.enregistrer_sous_parametres()

            else:
                texte = ""
                for i in data.liste_nom_var:
                    if i in self.dico_arbre:
                        texte += '{}: {}\n'.format(i,self.dico_arbre[i])

                with open(self.emplacement_parametres,'w') as files:
                    files.write(texte)

        #────────────────────────────────
        def enregistrer_sous_parametres(self):
            self.emplacement_parametres = tkfil.asksaveasfilename(parent= self.root)
            if self.emplacement_parametres != '':
                if not(self.emplacement_parametres.endswith('.txt')):
                    self.emplacement_parametres += '.txt'
                self.enregistrer_parametres()

        #==============================================
        def modifie_var(self,event):
            #Fonction pour modifier la valeur dans la zone d'écriture quand on sélectionne un paramètre.
            var_text = self.parametre.get()
            self.variable.set(self.dico_arbre[var_text])

        #──────────────────────────────────────────────
        def pousse(self):
            #Fonction qui fait évoluer l'arbre tant qu'il a de l'énergie.
            self.arbre.energie = self.arbre.recup_energie()
            self.energie_arb.append(self.arbre.energie)

            if self.arbre.energie >= 0:
                self.arbre.distribution(self.arbre.energie)
                if not(self.dico_arbre['énergie produite par feuille']== 0):
                        self.arbre.decoupe()

            if self.arbre.energie <= 0 and not(self.dico_arbre['énergie produite par feuille']== 0):
                self.decompte += 1

        #──────────────────────────────────────────────
        def reinit(self):
            #Fonction qui réinitialise l'arbre.
            self.axe.clear()
            self.axe2.clear()

            if not(self.seed is None): rd.seed(self.seed)
            self.decompte = 0

            self.arbre = branche(position_pere = (0,0,0), 
                                 degre = 90, 
                                 dico_arbre = self.dico_arbre, 
                                 var_degre = 90., 
                                 inclinaison = 0., 
                                 position = (0,0,self.dico_arbre["longueur élémentaire de croissance"]))
            branche.temps = 0
            self.arbre.energie = self.dico_arbre["energie arbre départ"]
            self.energie_arb = [self.arbre.energie]
            self.time = [0]

        #──────────────────────────────────────────────
        def attribut_constante(self):
            #Fonction qui modifie les paramètres quand on appuie sur le bouton modifier.
            var_text = self.parametre.get()
            
            if var_text in data.liste_entier : 
                self.dico_arbre[var_text] = int(self.variable.get())

            else:
                self.dico_arbre[var_text] = float(self.variable.get())

            self.valeur[var_text].set(self.dico_arbre[var_text])
            self.anim.event_source.interval = self.dico_arbre["delta t"]

        #──────────────────────────────────────────────
        def actualisation(self,dt):
            #Fonction qui actualise les différentes choses.
            #La gaussienne:
            val_95 = 2*self.dico_arbre['sigma']
            X = np.linspace(-val_95,val_95,2*int(val_95)*100) if val_95 > 1 else np.linspace(-1,1,200)
            H = np.vectorize(self.gauss)(X)
            self.proba.clear()
            self.proba.plot(X,H,marker = '',linestyle ='-',color = 'blue')
            
            #L'arbre et son énergie:
            if self.champ_iter_var.get() == 1:
                    branche.temps += 1

                    branche.points_branches = [[],[],[]]
                    
                    self.pousse()
                    self.affichage()

        #──────────────────────────────────────────────
        def affichage(self):
            #Fonction qui gère l'affichage de l'arbre et de son énergie
            self.axe.clear()

            self.arbre.affiche_branche(self.axe)

            self.axe2.clear()

            #Sécurité si la liste est vide.
            if self.time == []:
                self.time = [0]
            else:
                self.time.append((self.time[-1]+1))

            if self.decompte >= 10:
                self.reinit()
            
            self.clock_value.set("temps: {}".format(self.time[-1]))

            self.axe2.plot(self.time,self.energie_arb)

            set_axes_equal(self.axe)                

                
        #──────────────────────────────────────────────
        def afficher(self):
            #Fonction qui affiche la fenêtre graphique en rajoutant les derniers boutons et label
            nb_label = len(self.label)

            self.clock.grid(row=1,column=0)

            tk.Label(self.frame,text='Évolution automatique:').grid(row=1,column=1)
            self.champ_iter.grid(row=1, column=2)
            tk.Button(self.frame,text='réinitialiser', command = self.reinit).grid(row=1,column=4)

            self.parametre.grid(row=1,column=5,columnspan=3,sticky=tk.E+tk.W)
            self.saisie.grid(row=1,column=8)
            tk.Button(self.frame,text='modifier',command= self.attribut_constante).grid(row=1,column=9)

            self.canvas.get_tk_widget().grid(row=2,rowspan=(nb_label+1),column=0,columnspan=5,sticky=tk.N+tk.E+tk.S+tk.W)
            for i in range(nb_label):
                self.label[i].grid(row = 2+i,column = 6)
                self.label_value[i].grid(row = 2+i,column = 7)
            
            self.c.create_window(0, 0,  window=self.frame)
            self.frame.update_idletasks()
            self.c.config(scrollregion=self.c.bbox("all"))
            self.c.xview_moveto(0)
            self.c.yview_moveto(0)
            
            self.root.mainloop()
            
#=====================================================
