
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A3
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
import dbsqlite
import numpy as np

class LosPdfs:

    def LosGraficos(self, mes_r, ano_r):
        banco = dbsqlite.ConectarDB()
        rtcode = banco.inicia_banco()
        raiz_dir = banco.cap_loc('raiz')
        dir_path = banco.cap_loc('dirpdf')
        dir_path = raiz_dir + dir_path        
        stringval = banco.gerar_cards(mes_r, ano_r)
        recebido = stringval['rec']
        saldo = stringval['sld']
        salario = stringval['inss']
        transfer = stringval['transf']
        pagos = stringval['tpag']
        sinal = stringval['sinrest']
        restam = stringval['rest']
        prev = stringval['prev']
        pend = stringval['pend']
        #-------------------------------------------------------------------------Template-----------------
        w, h =  A3
        c = canvas.Canvas(dir_path + "analise-" + str(mes_r) + str(ano_r) + ".pdf", pagesize=A3)
        img = ImageReader(dir_path + "template_base.png")                     
        img_w, img_h = img.getSize()
        query = "SELECT  sum(valor) from recebido where ano_ref = " + str(ano_r) + " and mes_ref = " + str(mes_r)
        rec = banco.db_read(query)
        if (rec[0] == None):
            valor_receb = "0.00"
            valor_saldo = "0.00"
        else:    
            valor_receb = str(rec[0])
            valor_saldo = rec[0]
        banco.somaPagtos(mes_r, ano_r) 
        if banco.result != None:
            if banco.result[0] == None:
                valor_pagto = "0.00"
            else:
                valor_pagto = str(banco.result[0])       
                valor_saldo = str(valor_saldo - banco.result[0])
        else:
            valor_pagto = "0.00"        
        c.drawImage(img, 90, h - img_h)
        c.drawString(90+60, 1050, str(mes_r) + "/" + str(ano_r))
        c.drawString(90+60, 1005, "R${:,.2f}".format(float(valor_receb)))
        c.drawString(90+60, 960, "R${:,.2f}".format(float(valor_pagto)))
        c.drawString(90+60, 920, "R${:,.2f}".format(float(valor_saldo)))
        c.drawString(90+200, 1050, "    Recebido       ")  
        c.drawString(90+200, 1030, "Saldo Anterior: ")
        c.drawString(90+200, 1010, "Receb.Mes:      ")
        c.drawString(90+200, 990,  "Valor Transfer: ")
        c.drawString(90+300, 1030, "R${:,.2f}".format(float(saldo)))
        c.drawString(90+300, 1010, "R${:,.2f}".format(float(salario)))
        c.drawString(90+300, 990,  "R${:,.2f}".format(float(transfer)))
        c.drawString(90+400, 1050, "Pagamentos:        ")  
        c.drawString(90+400, 1030, "Pendentes:         ") 
        c.drawString(90+400, 1010, "Caixa:             ") 
        c.drawString(90+400, 990,  "Após pg. pend.:    ")  
        c.drawString(90+500, 1050, "R${:,.2f}".format(float(pagos)))  
        c.drawString(90+500, 1030, "R${:,.2f}".format(float(pend))) 
        c.drawString(90+500, 1010, "R${:,.2f}".format(float(restam))) 
        c.drawString(90+500, 990,  sinal + "R${:,.2f}".format(float(prev)))  
        c.drawString(90+30, 885, 'Contas sem agenda')
        query = "select id, nome, descricao from contas where ativo = 1 and tipo = 'D' " 
        rows = banco.db_read_all(query)
        lim = 865
        for row in rows:  
            id_c = str(row[0])
            nome_c = row[1] 
            query = "select id from pagamento where id_conta = " + id_c + " and mes_ref = " + str(mes_r) + " and  ano_ref = " + str(ano_r)
            excl = banco.db_read(query)
            if excl == None:
                c.drawString(90+20, lim, nome_c)
                lim = lim - 20               
        lim = 865
        query = "select * from pagamento where mes_ref = " + str(mes_r) + " and  ano_ref = " + str(ano_r) + " order by vencimento"
        rows = banco.db_read_all(query)
        for row in rows:  
            #
            #  0-id 1-id_conta 2-nome 3-detalhe 4-mes_ref 
            #  5-ano_ref 6-vencimento 7-valor 8-agendado 9-pago 
            #            
            nome = row[2] 
            vencimento = str(row[6])
            valor = str(row[7])
            agendado = row[8]
            pago = row[9]
            c.drawString(90+200, lim, nome)
            c.drawString(90+300, lim, vencimento)
            c.drawString(90+390, lim, "R${:,.2f}".format(float(valor)))
            c.drawString(90+500, lim, agendado)
            c.drawString(90+600, lim, pago)
            lim = lim - 20
        c.showPage()
        c.save()
        banco.fecha_db()

    def PlotGraf (self, ano_r):                               
        banco = dbsqlite.ConectarDB()
        rtcode = banco.inicia_banco() 
        raiz_dir = banco.cap_loc('raiz')
        dir_path = banco.cap_loc('dirpdf')
        dir_path = raiz_dir + dir_path
        #-----------------------------------------------------------------Template-----------------
        w, h =  A3
        c = canvas.Canvas(dir_path + "grafico-" + str(ano_r) + ".pdf", pagesize=A3)  #   + mes_r
        img = ImageReader(dir_path + "template_plot.png")                     
        img_w, img_h = img.getSize()
        c.drawImage(img, 90, h - img_h)
        fig_file = dir_path + "graf.png"
        fig_file_r = dir_path + "graf_rec.png"
        meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        valrec =  self.plota_grf('R', ano_r)   
        valpag =  self.plota_grf('P', ano_r)  
