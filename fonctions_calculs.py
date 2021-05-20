import numpy as np

#=====================================================
def est_en_dessous(P1,P2,M):
        entre_p1_p2 = (P1[0] < M[0] and M[0] < P2[0])
        entre_p2_p1 = (P2[0] < M[0] and M[0] < P1[0])
        signe = 1 if entre_p1_p2 else -1
        return( ( entre_p1_p2 or entre_p1_p2 ) and ( signe*( (M[0]-P1[0])*(P2[1]-P1[1]) - (P2[0]-P1[0])*(M[1]-P1[1]) ) >= 0) )

#──────────────────────────────────────────────
def distance(a,b):
        xa,_,za = a
        xb,_,zb = b
        return(np.sqrt((xb-xa)**2 + (zb-za)**2))

#──────────────────────────────────────────────
def limite_r(f,r,centre):
        a,b = centre 
        return(lambda x,y : f(x,y) if ((x-a)**2 + (y-b)**2)**(1/2) <= r else 0)

#──────────────────────────────────────────────
#tangente hyperbolique, de [0, +inf[ -> [0,1]
def couleur_energie(x): return (np.exp(x)-np.exp(-x))/(np.exp(x)+np.exp(-x))

#=====================================================
