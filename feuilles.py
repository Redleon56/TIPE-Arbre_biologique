import data as data

#=====================================================
class feuille:
        #──────────────────────────────────────────────
        def __init__(self, vie = None ,dico = None):
                self.dico = data.dico_depart if dico is None else dico
                self.longevite = dico["longévité d'une feuille"] if vie is None else vie
                
        #──────────────────────────────────────────────
        def energie_fe(self,n):
                if self.longevite > 0:
                        self.longevite -= 1
                        pourcent = (100-(5*n)) if ((5*n) < 100) else 0
                        enerj = (pourcent*self.dico["énergie produite par feuille"]//100) - self.dico["consommation d'énergie par feuille"]
                        return enerj if enerj > 0 else 0
                else:
                        return 0
                    
#=====================================================
