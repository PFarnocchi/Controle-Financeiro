# use Python 3.12.3
# Livre para usar/alterar/modificar    :)
# não contém componentes pagos (all free) 
#---------------------------------------------------------------------------------------------------------------
#  Instalar o virtual environment       python -m venv .venv
#                                       source .venv/bin/activate   (no Linux)
#                                       C:\Pasta_Projeto\fin_control>venv\scripts\activate (no Windows)   
#
#  Para Compilar         pyinstaller -F -w finplan.py --hidden-import='PIL._tkinter_finder'   (no Linux)
#                        pyinstaller -F -w finplan.py                                         (no  Windows)
#
#  Autor:  Paulo Farnocchi     Data: 2024      Local: Maringá - Paraná        
#---------------------------------------------------------------------------------------------------------------

import FreeSimpleGUI as sg
import dbsqlite
import sys
import os
import subprocess
from datetime import date
import pr_gerapdf
import shutil
import platform

def checkSys():
    return platform.system() 

# Tabelas:          contas [id, tipo, nome, descricao, ativo]
#                   pagamento [id, id_conta, nome, detalhe, mes_ref, ano_ref, vencimento, valor, agendado, pago]
#                   recebido [id, id_conta, nome, detalhe, mes_ref, ano_ref, recebimento, valor, pagar, restou]

def janela_menu():
    sg.theme('DarkGrey3')
    layout = [
        [sg.Image(c_barra + cap_icon + 'pitoko_w.png', size=(30, 38)),
        sg.Text('Ano Ref:', size=(9, 1)),
        sg.Combo(selecAnoref, size=(10, 5), key='-SAN-', enable_events=True)],       
        [sg.Button('Contas'), sg.Button('Recebimento'), sg.Button('Pagamentos'),
        sg.Button('Calcular'), sg.Button('Mostra Gráfico'), sg.Button('Imprimir'), sg.Button('Sair')],
        [sg.Text('Para analisar a evolução das contas clique em--->'), sg.Button('Gráfico por Conta')]
    ]
    return sg.Window('Planejamento - Menu', layout, finalize=True)

def janela_conta():
    sg.theme('Topanga')
    layout = [
        [sg.Text('Entre com o nome e descrição da conta.')],
        [sg.Text('Id', size=(15, 1)), sg.InputText(key = '-Fi-', size=(30, 1)),
        sg.Button('+'), sg.Button('-')],
        [sg.Text('Tipo D/C', size=(15,1)), sg.InputText(key = '-Tc-', size=(5,1)),
         sg.Text('Ativa', size=(5,1)), sg.InputText(key = '-Zt-', size=(5,1))],
        [sg.Text('Nome', size=(15, 1)), sg.InputText(key = '-N-')],
        [sg.Text('Descrição', size=(15, 1)), sg.InputText(key = '-A-')],
        [sg.Button('Incluir'), sg.Button('Alterar'), sg.Button('Excluir'), 
         sg.Button('Contas Padrão'), sg.Button('Sair')],
        [sg.Text('Defina as contas PADRÃO.')]
    ]
    return sg.Window('Planejamento - Contas', layout, finalize=True)

def janela_recebimento():
    sg.theme('Topanga')
    layout = [
        [sg.Text('Entre com as info do Recebimento.')],
        [sg.Text('Id', size=(15, 1)), sg.InputText(key = '-Fi-', size=(30, 1)),
        sg.Button('+'), sg.Button('-')],
        [sg.Text('Nome', size=(15, 1)),
        sg.Combo(selecConta, size=(30, 5), key='-NE-', enable_events=True),
        sg.Button('Buscar')],        
        [sg.Text('Mes-Ref', size=(15, 1)), sg.InputText(key = '-MR-')],
        [sg.Text('Ano-Ref', size=(15, 1)), sg.InputText(key = '-AR-')],
        [sg.Text('Dia Receb.', size=(15, 1)), sg.InputText(key = '-DR-')],
        [sg.Text('Valor', size=(15, 1)), sg.InputText(key = '-VL-')],
        [sg.Text('Detalhe', size=(15,1)), sg.InputText(key= '-DT-')],
        [sg.Button('Incluir'), sg.Button('Alterar'), sg.Button('Excluir'), sg.Button('Sair')]
    ]
    return sg.Window('Planejamento - Recebimento', layout, finalize=True)

