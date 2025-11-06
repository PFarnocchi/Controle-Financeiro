import sqlite3
from datetime import date
import json
import os
import platform

class ConectarDB:
    def checkSys(self):
        return platform.system() 

    def inicia_banco(self):
        sysop = self.checkSys()
        #print("*** Usando em " + sysop + " ***")
        if sysop == "Linux":
            c_barra = os.path.expanduser('~')
            a_bar = '/'
        else:
            c_barra = "C:" 
            a_bar = '\\'  
        local_db = c_barra + a_bar + "finplan"  + a_bar + "db_finplan"
        self.con = sqlite3.connect(local_db + a_bar + 'db.sqlite3')
        #print("*** Banco de Dados em " + local_db + " ***")
        self.cur = self.con.cursor() 
        base = self.cap_loc("base")
        if base == "not":
            self.criar_tabelas()
            self.carga_ini()

    def criar_tabelas(self):
        try:
            self.cur.execute('''CREATE TABLE IF NOT EXISTS contas (
                id INTEGER,
                tipo TEXT,
                nome TEXT,
                descricao TEXT,
                ativo INTEGER)''')
            self.cur.execute('''CREATE TABLE IF NOT EXISTS pagamento (
                id INTEGER,
                id_conta INTEGER,
                nome TEXT,
                detalhe TEXT,
                mes_ref INTEGER,
                ano_ref INTEGER,
                vencimento DATE,
                valor DECIMAL,
                agendado TEXT,
                pago TEXT)''')
            self.cur.execute('''CREATE TABLE IF NOT EXISTS ponto_ini (
                id INTEGER,
                nome TEXT,
                diretorio TEXT)''')
            self.cur.execute('''CREATE TABLE IF NOT EXISTS config (
                id INTEGER,
                nome TEXT,
                id_conta INTEGER)''')
            self.cur.execute('''CREATE TABLE IF NOT EXISTS recebido (
                id INTEGER,
                id_conta INTEGER,
                nome TEXT,
                detalhe TEXT,
                mes_ref INTEGER,
                ano_ref INTEGER,
                recebimento DATE,
                valor DECIMAL,
                pagar DECIMAL,
                restou DECIMAL)''')
        except Exception as e:
            ret = (f'[x] Falha ao criar tabelas [x]: {e}')
        else:
            ret = ('[!] Tabelas criadas com sucesso [!]\n')
        return ret
    
    def carga_ini(self):
        sysop = self.checkSys()
        if sysop == "Linux":
            c_barra = os.path.expanduser('~')
            a_bar = '/'
        else:
            c_barra = "C:" 
            a_bar = '\\'        
        raiz =  c_barra
        local_db = a_bar + "finplan" + a_bar + "db_finplan"
        local_imag = a_bar + "finplan" + a_bar + "images"
        local_file = a_bar + "finplan" + a_bar + "files"
        query =  "INSERT INTO ponto_ini VALUES (1,'raiz', '" + raiz + "')"
        ret = self.db_exec(query)
        query =  "INSERT INTO ponto_ini VALUES (2,'base', '" + local_db + a_bar + "')"
        ret = self.db_exec(query)
        query =  "INSERT INTO ponto_ini VALUES (3,'dirpdf', '" + local_file + a_bar + "')"
        ret = self.db_exec(query)
        query =  "INSERT INTO ponto_ini VALUES (4,'chart', '" + local_file + a_bar + "')"
        ret = self.db_exec(query)
        query =  "INSERT INTO ponto_ini VALUES (5,'chartfin', '" + local_file + a_bar + "')"
        ret = self.db_exec(query)
        query =  "INSERT INTO ponto_ini VALUES (6,'images', '" + local_imag + a_bar + "')"
        ret = self.db_exec(query)
        return

    def fecha_db(self):
        self.con.close()        