#--------------------------------------------------------bar graf--------------------------        
        x = np.arange(len(meses)) 
        largura = 0.35 
        fig, ax = plt.subplots()
        ret1 = ax.bar(x - largura/2, valrec, largura, label='Rec.')
        ret2 = ax.bar(x + largura/2, valpag, largura, label='Pag.')

        def adicionar_valor_barra(rects):
            for rect in rects:
                altura = rect.get_height() 
                ax.annotate(f'{altura}', 
                            xy=(rect.get_x() + rect.get_width() / 2, altura), 
                            xytext=(0, 3),  
                            textcoords="offset points",
                            ha='center', va='bottom',
                            fontsize=6) 

        adicionar_valor_barra(ret1)
        adicionar_valor_barra(ret2)
        ax.set_ylabel('Valores')
        ax.set_title(ano_r)
        ax.set_xticks(x)
        ax.set_xticklabels(meses)
        ax.legend()
        plt.savefig(fig_file, bbox_inches='tight', pad_inches=0.1)
#------------------------------------------------------------Line graf------------------------
        plt.figure(figsize=(6, 4))
        plt.plot(meses, valrec, marker='o', linestyle='-', label='Rec.')
        for i, (xi, yi) in enumerate(zip(meses, valrec)):
            plt.annotate(f'{yi}', (xi, yi), 
                         textcoords="offset points", 
                         xytext=(0, 10), ha='center', fontsize=6)
        plt.plot(meses, valpag, marker='o', linestyle='-', label='Pag.')
        for i, (xi, yi) in enumerate(zip(meses, valpag)):
            plt.annotate(f'{yi}', (xi, yi), 
                         textcoords="offset points", 
                         xytext=(0, 10), ha='center', fontsize=6)
        plt.title('')
        plt.xlabel('')
        plt.ylabel('Valores')
        plt.grid(True)
        plt.legend()
        plt.savefig(fig_file_r, bbox_inches='tight', pad_inches=0.1)