def janela_pagamento():
    sg.theme('Topanga')
    layout = [
        [sg.Text('Entre com a previsão do pagamento.')],
        [sg.Text('Id', size=(15, 1)), sg.InputText(key = '-Fi-', size=(30, 1)),
        sg.Button('+'), sg.Button('-')],
        [sg.Text('Nome', size=(15, 1)),
        sg.Combo(selecConta, size=(30, 5), key='-NE-', enable_events=True),
        sg.Button('Buscar')],        
        [sg.Text('Mes-Ref', size=(15, 1)), sg.InputText(key = '-PR-')],
        [sg.Text('Ano-Ref', size=(15, 1)), sg.InputText(key = '-AP-')],
        [sg.Text('Dia Vencimento', size=(15, 1)), sg.InputText(key = '-VT-')],
        [sg.Text('Valor.', size=(15, 1)), sg.InputText(key = '-VK-')],
        [sg.Text('Detalhe', size=(15,1)), sg.InputText(key= '-DT-')],
        [sg.Text('Agendado', size=(15,1)), sg.Checkbox('Sim  ', default=False, key = '-GO-')],
        [sg.Text('Pago', size=(15,1)), sg.Checkbox('Sim  ', default=False, key = '-OP-')],
        [sg.Button('Incluir'), sg.Button('Alterar'), sg.Button('Excluir'), sg.Button('Sair')]
    ]
    return sg.Window('Planejamento - Pagamentos', layout, finalize=True)

def janela_calcular():
    sg.theme('Topanga')
    layout = [
        [sg.Text('Clique para efetuar a verificação.')],
        [sg.Text('Conta Saldo', size=(15, 1)),
        sg.Combo(selecConta, size=(30, 5), key='-NE-', enable_events=True)],
        [sg.Text('Mes-Ref', size=(15, 1)), sg.InputText(key = '-PR-')],
        [sg.Text('Ano-Ref', size=(15, 1)), sg.InputText(key = '-AP-')],
        [sg.Text('Valor Inicial', size=(15, 1)), sg.InputText(key = '-VN-')],
        [sg.Text('Débitos', size=(15, 1)), sg.InputText(key = '-DB-')],
        [sg.Text('Valor Atual', size=(15, 1)), sg.InputText(key = '-RS-')],
        [sg.Button('Calcular'), sg.Button('Sair')]
    ]
    return sg.Window('Planejamento - Calcular', layout, finalize=True)

def janela_imprimir():
    sg.theme('Topanga')
    layout = [
        [sg.Text('Selecione Mes e Ano e clique Imprimir.')],
        [sg.Text('Mes', size=(4, 1)), sg.Combo(selMes, size=(3, 1), key = '-MRr-', enable_events=True, readonly=True),
        sg.Text('Ano', size=(4, 1)), sg.Combo(selAno, size=(5, 1), key = '-ARr-', enable_events=True, readonly=True)],
        [sg.Button('Imprimir'), sg.Button('Sair')]
    ]
    return sg.Window('Planejamento - Imprime PDF', layout, finalize=True)    

def janela_grafico():
    sg.theme('Topanga')
    layout = [
        [sg.Text('Selecione o Ano e clique Imprimir.')],
        [sg.Text('Ano', size=(4, 1)), sg.Combo(selAno, size=(5, 1), key = '-ARr-', enable_events=True, readonly=True)],
        [sg.Button('Imprimir'), sg.Button('Sair')]
    ]
    return sg.Window('Planejamento - Imprime gráfico PDF', layout, finalize=True)

def janela_padrao():
    sg.theme('Topanga')
    layout = [
        [sg.Text('Selecione as Contas para SALÁRIO e SALDO.')],
        [sg.Text('Conta Salário', size=(15, 1)),
        sg.Combo(selecConta, size=(30, 5), key='-LAR-', enable_events=True)],
        [sg.Text('Conta Saldo', size=(15, 1)),
        sg.Combo(selecConta, size=(30, 5), key='-LDO-', enable_events=True)],
        [sg.Button('Gravar'), sg.Button('Sair')]
    ]
    return sg.Window('Planejamento - Define Padrões', layout, finalize=True) 

