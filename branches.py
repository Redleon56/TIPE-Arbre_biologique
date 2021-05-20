import random as rd
import numpy as np

import data as data

from feuilles import feuille
from fonctions_calculs import est_en_dessous, distance, couleur_energie

#================================================================
class branche:
	temps = 0
	point_branches = [[],[],[]]

	#──────────────────────────────────────────────
	def __init__(self,
		     position_pere = None,
		     degre = None,
		     dico_arbre = None,
		     position = None,
		     var_degre = None,
		     inclinaison = None,
		     pourcent_nouvelle_br = None,
		     nb_max_branche = None,
		     energie = None,
		     feuilles = None,
		     pourcent_nouvelle_feuille = None,
		     fils = None,
		     tps_vie = None):
		
		self.tps_vie = 0 if tps_vie is None else tps_vie
		self.position_pere = (0,0,0) if position_pere is None else position_pere
		self.dico_arbre = data.dico_depart if dico_arbre is None else dico_arbre

		self.fils = [] if fils is None else fils
		self.premier_branche = self.fils == [] or self.fils[0].tps_vie == 0
		self.nb_max_branche = rd.randint(self.dico_arbre["nombre minimal de branches générables"],self.dico_arbre["nombre maximal de branches générables"]) if nb_max_branche == None else nb_max_branche
		self.nb_branche = len(self.fils)
		
		self.feuilles = feuilles
		self.bool_feuille = not(self.feuilles is None)
		self.pourcent_nouvelle_feuille = self.dico_arbre['probabilité de faire pousser une feuille au départ (en %)'] if pourcent_nouvelle_feuille is None else pourcent_nouvelle_feuille
		
		self.energie = self.dico_arbre["énergie de base d'une branche"] if energie is None else energie

		degre = 90 if degre is None else degre
				
		self.var_degre = rd.normalvariate(degre,self.dico_arbre["sigma"]) if var_degre is None else var_degre
		x,y,z = position_pere

		degre_rad = int(self.dico_arbre["precision"]*2*np.pi*self.var_degre/360)/self.dico_arbre["precision"]
		proj_h = int(self.dico_arbre["precision"]*np.cos(degre_rad))/self.dico_arbre["precision"]
		self.inclinaison = rd.vonmisesvariate(np.pi,0) if inclinaison is None else inclinaison
		
		self.position = (x + self.dico_arbre["longueur élémentaire de croissance"]*proj_h*int(self.dico_arbre["precision"]*np.cos(self.inclinaison))/self.dico_arbre["precision"],
				 y + self.dico_arbre["longueur élémentaire de croissance"]*proj_h*int(self.dico_arbre["precision"]*np.sin(self.inclinaison))/self.dico_arbre["precision"],
				 z + self.dico_arbre["longueur élémentaire de croissance"]*int(self.dico_arbre["precision"]*np.sin(degre_rad))/self.dico_arbre["precision"]) if position is None else position

		self.sol()

		self.consommation = self.dico_arbre["consommation d'énergie par sous-branches directes"]*len(self.fils)**self.dico_arbre["puissance"] + self.dico_arbre["consommation d'énergie pour vivre par branche"]
		self.production = 0

		self.pourcent_nouvelle_br = self.dico_arbre["probabilité d'apparition de nouvelles branches (en %)"]
		self.pourcent_feuille = self.dico_arbre["probabilité de faire pousser une feuille minimale (en %)"]
		
	#────────────────────────────────────────────────────────────────────────────────────────────
	def sol(self):
		x,y,z = self.position
		if z < 0:
		   self.position = x,y,0   
	
	#──────────────────────────────────────────────
	def nb_branche_au_dessus(self,feuille):
		n = len(self.point_branches[0])
		accu = 0
		for i in range(n//3):
			P1 = [self.point_branches[0][3*i],self.point_branches[2][3*i]]
			P2 = [self.point_branches[0][3*i+1],self.point_branches[2][3*i+1]]
			x,y,z = feuille
			M = [x,z]
			if est_en_dessous(P1,P2,M):
				accu += 1
		return(accu)
		
	#──────────────────────────────────────────────
	def energie_feuille(self):

		self.energie = self.energie if self.premier_branche else 0
		if self.nb_branche >= 1:
			self.premier_branche = False
		
		self.production = 0

		n = self.nb_branche_au_dessus(self.position)

		if self.bool_feuille:
			self.production = self.feuilles.energie_fe(n)
			if self.feuilles.longevite == 0:
				self.feuilles = None
				self.bool_feuille = False

		self.energie += self.production
	
	#──────────────────────────────────────────────
	def recup_energie(self):
		self.energie_feuille()

		for fils in self.fils:
			self.energie += fils.recup_energie()
			self.production += fils.production

		return self.energie
	
	#──────────────────────────────────────────────
	def distribution(self,enerj):
		branche_ajoute = False
		self.energie = enerj
		self.consommation =  self.dico_arbre["consommation d'énergie par sous-branches directes"]*len(self.fils)**self.dico_arbre["puissance"] + self.dico_arbre["consommation d'énergie pour vivre par branche"]
		self.energie -= self.consommation
		self.energie = self.energie if self.energie >= 0 else 0
		self.tps_vie += 1

		if not(self.bool_feuille):
			if self.fils == [] and self.energie >= self.dico_arbre["consommation d'énergie pour générer une feuille"] and (rd.randint(0,100) < self.pourcent_nouvelle_feuille or self.energie <= 5*min(self.dico_arbre["consommation d'énergie pour générer une feuille"],self.dico_arbre["consommation d'énergie pour vivre par branche"])):
				self.ajoute_feuille()
				self.pourcent_nouvelle_feuille -= self.dico_arbre["décroissance pourcent nouvelle feuille"]
				self.pourcent_nouvelle_feuille = self.pourcent_nouvelle_feuille if self.pourcent_nouvelle_feuille > self.pourcent_feuille else self.pourcent_feuille
			else:
				if self.nb_branche < self.nb_max_branche and self.energie >= self.dico_arbre["consommation d'énergie pour générer une branche"]:
					if rd.randint(0,100) < self.pourcent_nouvelle_br:  
						self.ajoute_branche()
						branche_ajoute = True
					else:
						if self.pourcent_nouvelle_br < self.dico_arbre["probabilité maximal d'apparition de nouvelles branches (en %)"]:
							self.pourcent_nouvelle_br += self.dico_arbre["croissance pourcent nouvelle branche"]
							self.pourcent_nouvelle_br = self.pourcent_nouvelle_br if self.pourcent_nouvelle_br < self.dico_arbre["probabilité maximal d'apparition de nouvelles branches (en %)"] else self.dico_arbre["probabilité maximal d'apparition de nouvelles branches (en %)"]

		if self.energie >= self.dico_arbre["consommation d'énergie pour grandir"] :
			if rd.randint(0,100) < self.dico_arbre["probabilité qu'une branche grandisse (en %)"]:
				self.energie -= self.dico_arbre["consommation d'énergie pour grandir"]
				x,y,z = self.position
				rad = 2*np.pi*self.var_degre/360
				proj_h = int(self.dico_arbre["precision"]*np.cos(rad))/self.dico_arbre["precision"]
				self.position = (x+self.dico_arbre["longueur élémentaire de croissance"]*proj_h*int(self.dico_arbre["precision"]*np.cos(self.inclinaison))/self.dico_arbre["precision"],
								 y + self.dico_arbre["longueur élémentaire de croissance"]*proj_h*int(self.dico_arbre["precision"]*np.sin(self.inclinaison))/self.dico_arbre["precision"],
								 z + self.dico_arbre["longueur élémentaire de croissance"]*int(self.dico_arbre["precision"]*np.sin(rad))/self.dico_arbre["precision"])
				self.actualiser_fils((x,y,z))

		for fils in self.fils:
			x,y,z = fils.position
			xp,yp,zp = fils.position_pere
			self.points_branches[0] += [xp,x,np.nan]
			self.points_branches[1] += [yp,y,np.nan]
			self.points_branches[2] += [zp,z,np.nan]

		self.energie = self.energie if self.energie >= 0 else 0

		somme = 0
		for fils in self.fils[:-1]:
			ajout = fils.production/fils.consommation if fils.consommation != 0 else 0
			somme += ajout
			
		if self.fils != [] and not(branche_ajoute):
			ajout = self.fils[-1].production/self.fils[-1].consommation if self.fils[-1].consommation != 0 else 0
			somme += ajout
			
		for fils in self.fils[:-1]:
			unif = 1/self.nb_branche if not(branche_ajoute) else 1/(self.nb_branche-1)
			ratio = unif if somme == 0 else ((fils.production/fils.consommation)/somme if fils.consommation != 0 else 0)
			fils.distribution(self.energie/(self.dico_arbre["ratio"]+self.dico_arbre["uniforme"]) * (self.dico_arbre["ratio"]*ratio + self.dico_arbre["uniforme"]*unif))

		if self.fils != [] and not(branche_ajoute):
			ratio = 1/self.nb_branche if somme == 0 else ((self.fils[-1].production/self.fils[-1].consommation)/somme if fils.consommation != 0 else 0)
			self.fils[-1].distribution(self.energie/(self.dico_arbre["ratio"]+self.dico_arbre["uniforme"]) * (self.dico_arbre["ratio"]*ratio + self.dico_arbre["uniforme"]*1/self.nb_branche))

	#──────────────────────────────────────────────
	def actualiser_fils(self,pos_origine):
		for i in self.fils:
			i.position_pere = self.position
			xi,yi,zi = i.position
			x0,y0,z0 = pos_origine
			x,y,z = self.position
			i.position = (xi+x-x0,
				      yi+y-y0,
				      zi+z-z0)
			i.sol()
			i.actualiser_fils((xi,yi,zi))

	#──────────────────────────────────────────────
	def ajoute_feuille(self):
		self.feuilles = feuille(dico = self.dico_arbre)
		self.bool_feuille = not(self.feuilles is None)
		self.energie -= self.dico_arbre["consommation d'énergie pour générer une feuille"]

	#──────────────────────────────────────────────
	def ajoute_branche(self):
		self.energie -= self.dico_arbre["consommation d'énergie pour générer une branche"]
		self.fils.append(branche(position_pere = self.position, degre = self.var_degre, dico_arbre = self.dico_arbre, energie = (self.dico_arbre["pourcentage d'énergie de départ (en %)"]/100)*self.energie))
		self.energie -= (self.dico_arbre["pourcentage d'énergie de départ (en %)"]/100)*self.energie
		self.nb_branche += 1
		if self.nb_branche == 1 :
			self.fils[-1].var_degre = self.var_degre
			self.fils[-1].inclinaison = self.inclinaison
			
			x,y,z = self.position
			rad = int(self.dico_arbre["precision"]*2*np.pi*self.var_degre/360)/self.dico_arbre["precision"]
			proj_h = int(self.dico_arbre["precision"]*np.cos(rad))/self.dico_arbre["precision"]
			self.fils[-1].position = (x + self.dico_arbre["longueur élémentaire de croissance"]*int(self.dico_arbre["precision"]*proj_h*np.cos(rad))/self.dico_arbre["precision"],
						  y + self.dico_arbre["longueur élémentaire de croissance"]*int(self.dico_arbre["precision"]*proj_h*np.sin(self.inclinaison))/self.dico_arbre["precision"],
						  z + self.dico_arbre["longueur élémentaire de croissance"]*int(self.dico_arbre["precision"]*np.sin(rad))/self.dico_arbre["precision"])

	#──────────────────────────────────────────────
	def affiche_branche(self,graph):
		x,y,z = self.position
		xp,yp,zp = self.position_pere

		alpha = couleur_energie(self.energie)

		graph.plot([x,xp],[y,yp],[z,zp], color = (0.36,0.18,0.,alpha), linestyle = '-', marker = '')

		if not(self.feuilles is None):
			graph.scatter(x,y,z, marker = '.',edgecolor = (0.,0.37,0.06,alpha), facecolor = (0.,0.5,0.08,alpha))


		for fils in self.fils:
			fils.affiche_branche(graph)
			
	#──────────────────────────────────────────────
	def decoupe(self):
		liste_traite = []
		while self.fils != []:
			i = self.fils.pop()
			if i.energie > 0 or (i.energie == 0 and i.tps_vie == 0):
				liste_traite.append(i)
				i.decoupe()
				

		for j in liste_traite:
			self.fils.append(j)

		self.nb_branche = len(self.fils)

#=====================================================
