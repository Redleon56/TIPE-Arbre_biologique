
#=====================================================
def indice_fils(txt):
    for i,j in enumerate(txt):
        if j == '[':
            return i
    return 0

#──────────────────────────────────────────────
def retire_espace(txt):
    accu = 0
    text = ''
    for i in txt.split('\t'):
        text += i
    n = len(text)
    while accu < n and text[accu] == ' ':
        accu += 1
    return(text[accu:])

#──────────────────────────────────────────────
def separation(txt):
    accu = 0
    indice = 0
    tab_res = []
    for i,j in enumerate(txt):
        if j =='{':
            accu += 1
        if j == '}':
            accu -= 1
        if accu == 0 and j != ';':
            tab_res.append(txt[indice:i+1])
            indice = i + 2
    return tab_res 

#──────────────────────────────────────────────
def lecture(txt):
    indice = indice_fils(txt)

    tab_res = [i.split(': ') for i in txt[1:indice-1].split(';')]
    tab_res[0][1] = [float(i.split('(')[-1].split(')')[0]) for i in tab_res[0][1].split(',')]

    for i in range(1,len(tab_res)-1):
        tab_res[i][1] = float(tab_res[i][1]) if tab_res[i][1] != 'None' else None

    tab_aux = separation(txt[indice+1:-2])

    tab_res[-1] = ['fils',[]]

    for i in tab_aux:
        tab_res[-1][-1].append(lecture(i))

    return tab_res

#──────────────────────────────────────────────
def ligne(txt):
    txt_res = ''
    for i in txt.split('\n'):
        txt_res += retire_espace(i)
    return txt_res

#=====================================================