def analise_contas():
    sg.theme('Topanga')
    layout = [
        [sg.Text('Selecione a Conta e Ano.')],
        [sg.Text('Conta', size=(15, 1)),
        sg.Combo(selecConta, size=(30, 5), key='-LAR-', enable_events=True),
        sg.Text(' Ano', size=(5, 1)), sg.Combo(selAno, size=(5, 1), key = '-ARr-', enable_events=True, readonly=True)],
        [sg.Button('Gerar Gráfico'), sg.Text('Será feito com ano/ano-1', size=(25, 1)), sg.Button('Sair')]
    ]
    return sg.Window('Planejamento - Análise de Conta', layout, finalize=True) 

def criar_dir(diret):
    caminho_destino = diret  
    if not os.path.exists(caminho_destino):
        os.makedirs(caminho_destino)

def copiar_arq(orig, dloc, dest, nome):
    orig = orig + dloc + nome
    if not os.path.exists(dest + nome):
        shutil.copy2(orig, dest)
        
sysop = checkSys()
if sysop == "Linux":
    c_barra = os.path.expanduser('~')
    a_bar = '/'
else:
    c_barra = "C:"     
    a_bar = '\\'
raiz =  c_barra + a_bar + "finplan"
criar_dir(raiz)
local_db = c_barra + a_bar + "finplan"  + a_bar + "db_finplan"
criar_dir(local_db)
local_imag = c_barra + a_bar + "finplan" + a_bar + "images"
criar_dir(local_imag)
local_file = c_barra + a_bar + "finplan" + a_bar + "files"
criar_dir(local_file)

diretorio_atual = os.getcwd()
origem = diretorio_atual
dloc =  a_bar + 'images'
destino = local_imag 
nome = a_bar + 'pitoko_w.png'
copiar_arq(origem, dloc, destino, nome)
dloc = a_bar + 'files'
destino = local_file 
nome = a_bar + 'template_base.png'
copiar_arq(origem, dloc, destino, nome)
dloc = a_bar + 'files'
destino = local_file
nome = a_bar + 'template_plot.png'
copiar_arq(origem, dloc, destino, nome)

banco = dbsqlite.ConectarDB()
rtcode = banco.inicia_banco()
gerar_pdf = pr_gerapdf.LosPdfs()
selecAnoref = banco.cap_AnoRef()  
raiz_dir = banco.cap_loc('raiz') 
cap_icon = banco.cap_loc('images') 
dir_path = raiz_dir + banco.cap_loc('dirpdf')
selMes = banco.all_Meses()
selAno = banco.all_Anos()

jan1, jan2, jan3 ,jan4, jan5, jan6, jan7, jan8, jan9 = janela_menu(), None, None, None, None, None, None, None, None

while True:
    window, event, values = sg.read_all_windows()
    if window == jan1 and event == sg.WIN_CLOSED:
        break
    if window == jan2 and (event == sg.WIN_CLOSED or event == 'Sair'):
        jan2.hide()
    if window == jan3 and (event == sg.WIN_CLOSED or event == 'Sair'):
        jan3.hide()
    if window == jan4 and (event == sg.WIN_CLOSED or event == 'Sair'):
        jan4.hide()
    if window == jan5 and (event == sg.WIN_CLOSED or event == 'Sair'):
        jan5.hide()
    if window == jan6 and (event == sg.WIN_CLOSED or event == 'Sair'):
        jan6.hide()
    if window == jan7 and (event == sg.WIN_CLOSED or event == 'Sair'):
        jan7.hide()
    if window == jan8 and (event == sg.WIN_CLOSED or event == 'Sair'):
        jan8.hide()
    if window == jan9 and (event == sg.WIN_CLOSED or event == 'Sair'):
        jan9.hide()

 # ---------------------------------MENU-----------------------------------------------

    if window == jan1 and event == 'Sair':
        break
    if window == jan1 and event == "Contas":
        jan2 = janela_conta()
    if window == jan1 and event == "Recebimento":
        prinAnoRef = values['-SAN-']
        selecConta  =  banco.all_Contas('C')
        jan3 = janela_recebimento()
    if window == jan1 and event == "Pagamentos":
        prinAnoRef = values['-SAN-']
        selecConta =  banco.all_Contas('D')
        jan4 = janela_pagamento()
    if window == jan1 and event == "Calcular":
        prinAnoRef = values['-SAN-']
        selecConta =  banco.all_Contas('C')
        jan5 = janela_calcular()
    if window == jan1 and event == "Mostra Gráfico":
        jan7 = janela_grafico()
    if window == jan1 and event == "Imprimir":
        jan6 = janela_imprimir()
    if window == jan1 and event == "Gráfico por Conta":
        selecConta =  banco.all_Contas('A')
        jan9 = analise_contas()     