#----------------------------------------------------------------------------------------
    def db_exec(self, query):
        try:
            self.cur.execute(query)
            self.con.commit()
            mensa = "OK"
        except Exception as err:
            mensa = "Erro" + str(err)
        return mensa 

    def db_read_all(self, query):
        try:
            self.cur.execute(query)
            result = self.cur.fetchall()        
        except Exception as err:
            print("Erro " + query + "  -  " + str(err))
            result = None
        return result

    def db_read(self, query):
        try:
            self.cur.execute(query)
            result = self.cur.fetchone()        
        except Exception as err:
            result = None
        return result

    def all_Meses(self):
        self.result = ['01','02','03','04','05','06','07','08','09','10','11','12']
        return self.result

    def all_Anos(self):
        try:
            sql = "SELECT distinct ano_ref from recebido order by ano_ref" 
            self.cur.execute(sql)
            self.result = self.cur.fetchall()
        except Exception as err:
            self.result =  str(date.today().year)
        return self.result

    def consultar_registro(self, tabela, id):
        sql = "SELECT * from " + tabela + " WHERE id = " + id
        self.cur.execute(sql)
        self.result = self.cur.fetchone()
        return self.result
    
    def buscar_registro(self, tabela, nome, bymes, byano):
        sql = "SELECT * from " + tabela + " WHERE nome = '" + str(nome[1]) + "' and mes_ref = " + bymes + " and ano_ref = " + byano
        self.cur.execute(sql)
        self.result = self.cur.fetchone()
        return self.result    

    def pega_ultimo(self, tabela):
        sql = "SELECT max(id) from " + tabela
        self.cur.execute(sql)
        self.result = self.cur.fetchone()
        return self.result

    def all_Contas(self, tipo):
        if tipo == 'A':
            sql =  "SELECT id, nome, tipo from contas where ativo = 1"
        else:    
            sql = "SELECT id, nome from contas where ativo = 1 and tipo = '" + tipo + "'"
        self.cur.execute(sql)
        self.result = self.cur.fetchall()
        return self.result
    
    def cap_AnoRef(self):
        sql = "SELECT distinct ano_ref from recebido"
        self.cur.execute(sql)
        self.result = self.cur.fetchall()
        return self.result
    
    def cap_loc(self, local):
        try:
            sql = "SELECT diretorio from ponto_ini where nome = '" + local + "'"
            self.cur.execute(sql)
            self.result = self.cur.fetchone()
        except Exception as err:    
            self.result = 'not'
            return self.result
        if self.result == None:
            self.result = 'not'
            return self.result
        return self.result[0]

    def pegaInicial(self, mes, ano):
        try:
            sql = "SELECT sum(valor) from recebido WHERE mes_ref = " + mes + " and ano_ref = " + ano
            self.cur.execute(sql)
            self.result = self.cur.fetchone()
        except Exception as err:    
            self.result = None  
        return self.result        
    
    def somaPagtos(self, mes, ano):
        try:
            sql = "SELECT sum(valor) as valor from pagamento WHERE mes_ref = " + mes + " and ano_ref = " + ano
            self.cur.execute(sql)
            self.result = self.cur.fetchone()
        except Exception as err:    
            self.result = None
        return self.result        
#-------------------------------------------Definição de padrões-------------------------
    def ctpadrao(self):
        sql = "SELECT * from config"      # [0] id  [1] nome  [2] id_conta
        rec = self.db_read_all(sql)
        chave_rec = 0
        chave_sld = 0
        if  rec != None:     
            for row in rec:
                if row[1] == "Recebido":
                    chave_rec =  row[2]
                if row[1] == "Saldo":
                    chave_sld = row[2]                  
        json_string = '{"chave_rec": "' + str(chave_rec) + '", "chave_sld": "' + str(chave_sld) + '"}'
        stringval = json.loads(json_string) 
        return stringval  
    
    def gravar_padrao(self, conta_salario, conta_saldo):
        self.procura_padrao(conta_salario)
        self.insere_padrao(conta_salario, "Recebido")
        self.procura_padrao(conta_saldo)
        self.insere_padrao(conta_saldo, "Saldo")
        return "OK"

    def insere_padrao(self, conta, chave):  
        self.pega_ultimo("config")
        if self.result[0] == None:
            pad_id = 1
        else:
            pad_id = int(self.result[0] + 1)          
        try:
            sql = "INSERT INTO config (id, nome, id_conta) VALUES(" \
                    + str(pad_id) + ", '" + chave + "', '" + str(conta[0]) + "')"
            self.cur.execute(sql)
        except Exception as e:
            self.con.rollback()
        else:
            self.con.commit()
        return "OK"    

    def procura_padrao(self, conta):
        try:
            sql = "SELECT nome from config where id_conta = " + str(conta[0]) 
            self.cur.execute(sql)
            self.result = self.cur.fetchone()
            if self.result != None:
                sql = "DELETE from config WHERE id_conta = " + str(conta[0]) 
                self.cur.execute(sql)
        except Exception as e:
            print("Erro " + str(e))
            self.con.rollback()
        else:
            self.con.commit()
        return "OK"
    
