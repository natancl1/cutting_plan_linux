# Importação dos módulos necessários
import random, copy, time
from pulp import *

# Função com algoritmo simplex para maximizar a utilização do comprimento da faixa horizontal
def simplexH(x, z, y):
    probH = LpProblem("corteH", LpMaximize) # Definindo se o problema é maximizar ou minimizar
    # Definição das variáveis
    qtdh = []
    for i in range(len(x)):
        qtdh.append(LpVariable('x%d' % i, 0, cat='Integer'))
    # Função Objetivo
    probH += sum((x[i][0]+y) * qtdh[i] for i in range(len(x)))-y
    # Restrições
    for c in range(len(x)):
        probH += qtdh[c] <= x[c][2]
    probH += sum((x[i][0]+y) * qtdh[i] for i in range(len(x)))-y <= z[0]
    for c in range(len(x)):
        for i in range(len(x)):
            if (x[c][0] == x[i][1]) and (x[c][1] == x[i][0]) and (x[c][0] != x[c][1]):
                probH += qtdh[c] + qtdh[i] <= x[c][2]
    # Resolvendo o problema
    probH.solve()
    # Adicionando os valores das variaveis em uma lista
    pecasimh = []
    for v in probH.variables():
        pecasimh += [v.varValue]
    # A função retorna a lista com a quantidade de peças
    return pecasimh
# Função com algoritmo simplex para maximização da utilização da faixa vertical
def simplexV(x, z, y):
    probV = LpProblem("corteV", LpMaximize) # Definindo se o problema é maximizar ou minimizar
    # Definição das variáveis
    qtdv = []
    for i in range(0, len(x)):
        qtdv.append(LpVariable('x%d' % i, 0, cat='Integer'))
    # Função Objetivo
    probV += sum((x[i][1]+y) * qtdv[i] for i in range(0, len(x)))-y
    # Restrições
    for c in range(0, len(x)):
        probV += qtdv[c] <= x[c][2]
    probV += sum((x[i][1]+y) * qtdv[i] for i in range(0, len(x)))-y <= z[1]
    for c in range(len(x)):
        for i in range(len(x)):
            if (x[c][0] == x[i][1]) and (x[c][1] == x[i][0]) and (x[c][0] != x[c][1]):
                probV += qtdv[c] + qtdv[i] <= x[c][2]
    # Resolvendo o problema
    probV.solve()
    # Adicionando os valores das variaveis em uma lista
    pecasimv = []
    for v in probV.variables():
        pecasimv += [v.varValue]
    # A função retorna a lista com a quantidade de peças
    return pecasimv