#----------------------------------------------------------------------------------------

#---------------------------------Contas---------------------------------------------------
    if window == jan2:
        banco.pega_ultimo("contas")
        if banco.result[0] == None:
            ult_forn = 0
        else:
            ult_forn = int(banco.result[0])
        if event == "Incluir":
            id = str(ult_forn + 1)
            tipo = values['-Tc-']
            nome = values['-N-']
            descricao = values['-A-']
            ativo = values['-Zt-']
            banco.inserir_conta(id, tipo, nome, descricao, ativo)
            banco.pega_ultimo("contas")
            if banco.result[0] == None:
                ult_forn = 1
            else:
                ult_forn = int(banco.result[0])
            sg.popup('Registro de Conta incluido OK ')
        if event == '+':
            idinc = values['-Fi-']
            if idinc == '':
                idinc = 0
            idinc = int(idinc) + 1
            if idinc > ult_forn:
                idinc = 1
            id_forn = str(idinc)
            banco.consultar_registro("contas", id_forn)
            if (banco.result == None):
                sg.popup('Este ID não existe ', id_forn)
                window['-Fi-'].update(id_forn)
                window['-Tc-'].update('')
                window['-N-'].update('')
                window['-A-'].update('')
                window['-Zt-'].update('')
            else:
                window['-Fi-'].update(str(banco.result[0]))
                window['-Tc-'].update(str(banco.result[1]))
                window['-N-'].update(str(banco.result[2]))
                window['-A-'].update(str(banco.result[3]))
                window['-Zt-'].update(str(banco.result[4]))
        if event == '-':
            idinc = values['-Fi-']
            if idinc == '':
                idinc = 1
            idinc = int(idinc) - 1
            if idinc < 1:
                idinc = ult_forn
            id_forn = str(idinc)
            banco.consultar_registro("contas", id_forn)
            if (banco.result == None):
                sg.popup('Este ID não existe ', id_forn)
                window['-Fi-'].update(id_forn)
                window['-Tc-'].update('')
                window['-N-'].update('')
                window['-A-'].update('')
                window['-Zt-'].update('')
            else:
                window['-Fi-'].update(str(banco.result[0]))
                window['-Tc-'].update(str(banco.result[1]))
                window['-N-'].update(str(banco.result[2]))
                window['-A-'].update(str(banco.result[3]))
                window['-Zt-'].update(str(banco.result[4]))
        if event == "Alterar":
            id = values['-Fi-']
            tipo = values['-Tc-']
            nome = values['-N-']
            descricao = values['-A-']
            ativo = values['-Zt-']
            banco.alterar_conta(id, tipo, nome, descricao, ativo)
            sg.popup('Registro de Conta alterado OK ')
        if event == "Excluir":
            id = values['-Fi-']
            banco.excluir_conta(id)
            banco.pega_ultimo("contas")
            if banco.result[0] == None:
                ult_forn = 1
            else:
                ult_forn = int(banco.result[0])
            sg.popup('Registro de Conta excluido OK ')   
        if event == "Contas Padrão":
           selecConta  =  banco.all_Contas('C')
           jan8 = janela_padrao()     
#------------------------------------------------------------------------------------------            
        