#------------------------------ Tabela Recebido ----------------------------------------
    def inserir_recebimento(self, id, nome, detalhe, mes, ano, data, valor):
        try:
            sql = "INSERT INTO recebido (id, id_conta, nome, detalhe, mes_ref, ano_ref, recebimento, valor, pagar, restou) VALUES(" \
                        + id + ", "  + str(nome[0]) + ", '" + str(nome[1]) + "','" + detalhe + "', "  + mes + ", " + ano + ", '" + data +  "', " + valor + ", 0, 0)"
            self.cur.execute(sql)
        except Exception as e:
            self.con.rollback()
        else:
            self.con.commit()

    def alterar_recebimento(self, id, nome, detalhe, mes, ano, data, valor):
        try:
            sql = "UPDATE recebido SET id_conta = " + str(nome[0]) +  \
                  ",  nome = '" + str(nome[1]) +  \
                  "',  detalhe = '" + detalhe + \
                  "', mes_ref = " + mes + ", ano_ref = " + ano + ", recebimento = '" + \
                  data + "', valor = " + valor + \
                  " WHERE id = " + id
            self.cur.execute(sql)
        except Exception as e:
            self.con.rollback()
        else:
            self.con.commit()

    def excluir_recebimento(self, id):
        try:
            sql = "DELETE from recebido WHERE id = " + id
            self.cur.execute(sql)
        except Exception as e:
            self.con.rollback()
        else:
            self.con.commit()
#---------------------------------------------------------------------------------------
#------------------------------ Tabela Contas ----------------------------------------
    def inserir_conta(self, id, tipo, nome, descricao, ativo):
        try:
            sql = "INSERT INTO contas (id, tipo, nome, descricao, ativo) VALUES(" \
                        + id + ",'" + tipo + "', '" + nome + "', '" + descricao + "', " + ativo + ")"
            self.cur.execute(sql)
        except Exception as e:
            self.con.rollback()
        else:
            self.con.commit()

    def alterar_conta(self, id, tipo, nome, descricao, ativo):
        try:
            sql = "UPDATE contas SET tipo = '" + tipo + "', nome = '" + nome + \
                  "', descricao = '" + descricao + "', ativo = " + ativo + " WHERE id = " + id
            self.cur.execute(sql)
        except Exception as e:
            self.con.rollback()
        else:
            self.con.commit()

    def excluir_conta(self, id):
        try:
            sql = "DELETE from contas WHERE id = " + id
            self.cur.execute(sql)
            sql = "DELETE from config where id_conta = " + id 
            self.cur.execute(sql)
        except Exception as e:
            self.con.rollback()
        else:
            self.con.commit()
#---------------------------------------------------------------------------------------    
#------------------------------ Tabela Pagamentos ----------------------------------------
    def inserir_pagamento(self, id, nome, detalhe, mes, ano, vencimento, valor, agendado, pago):
        try:
            sql = "INSERT INTO pagamento (id, id_conta, nome, detalhe, mes_ref, ano_ref, vencimento, valor, agendado, pago) VALUES(" \
                        + id + ", " + str(nome[0]) + ", '" + str(nome[1]) + "','" + detalhe + "', " + mes + ", " + ano + ", '" + vencimento + "', " + valor \
                            + ", '" + agendado + "', '" + pago + "')"
            self.cur.execute(sql)
        except Exception as e:
            self.con.rollback()
        else:
            self.con.commit()

    def alterar_pagamento(self, id, nome, detalhe, mes, ano, vencimento, valor, agendado, pago):
        try:
            sql = "UPDATE pagamento SET id_conta = " + str(nome[0]) +  \
                                ",  nome = '" + str(nome[1]) +  \
                                "', detalhe = '" + detalhe + \
                                "', mes_ref = " + mes + \
                                ", ano_ref = " + ano + \
                                ", vencimento = '" + vencimento + \
                                "', valor = " + valor + \
                                ", agendado = '" + agendado + \
                                "', pago = '" + pago + \
                                "' WHERE id = " + id
            self.cur.execute(sql)
        except Exception as e:
            self.con.rollback()
        else:
            self.con.commit()

    def excluir_pagamento(self, id):
        try:
            sql = "DELETE from pagamento WHERE id = " + id
            self.cur.execute(sql)
        except Exception as e:
            self.con.rollback()
        else:
            self.con.commit()