#-----------------------------------------------------------------------------------------------
        graf = ImageReader(dir_path + "graf.png") 
        grf_w, grf_h = graf.getSize()
        c.drawImage(graf, 60+30, 1050 - grf_h)
        graf = ImageReader(dir_path + "graf_rec.png") 
        grf_w, grf_h = graf.getSize()
        c.drawImage(graf, 60+30, 500 - grf_h)
        c.showPage()
        c.save()
        banco.fecha_db()

    def plota_grf(self, tp, ano_r):                  
        banco = dbsqlite.ConectarDB()   
        rtcode = banco.inicia_banco()        
        stringval = banco.ctpadrao()
        conta_recebido = stringval['chave_rec']
        conta_saldo = stringval['chave_sld']  
        mes = 1
        grfRet = []
        while mes < 13:
            if tp == "R":
                sql = "SELECT mes_ref, sum(valor) from recebido where " \
                 + " mes_ref = " + str(mes) + " and ano_ref = " + str(ano_r)        
            if tp == "P":    
                sql = "SELECT mes_ref, sum(valor) as val from pagamento where ano_ref = "  \
                    + str(ano_r) + " and mes_ref = " + str(mes)
            row = banco.db_read(sql)
            if row != None:
                tmes = row[0]
                if tmes != None:
                    grfRet.append(int(row[1]))     
                else:
                    grfRet.append(0)     
            else:
                grfRet.append(0)     
            mes = mes + 1
        return grfRet     

    def GrafAnalise(self, conta, ano_atual, ano_anter):
        banco = dbsqlite.ConectarDB()
        rtcode = banco.inicia_banco()
        raiz_dir = banco.cap_loc('raiz')
        dir_path = banco.cap_loc('dirpdf')
        dir_path = raiz_dir + dir_path
        #-----------------------------------------------------------------Template-----------------
        w, h =  A3
        c = canvas.Canvas(dir_path + "grafico-" + str(conta[0]) + ".pdf", pagesize=A3)  
        img = ImageReader(dir_path + "template_plot.png")                     
        img_w, img_h = img.getSize()
        c.drawImage(img, 90, h - img_h)
        fig_file_r = dir_path + "graf_anl.png"
        meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        valrec =  self.plota_anl(conta[0], conta[2], ano_atual)   
        valpag =  self.plota_anl(conta[0], conta[2], ano_anter)  
#------------------------------------------------------------Line graf------------------------
        plt.figure(figsize=(6, 4))
        plt.plot(meses, valrec, marker='o', linestyle='-', label=ano_atual)
        for i, (xi, yi) in enumerate(zip(meses, valrec)):
            plt.annotate(f'{yi}', (xi, yi), 
                         textcoords="offset points", 
                         xytext=(0, 10), ha='center', fontsize=6)
        plt.plot(meses, valpag, marker='o', linestyle='-', label=ano_anter)
        for i, (xi, yi) in enumerate(zip(meses, valpag)):
            plt.annotate(f'{yi}', (xi, yi), 
                         textcoords="offset points", 
                         xytext=(0, 10), ha='center', fontsize=6)
        plt.title('')
        plt.xlabel('')
        plt.ylabel('Conta: ' + str(conta[0]) + ' - ' + str(conta[1]))
        plt.grid(True)
        plt.legend()
        plt.savefig(fig_file_r, bbox_inches='tight', pad_inches=0.1)
#-----------------------------------------------------------------------------------------------
        graf = ImageReader(dir_path + "graf_anl.png") 
        grf_w, grf_h = graf.getSize()
        c.drawImage(graf, 60+30, 1050 - grf_h)
        c.showPage()
        c.save()
        banco.fecha_db()   
    
    def plota_anl(self, conta, tipo, ano_r):                  
        banco = dbsqlite.ConectarDB()   
        rtcode = banco.inicia_banco()        
        mes = 1
        grfRet = []
        while mes < 13:
            if tipo == "D":
                sql = "SELECT mes_ref, sum(valor) from pagamento where id_conta = " + str(conta) +  \
                     " and mes_ref = " + str(mes) + " and ano_ref = " + str(ano_r)        
            else:    
                sql = "SELECT mes_ref, sum(valor) from recebido where id_conta = " + str(conta) +  \
                     " and mes_ref = " + str(mes) + " and ano_ref = " + str(ano_r)        
            row = banco.db_read(sql)
            if row != None:
                tmes = row[0]
                if tmes != None:
                    grfRet.append(int(row[1]))     
                else:
                    grfRet.append(0)     
            else:
                grfRet.append(0)     
            mes = mes + 1
        return grfRet     