#---------------------------------Recebimento-------------------------------------------- 
    if window == jan3:
        window['-MR-'].update(int(date.today().month))
        window['-AR-'].update(int(date.today().year))
        if len(prinAnoRef) == 0:
            window['-AR-'].update(int(date.today().year))
        else:    
            window['-AR-'].update(int(prinAnoRef[0]))
        banco.pega_ultimo("recebido")
        if banco.result[0] == None:
            ult_forn = 0
        else:
            ult_forn = int(banco.result[0])
        if event == "Incluir":
            id = str(ult_forn + 1)
            nome = values['-NE-']
            mes = values['-MR-']
            ano = values['-AR-']
            dia = values['-DR-']
            data = ano + '-' + mes + '-' + dia
            valor = values['-VL-']
            detalhe = values['-DT-']
            banco.inserir_recebimento(id, nome, detalhe, mes, ano, data, valor)
            banco.pega_ultimo("recebido")
            if banco.result[0] == None:
                ult_forn = 1
            else:
                ult_forn = int(banco.result[0])
            sg.popup('Registro de Recebimento incluido OK ')
        if event == '+':
            idinc = values['-Fi-']
            if idinc == '':
                idinc = 0
            idinc = int(idinc) + 1
            if idinc > ult_forn:
                idinc = 1
            id_forn = str(idinc)
            banco.consultar_registro("recebido", id_forn)
            if (banco.result == None):
                sg.popup('Este ID não existe ', id_forn)
                window['-Fi-'].update(id_forn)
                window['-NE-'].update('')
                window['-MR-'].update('')
                window['-AR-'].update('')
                window['-DR-'].update('')
                window['-VL-'].update('')
                window['-DT-'].update('')
            else:
                window['-Fi-'].update(str(banco.result[0]))
                window['-NE-'].update((str(banco.result[1]), str(banco.result[2])))
                window['-DT-'].update(str(banco.result[3]))
                window['-MR-'].update(str(banco.result[4]))
                window['-AR-'].update(str(banco.result[5]))
                dia = str(banco.result[6])[-2:]
                window['-DR-'].update(dia)
                window['-VL-'].update(str(banco.result[7]))
        if event == '-':
            idinc = values['-Fi-']
            if idinc == '':
                idinc = 1
            idinc = int(idinc) - 1
            if idinc < 1:
                idinc = ult_forn
            id_forn = str(idinc)
            banco.consultar_registro("recebido", id_forn)
            if (banco.result == None):
                sg.popup('Este ID não existe ', id_forn)
                window['-Fi-'].update(id_forn)
                window['-NE-'].update('')
                window['-MR-'].update('')
                window['-AR-'].update('')
                window['-DR-'].update('')
                window['-VL-'].update('')
                window['-DT-'].update('')
            else:
                window['-Fi-'].update(str(banco.result[0]))
                window['-NE-'].update((str(banco.result[1]), str(banco.result[2])))
                window['-DT-'].update(str(banco.result[3]))
                window['-MR-'].update(str(banco.result[4]))
                window['-AR-'].update(str(banco.result[5]))
                dia = str(banco.result[6])[-2:]
                window['-DR-'].update(dia)
                window['-VL-'].update(str(banco.result[7]))
        if event == "Buscar":
            bynome = values['-NE-']
            bymes = values['-MR-']
            byano = values['-AR-']
            if bynome != '' and bymes != '' and byano != '': 
                banco.buscar_registro('recebido', bynome, bymes, byano)
                if (banco.result == None):
                    sg.popup('Este Receb. não existe')
                    window['-Fi-'].update('')
                    window['-NE-'].update('')
                    window['-MR-'].update('')
                    window['-AR-'].update('')
                    window['-DR-'].update('')
                    window['-VL-'].update('')
                    window['-DT-'].update('')
                else:
                    window['-Fi-'].update(str(banco.result[0]))
                    window['-NE-'].update((str(banco.result[1]), str(banco.result[2])))
                    window['-DT-'].update(str(banco.result[3]))
                    window['-MR-'].update(str(banco.result[4]))
                    window['-AR-'].update(str(banco.result[5]))
                    dia = str(banco.result[6])[-2:]
                    window['-DR-'].update(dia)
                    window['-VL-'].update(str(banco.result[7]))
        if event == "Alterar":
            id = values['-Fi-']
            nome = values['-NE-']
            detalhe = values['-DT-']
            mes = values['-MR-']
            ano = values['-AR-']
            dia = values['-DR-']
            data = ano + '-' + mes + '-' + dia
            valor = values['-VL-']
            banco.alterar_recebimento(id, nome, detalhe, mes, ano, data, valor)
            sg.popup('Registro de Recebimento alterado OK ')
        if event == "Excluir":
            id = values['-Fi-']
            banco.excluir_recebimento(id)
            banco.pega_ultimo("recebido")
            if banco.result[0] == None:
                ult_forn = 1
            else:
                ult_forn = int(banco.result[0])
            sg.popup('Registro de Recebimento excluido OK ')   
#------------------------------------------------------------------------------------------
            
