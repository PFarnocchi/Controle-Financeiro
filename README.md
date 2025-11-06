# Controle-Financeiro-
Para acompanhar os gastos domésticos.


 use Python 3.12.3
 
 Livre para usar/alterar/modificar    :)
 
 não contém componentes pagos (all free) 
 

---------------------------------------------------------------------------------------------------------------
  Instalar o virtual environment
                                       python -m venv .venv
                                       source .venv/bin/activate   (Linux)
                                       C:\Pasta_Projeto\fin_control>venv\scripts\activate (Windows) 
                                       
                                       Após ativar o Venv:
                                                            pip install requirements.txt
                                                            
                                       deactivate           (desativa o virtual environment)  

  Recomensável instalar o DB browser for SQLite. 
  
                                       sudo snap install sqlitebrowser-casept    OU
                                       sudo apt install sqlitebrowser          (no Linux)
                                       Baixar o instalador em sqlitebrowser.org e executar o .msi (windows)

  Para Compilar         pyinstaller -F -w finplan.py --hidden-import='PIL._tkinter_finder'   (Linux)
                        pyinstaller -F -w finplan.py                                         (Windows)

  Autor:  Paulo Farnocchi     Data: 2024      Local: Maringá - Paraná                
---------------------------------------------------------------------------------------------------------------

Aplicativo construido para controlar minhas contas e mostrar evolução salarial e gastos.
Não tem pretensão de ser um Controle Financeiro, servindo simplesmente como um histórico
comparativo.
Futuramente pretendo substituir as contas por um Plano de Contas escalonado em níveis, bem 
como adicionar módulos de previsão orçamentária.   

Definições:
    Tela Menu:
        Contas - Abre a Tela de Contas (inclusão, alteração, exclusão)
                 Solicita Padrões de contas "Salário" e  "Saldo" para fins de 
                 emissão do relatório apenas. A conta Saldo habilita o valor 
                 restante para o próximo mes ao proceder com "Calcular" (Fecha Mes).
                 
        Recebimento - Abre a Tela de valores a receber (inclusão, alteração, exclusão).
                      Botões "+", "-" e "Buscar" navega as contas existentes.    

        Pagamentos  - Abre a Tela de valores a pagar (inclusão, alteração, exclusão).
                      Botões "+", "-" e "Buscar" navega as contas existentes.    

        Calcular - Possibilita o fechamento do Mes e prepara para o subsequente.

        Mostra Gráfico - Abre a Tela para seleção de Ano e apresenta um gráfico simples
                         contendo a somatória de valores recebidos e pagos. 

        Imprimir - Abre a Tela de seleção de MES e ANO e apresenta um relatório com o 
                   espelhamento da posição no momento, podendo ser parcial ou total, conforme
                   o mes, caso em aberto ou fechado.

        Sair - Fecha a Tela Menu. 

        Gráfico por Conta - Abre a Tela de seleção de CONTA e ANO (*) e mostra a evolução 
                            em valores nos meses.
                            (*) Se não for informado será usado o ano corrente 

                            O grafico mostra um comparativo entre o ano (*) e ano -1
                            se houver, não havendo mostrará valor 0.  

Obs: Na primeira rodada o programa irá criar e Pré-montar o banco de dados SQLite.
     Caso não seja criado devido a definições de permissão ou outro problema, copie 
     o arquivo db.sqlite3 no diretório correspondente e dê permissão 755 ou 777, observando
     regras de segurança.    

Estrutura dos diretórios:

    Linux:
        ~/finplan
            /db_finplan
                db.sqlite3                     banco de dados
            /files
                template_base.png              template para construção do relatório
                template_plot.png              template para construção dos gráficos 
            /images
                pitoko_w.png                   logo (Este é meu gato preto, o Pytoko) 
            finplan                            programa 

    Windows:
        C:\finplan
            \db_finplan
                db.sqlite3                     banco de dados
            \files
                template_base.png              template para construção do relatório
                template_plot.png              template para construção dos gráficos 
            \images
                pitoko_w.png                   logo (Este é meu gato preto, o Pytoko) 
            finplan.exe                            programa             