#---------------------------------------------------------------------------------------    

#------------------------------------------Saldo para o proximo mes---------------------
    def incluir_saldo(self, id, nome, restou, mesr, anor):
        data = str(anor) + '-' + str(mesr) + '-01'
        try:
            sql = "SELECT id from recebido WHERE id_conta = " + str(nome[0]) + \
               " and  mes_ref = " + str(mesr) + " and ano_ref = " + str(anor)
            rec = self.db_read(sql)
            if  rec == None:
                sql = "INSERT INTO recebido (id, id_conta, nome, mes_ref, ano_ref, recebimento, valor, pagar, restou) VALUES(" \
                    + str(id) + ", " + str(nome[0]) + ", '" + str(nome[1]) + "'," + str(mesr) + ", " + str(anor) + ", '" + str(data) +  "', " + str(restou) + ", 0, 0)"              
            else:
                id = int(rec[0])
                sql = "UPDATE recebido set valor = " + str(restou) + " WHERE id = " + str(id)            
            self.cur.execute(sql)
        except Exception as e:
            self.con.rollback()
        else:
            self.con.commit()
#---------------------------------------------------------------------------------------                    

    def gerar_cards(self, mesr, anor):
        stringval = self.ctpadrao()
        conta_recebido = stringval['chave_rec']
        conta_saldo = stringval['chave_sld']
        query = "select valor, id_conta from recebido where mes_ref = " + str(mesr) + \
             " and  ano_ref = " + str(anor)
        rec = self.db_read_all(query)
        if  rec != None:     
            valor_t_rec = 0
            valor_sld = 0
            valor_inss = 0
            valor_transf = 0
            valor_t_caixa = 0
            valor_t_pend = 0
            for row in rec:
                valor_t_rec = valor_t_rec + row[0]
                if row[1] == int(conta_saldo):                                         
                    valor_sld = valor_sld + row[0] 
                else: 
                    if row[1] == int(conta_recebido):                                   
                        valor_inss = valor_inss + row[0]
                    else:
                        valor_transf = valor_transf + row[0] 
        query = "select sum(valor) as valor from pagamento where mes_ref = " + str(mesr) + \
                " and  ano_ref = " + str(anor) + " and pago = 'sim'"
        rec = self.db_read(query)   
        if rec[0] != None:  
            valor_t_pag =  rec[0]
        else:
            valor_t_pag = 0
        query = "select sum(valor) as valor from pagamento where mes_ref = " + str(mesr) + \
                " and  ano_ref = " + str(anor) + " and pago = 'nao'"; 
        rec = self.db_read(query)   
        if rec[0] != None:  
             valor_t_pend =  rec[0]       
        valor_t_caixa =  valor_t_rec -  valor_t_pag
        valor_prev_cx =  valor_t_caixa -  valor_t_pend
        sinal_rest = "(+)"
        if valor_t_caixa <  valor_t_pend:
            sinal_rest = "(-)"
        json_string = '{"rec": "' + str(valor_t_rec) + '", "sld": "' + str(valor_sld) + '", "inss": "' + str(valor_inss) + \
                '", "transf": "' +  str(valor_transf) + '", "tpag": "' + str(valor_t_pag) + '", "sinrest": "' + sinal_rest + \
                '", "rest": "' + str(valor_t_caixa) + '", "prev": "' + str(valor_prev_cx) + '", "pend": "' +  str(valor_t_pend) + '"}'
        stringval = json.loads(json_string)        
        return stringval