#---------------------------------Pagamentos---------------------------------------------------
    if window == jan4:
        window['-PR-'].update(int(date.today().month))
        window['-AP-'].update(int(date.today().year))
        if len(prinAnoRef) == 0:
            window['-AP-'].update(int(date.today().year))
        else:    
            window['-AP-'].update(int(prinAnoRef[0]))
        banco.pega_ultimo("pagamento")
        if banco.result[0] == None:
            ult_forn = 0
        else:
            ult_forn = int(banco.result[0])
        if event == "Incluir":
            id = str(ult_forn + 1)
            nome = values['-NE-']
            mes = values['-PR-']
            ano = values['-AP-']
            dia = values['-VT-']
            vencimento = ano + '-' + mes + '-' + dia
            valor = values['-VK-']
            detalhe = values['-DT-']            
            if values['-GO-'] == True: 
                pex = 'sim'
            else:
                pex = 'nao'
            agendado = pex
            if values['-OP-'] == True: 
                pex = 'sim'
            else:
                pex = 'nao'
            pago = pex
            banco.inserir_pagamento(id, nome, detalhe, mes, ano, vencimento, valor, agendado, pago)
            banco.pega_ultimo("pagamento")
            if banco.result[0] == None:
                ult_forn = 1
            else:
                ult_forn = int(banco.result[0])
            sg.popup('Registro de Pagamento incluido OK ')
        if event == '+':
            idinc = values['-Fi-']
            if idinc == '':
                idinc = 0
            idinc = int(idinc) + 1
            if idinc > ult_forn:
                idinc = 1
            id_forn = str(idinc)
            banco.consultar_registro("pagamento", id_forn)
            if (banco.result == None):
                sg.popup('Este ID não existe ', id_forn)
                window['-Fi-'].update(id_forn)
                window['-NE-'].update('')
                window['-DT-'].update('')                
                window['-PR-'].update('')
                window['-AP-'].update('')
                window['-VT-'].update('')
                window['-VK-'].update('')
                window['-GO-'].update(False)
                window['-OP-'].update(False)
            else:
                window['-Fi-'].update(str(banco.result[0]))
                window['-NE-'].update((str(banco.result[1]),  str(banco.result[2])))
                window['-DT-'].update(str(banco.result[3]))
                window['-PR-'].update(str(banco.result[4]))
                window['-AP-'].update(str(banco.result[5]))
                dia = str(banco.result[6])[-2:]
                window['-VT-'].update(dia)
                window['-VK-'].update(str(banco.result[7]))
                if str(banco.result[8]) == 'sim':
                    tex = True
                else:
                    tex = False 
                window['-GO-'].update(tex)
                if str(banco.result[9]) == 'sim':
                    tex = True
                else:
                    tex = False 
                window['-OP-'].update(tex)
        if event == '-':
            idinc = values['-Fi-']
            if idinc == '':
                idinc = 1
            idinc = int(idinc) - 1
            if idinc < 1:
                idinc = ult_forn
            id_forn = str(idinc)
            banco.consultar_registro("pagamento", id_forn)
            if (banco.result == None):
                sg.popup('Este ID não existe ', id_forn)
                window['-Fi-'].update(id_forn)
                window['-NE-'].update('')
                window['-DT-'].update('')
                window['-PR-'].update('')
                window['-AP-'].update('')
                window['-VT-'].update('')
                window['-VK-'].update('')
                window['-GO-'].update(False)
                window['-OP-'].update(False)
            else:
                window['-Fi-'].update(str(banco.result[0]))
                window['-NE-'].update((str(banco.result[1]), str(banco.result[2])))
                window['-DT-'].update(str(banco.result[3]))
                window['-PR-'].update(str(banco.result[4]))
                window['-AP-'].update(str(banco.result[5]))
                dia = str(banco.result[6])[-2:]
                window['-VT-'].update(dia)
                window['-VK-'].update(str(banco.result[7]))
                if str(banco.result[8]) == 'sim':
                    tex = True
                else:
                    tex = False 
                window['-GO-'].update(tex)
                if str(banco.result[9]) == 'sim':
                    tex = True
                else:
                    tex = False 
                window['-OP-'].update(tex)
        if event == "Buscar":
            bynome = values['-NE-']
            bymes = values['-PR-']
            byano = values['-AP-']
            if bynome != '' and bymes != '' and byano != '': 
                banco.buscar_registro('pagamento', bynome, bymes, byano)
                if (banco.result == None):
                    sg.popup('Este Pagto. não existe')
                    window['-Fi-'].update('')
                    window['-NE-'].update('')
                    window['-DT-'].update('')
                    window['-PR-'].update('')
                    window['-AP-'].update('')
                    window['-VT-'].update('')
                    window['-VK-'].update('')
                    window['-GO-'].update(False)
                    window['-OP-'].update(False)
                else:
                    window['-Fi-'].update(str(banco.result[0]))
                    window['-NE-'].update((str(banco.result[1]), str(banco.result[2])))
                    window['-DT-'].update(str(banco.result[3]))
                    window['-PR-'].update(str(banco.result[4]))
                    window['-AP-'].update(str(banco.result[5]))
                    dia = str(banco.result[6])[-2:]
                    window['-VT-'].update(dia)
                    window['-VK-'].update(str(banco.result[7]))
                    if str(banco.result[8]) == 'sim':
                        tex = True
                    else:
                        tex = False 
                    window['-GO-'].update(tex)
                    if str(banco.result[9]) == 'sim':
                        tex = True
                    else:
                        tex = False 
                    window['-OP-'].update(tex)
        if event == "Alterar":
            id = values['-Fi-']
            nome = values['-NE-']
            detalhe = values['-DT-']
            mes = values['-PR-']
            ano = values['-AP-']
            dia = values['-VT-']
            vencimento = ano + '-' + mes + '-' + dia
            valor = values['-VK-']
            if values['-GO-'] == True: 
                pex = 'sim'
            else:
                pex = 'nao'
            agendado = pex
            if values['-OP-'] == True: 
                pex = 'sim'
            else:
                pex = 'nao'
            pago = pex
            banco.alterar_pagamento(id, nome, detalhe, mes, ano, vencimento, valor, agendado, pago)
            sg.popup('Registro de Pagamento alterado OK ')
        if event == "Excluir":
            id = values['-Fi-']
            banco.excluir_pagamento(id)
            banco.pega_ultimo("pagamento")
            if banco.result[0] == None:
                ult_forn = 1
            else:
                ult_forn = int(banco.result[0])
            sg.popup('Registro de Pagamento excluido OK ')   