# Função com o algoritmo GRASP para resolução do problema de corte bidimensional
def grasp_2d(P, R, a, maxiter,limit,t, esp):
    melhor_sol , aprov_ms = [] , 0
    R.sort(key=lambda x: x[0]*x[1])
    start = time.time()
    finish = time.time()
    for f in range(1, maxiter + 1):
        if (finish-start)>=(t*60):
            break
        sol_corr , aprov_sc , soma_chapas , C , Re = [] , 0 , 0 , [], []
        C = copy.deepcopy(P)
        Re = copy.deepcopy(R)
        while (C != []) and (Re != []):
            padcorte, Clinha = [], []
            Clinha = copy.deepcopy(C)
            Rf = Re[0].copy()
            # Comparação do comprimento e largura de todas as peças com o comprimento e largura da chapa
            qtdpqne = 0 # Se o qtdpqne (quantidade de peças que não entram) for igual a quantidade total de peças não será possível executar o algoritmo
            for c in Clinha:
                if (c[0] > Rf[0]) or (c[1] > Rf[1]):
                    qtdpqne += 1
            if qtdpqne != len(Clinha):
            	soma_chapas += (Re[0][0] * Re[0][1])
            	#cd.append(Re[0].copy()) LINHA DE CÓDIGO PARA GERAR A LISTA DE CHAPAS QUE SERÃO DESENHADAS NO CANVAS. OBS: PRECISA DECLARAR A VARIÁVEL NO INÍCIO
            while (Clinha != []) and (qtdpqne != len(Clinha)):
                # Definição da peça com maior área (Beta)
                Clinha.sort(key=lambda x: x[3], reverse=True)
                B = Clinha[0][3]
                # Construção do conjunto de peças LRC
                LRC = [c[:] for c in Clinha if ((a * B) <= c[3] <= B) and (c[0] <= Rf[0]) and (c[1] <= Rf[1])]
                # Escolha aleatória da peça em LRC
                if LRC != []:
                    pk = random.choice(LRC)
                    # Construção das faixas
                    Fh , Fv = [Rf[0], pk[1]] , [pk[0], Rf[1]] # Faixa horizontal e vertical
                    # Definição das peças que poderão melhorar a faixa horizontal
                    simH , lpifh = [] , []
                    Bh = [c[:] for c in Clinha if (c[1] <= Fh[1])]
                    # Ordenação da maior para a menor largura de peça
                    Bh.sort(key=lambda x: x[1], reverse=True)
                    # Procedimento para separar as peças com larguras iguais e aplicar o simplex utilizando ambos os tamanhos
                    while (len(Bh) >= 2) and (Fh[0] >= min(Bh)[0]):
                        while (len(Bh) >= 2) and (Bh[0][1] == Bh[1][1]):
                            simH.append(Bh[1][:])
                            Bh.remove(Bh[1])
                        simH.append(Bh[0][:])
                        Bh.remove(Bh[0])
                        qtdpcsh = simplexH(simH, Fh, esp)  # Quantidade de peças calculadas usando simplex para a horizontal
                        sumFh = sum((qtdpcsh[i] * (simH[i][0]+esp)) for i in range(len(qtdpcsh)))
                        if Fh[0] >= sumFh:
                            Fh[0] -= sumFh
                        else:
                            Fh[0] -= (sumFh-esp)
                        for c in range(len(simH)):
                            for i in range(len(Bh)):
                                if (simH[c][0] == Bh[i][1] != simH[c][1]) and (simH[c][1] == Bh[i][0]):
                                    Bh[i][2] -= int(qtdpcsh[c])
                        # Lista de peças que serão incluídas na faixa horizontal
                        while simH != []:
                            for i in range(int(qtdpcsh[0])):
                                lpifh.append(simH[0][:])
                            qtdpcsh.remove(qtdpcsh[0])
                            simH.remove(simH[0])
                    while (Bh != []) and (Fh[0] >= Bh[0][0]):
                        qtdpcsh = simplexH(Bh, Fh, esp)
                        sumFh = sum((qtdpcsh[i] * (Bh[i][0]+esp)) for i in range(len(qtdpcsh)))
                        if Fh[0] >= sumFh:
                            Fh[0] -= sumFh
                        else:
                            Fh[0] -= (sumFh-esp)
                        while (Bh != []):
                            for i in range(int(qtdpcsh[0])):
                                lpifh.append(Bh[0][:])
                            qtdpcsh.remove(qtdpcsh[0])
                            Bh.remove(Bh[0])
                    # Definição das peças que poderão melhorar a faixa vertical
                    simV , lpifv = [] , []
                    Bv = [c[:] for c in Clinha if c[0] <= Fv[0]]
                    # Procedimento para obter a menor largura de peça
                    Bv.sort(key=lambda x: x[1])
                    minlargBv = Bv[0][1]
                    # Ordenação do maior para o menor comprimento de peça
                    Bv.sort(key=lambda x: x[0], reverse=True)
                    # Procedimento para separar as peças com comprimentos iguais e aplicar o simplex utilizando ambos os tamanhos
                    while (len(Bv) >= 2) and (Fv[1] >= minlargBv):
                        while (len(Bv) >= 2) and (Bv[0][0] == Bv[1][0]):
                            simV.append(Bv[1][:])
                            Bv.remove(Bv[1])
                        simV.append(Bv[0][:])
                        Bv.remove(Bv[0])
                        qtdpcsv = simplexV(simV, Fv, esp) # Quantidade de peças calculadas usando simplex para a vertical
                        sumFv = sum((qtdpcsv[i] * (simV[i][1]+esp)) for i in range(len(qtdpcsv)))
                        if Fv[1] >= sumFv:
                            Fv[1] -= sumFv
                        else:
                            Fv[1] -= (sumFv-esp)
                        for c in range(len(simV)):
                            for i in range(len(Bv)):
                                if (simV[c][0] == Bv[i][1] != simV[c][1]) and (simV[c][1] == Bv[i][0]):
                                    Bv[i][2] -= int(qtdpcsv[c])
                        # Lista de peças que serão incluídas na faixa vertical
                        while simV != []:
                            for i in range(int(qtdpcsv[0])):
                                lpifv.append(simV[0][:])
                            qtdpcsv.remove(qtdpcsv[0])
                            simV.remove(simV[0])
                    while (Bv != []) and (Fv[1] >= Bv[0][1]):
                        qtdpcsv = simplexV(Bv, Fv, esp)
                        sumFv = sum((qtdpcsv[i] * (Bv[i][1]+esp)) for i in range(len(qtdpcsv)))
                        if Fv[1] >= sumFv:
                            Fv[1] -= sumFv
                        else:
                            Fv[1] -= (sumFv-esp)
                        while (Bv != []):
                            for i in range(int(qtdpcsv[0])):
                                lpifv.append(Bv[0][:])
                            qtdpcsv.remove(qtdpcsv[0])
                            Bv.remove(Bv[0])
                    # Cálculo dos percentuais de utilização das faixas horizontal e vertical
                    Fmelhor , somH , somV = [] , 0 , 0
                    for c in lpifh:
                        somH += c[3]
                    percentualH = (somH / (Rf[0] * Fh[1]))
                    for c in lpifv:
                        somV += c[3]
                    percentualV = (somV / (Rf[1] * Fv[0]))
                    if (percentualH > percentualV) and (lpifh != []):
                        lpifh.append("h")
                        Fmelhor = lpifh[:]
                        if Rf[1] >= (Fh[1]+esp):
                            Rf[1] -= (Fh[1]+esp)
                        else:
                            Rf[1] -= Fh[1]
                        lpifh.remove(lpifh[len(lpifh)-1])
                    elif (percentualH <= percentualV) and (lpifv != []):
                        lpifv.append("v")
                        Fmelhor = lpifv[:]
                        if Rf[0] >= (Fv[0]+esp):
                            Rf[0] -= (Fv[0]+esp)
                        else:
                            Rf[0] -= Fv[0]
                        lpifv.remove(lpifv[len(lpifv)-1])
                    if Fmelhor != []:
                        padcorte.append(Fmelhor[:])
                    # Atualiza a lista Clinha baseado na lista Fmelhor
                    prov = []
                    while (len(Fmelhor) >= 2) and (Clinha != []):
                        while (len(Fmelhor) >= 2) and (Fmelhor[0][0] == Fmelhor[1][0]) and (Fmelhor[0][1] == Fmelhor[1][1]):
                            prov.append(Fmelhor[1][:])
                            Fmelhor.remove(Fmelhor[1])
                        prov.append(Fmelhor[0][:])
                        Fmelhor.remove(Fmelhor[0])
                        ind = []
                        for c in range(len(Clinha)):
                            if (Clinha[c][0] == prov[0][0]) and (Clinha[c][1] == prov[0][1]):
                                Clinha[c][2] -= len(prov)
                                if Clinha[c][2] == 0:
                                    ind.append(c)
                            elif (Clinha[c][0] == prov[0][1]) and (Clinha[c][1] == prov[0][0]):
                                Clinha[c][2] -= len(prov)
                                if Clinha[c][2] == 0:
                                    ind.append(c)
                        if (ind != []) and (Clinha != []):
                            for c in range(len(ind)):
                                if c == 0:
                                    Clinha.remove(Clinha[ind[c]])
                                else:
                                    Clinha.remove(Clinha[ind[c]-c])
                        ind = []
                        prov.clear()
                    ind = []
                    if (Fmelhor != []) and (Clinha != []):
                        for c in range(len(Clinha)):
                            if (Fmelhor[0][0] == Clinha[c][0]) and (Fmelhor[0][1] == Clinha[c][1]):
                                Clinha[c][2] -= len(Fmelhor)
                                if Clinha[c][2] == 0:
                                    ind.append(c)
                            elif (Fmelhor[0][0] == Clinha[c][1]) and (Fmelhor[0][1] == Clinha[c][0]):
                                Clinha[c][2] -= len(Fmelhor)
                                if Clinha[c][2] == 0:
                                    ind.append(c)
                        if (ind != []) and (Clinha != []):
                            for c in range(len(ind)):
                                if c == 0:
                                    Clinha.remove(Clinha[ind[c]])
                                else:
                                    Clinha.remove(Clinha[ind[c]-c])
                        ind = []
                    if Clinha != []:
                        qtdpqne = 0 # Se o qtdpqne (quantidade de peças que não entram) for igual a quantidade total de peças não será possível executar o algoritmo
                        for c in Clinha:
                            if (c[0] > Rf[0]) or (c[1] > Rf[1]):
                                qtdpqne += 1
                else:
                    break
            # A solução corrente é atualizada com o padcorte e o conjunto C recebe Clinha
            sol_corr.append(padcorte)
            C = Clinha
            Re.remove(Re[0])
        # Cálculo do aproveitamento da solução corrente
        soma_sol_corr = 0
        for i in range(len(sol_corr)):
            for j in range(len(sol_corr[i])):
                for k in range(len(sol_corr[i][j])-1):
                    soma_sol_corr += sol_corr[i][j][k][0] * sol_corr[i][j][k][1]
        aprov_sc = soma_sol_corr/soma_chapas
        # Se o aproveitamento da solução corrente for maior que o da melhor solução, esta recebe aquela
        if aprov_sc > aprov_ms:
            aprov_ms = aprov_sc
            melhor_sol = sol_corr
        if aprov_ms >= limit:
            break
        finish = time.time()
    if (melhor_sol == []) and (aprov_ms == 0):
        print('O valor de alfa pode estar muito alto')
    return (melhor_sol, aprov_ms, f, (finish-start),C)