#------------------------------------------------------------------------------------------                        
            
#--------------------------------------------Calcular--------------------------------------
    if window == jan5:
        window['-PR-'].update(int(date.today().month))
        window['-AP-'].update(int(date.today().year))
        if len(prinAnoRef) == 0:
            window['-AP-'].update(int(date.today().year))
        else:    
            window['-AP-'].update(int(prinAnoRef[0]))
        if event == "Calcular":
            banco.pega_ultimo("recebido")
            if banco.result[0] == None:
                ult_forn = 0
            else:
                ult_forn = int(banco.result[0])
            id = str(ult_forn + 1)
            nome = values['-NE-']
            mes = values['-PR-']
            ano = values['-AP-']
            if mes != '' and ano != '': 
                banco.pegaInicial(mes, ano)
                if (banco.result[0] == None):
                    sg.popup('Este Recebimento não existe ')
                    window['-VN-'].update('')
                    window['-DB-'].update('')
                    window['-RS-'].update('')
                else:
                    window['-VN-'].update(str(banco.result[0]))
                    entrada = banco.result[0]
                    banco.somaPagtos(mes,ano)
                    if (banco.result[0] == None):
                        sg.popup('Os Pagamentos ainda não foram definidos')
                        window['-DB-'].update('')
                        window['-RS-'].update('')
                    else:
                        window['-DB-'].update(str(banco.result[0]))
                        saiu = banco.result[0]
                        restou = entrada - saiu
                        window['-RS-'].update(restou)
                        anor = int(ano) 
                        mesr = int(mes) + 1
                        if (mesr > 12):
                            mesr =  1
                            anor =  int(ano) + 1
                        banco.incluir_saldo(id, nome, restou, mesr, anor)
                        sg.popup('Incluido reg Saldo de ' + str(restou) + " para " + str(mesr) + "/" + str(anor))
            else:
                sg.popup('Coloque MES e ANO para selecionar.')
#-------------------------------------------------------------------------------------------

#------------------------------------Gráfico por Conta / ano--------------------------------
    if window == jan9 and event == "Gerar Gráfico":
        if values['-ARr-'] == '':
            ano_atual = date.today().year
        else:    
            ano_atual = str(values['-ARr-'][0])
        ano_anter = int(ano_atual) - 1
        conta = values['-LAR-']
        gerar_pdf.GrafAnalise(conta, ano_atual, ano_anter)        
        pdf_path = dir_path + "grafico-" + str(conta[0]) + ".pdf" 
        abs_pdf_path = os.path.abspath(pdf_path)
        if not os.path.exists(abs_pdf_path):
            sg.popup(f"Erro: Arquivo não encontrado em '{abs_pdf_path}'")
        else:
            try:
                if sys.platform == "win32":
                    os.startfile(abs_pdf_path) 
                elif sys.platform == "darwin": 
                    subprocess.run(['open', abs_pdf_path], check=True)
                else: 
                    subprocess.run(['xdg-open', abs_pdf_path], check=True)
            except FileNotFoundError:
                sg.popup(f"Erro: Comando 'open' (macOS) ou 'xdg-open' (Linux) não encontrado.")
                sg.popup("Verifique se você está em um ambiente gráfico e se o comando está no PATH.")
            except subprocess.CalledProcessError as e:
                sg.popup(f"Erro ao executar o comando para abrir o PDF: {e}")
            except Exception as e:
                sg.popup(f"Ocorreu um erro inesperado: {e}")        

#-------------------------------------------------------------------------------------------

#--------------------------------------Impressão--------------------------------------------
    if window == jan6 and event == "Imprimir":
        mes_r = values['-MRr-']
        ano_r = values['-ARr-']
        if mes_r == '': 
            mes_r =  date.today().month
        if len(ano_r) == 0:
            ano_r = date.today().year
        else:
            ano_r = str(ano_r[0])
        gerar_pdf.LosGraficos(mes_r, ano_r)        
        pdf_path = dir_path + "analise-" + str(mes_r) + str(ano_r) + ".pdf" 
        abs_pdf_path = os.path.abspath(pdf_path)
        if not os.path.exists(abs_pdf_path):
            sg.popup(f"Erro: Arquivo não encontrado em '{abs_pdf_path}'")
        else:
            try:
                if sys.platform == "win32":
                    os.startfile(abs_pdf_path) 
                elif sys.platform == "darwin": 
                    subprocess.run(['open', abs_pdf_path], check=True)
                else: 
                    subprocess.run(['xdg-open', abs_pdf_path], check=True)
            except FileNotFoundError:
                sg.popup(f"Erro: Comando 'open' (macOS) ou 'xdg-open' (Linux) não encontrado.")
                sg.popup("Verifique se você está em um ambiente gráfico e se o comando está no PATH.")
            except subprocess.CalledProcessError as e:
                sg.popup(f"Erro ao executar o comando para abrir o PDF: {e}")
            except Exception as e:
                sg.popup(f"Ocorreu um erro inesperado: {e}")

    if window == jan7 and event == "Imprimir":
        ano_r = values['-ARr-']
        if len(ano_r) == 0:
            ano_r = date.today().year
        else:
            ano_r = str(ano_r[0])
        gerar_pdf.PlotGraf(ano_r)        
        pdf_path = dir_path + "grafico-" + str(ano_r) + ".pdf"     #  + mes_r
        abs_pdf_path = os.path.abspath(pdf_path)
        if not os.path.exists(abs_pdf_path):
            sg.popup(f"Erro: Arquivo não encontrado em '{abs_pdf_path}'")
        else:
            try:
                if sys.platform == "win32":
                    os.startfile(abs_pdf_path) 
                elif sys.platform == "darwin": 
                    subprocess.run(['open', abs_pdf_path], check=True)
                else: 
                    subprocess.run(['xdg-open', abs_pdf_path], check=True)
            except FileNotFoundError:
                sg.popup(f"Erro: Comando 'open' (macOS) ou 'xdg-open' (Linux) não encontrado.")
                sg.popup("Verifique se você está em um ambiente gráfico e se o comando está no PATH.")
            except subprocess.CalledProcessError as e:
                sg.popup(f"Erro ao executar o comando para abrir o PDF: {e}")
            except Exception as e:
                sg.popup(f"Ocorreu um erro inesperado: {e}")                
#-------------------------------------------------------------------------------------------
#----------------------------------------------------define os padroes---------------------
    if window == jan8 and event == "Gravar":
        conta_salario = values['-LAR-']
        conta_saldo = values['-LDO-']
        retcode = banco.gravar_padrao(conta_salario, conta_saldo)
        sg.popup("Padrões gravados OK.")
        jan8.hide()

