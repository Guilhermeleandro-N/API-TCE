from fastapi import FastAPI
import requests
app=FastAPI(
    title="API TCE",
    description="Informações dos municipios e suas contas bancárias",   
)
    
#retorna nome e código de todos os municipios sem qualquer parâmetro
@app.get("/",tags=["Informações dos munícipios"])
def Retorna_o_nome_e_codigo_de_todos_os_municipios():
    dados=requests.get("https://api-dados-abertos.tce.ce.gov.br/municipios")
    dados=dados.json()
    dicionarios_municipios={"dados":[]}
    for c in range(len(dados["data"])):
        nome_municipio=dados["data"][c]["nome_municipio"]
        codigo_municipio=dados["data"][c]["codigo_municipio"]
        dicionario={
        "nome_municipio":nome_municipio,
        "codigo_municipio":codigo_municipio
        }
        dicionarios_municipios["dados"].append(dicionario)
    return dicionarios_municipios

#Retorna nome e código de um município específico usando o codigo deste como parâmetro
@app.get("/codigo_do_municipio={codigo}", tags=["Informações dos munícipios"])
def Retorna_o_nome_do_municipio_usando_o_codigo(codigo):
    dados=requests.get("https://api-dados-abertos.tce.ce.gov.br/municipios")
    dados=dados.json()
    dicionarios_municipio={"dados":[]}
    boleano=False
    for c in range(len(dados["data"])):  
        if dados["data"][c]["codigo_municipio"]==codigo:
            dicionario={
            "nome_municipio":dados["data"][c]["nome_municipio"],
            "codigo_municipio":dados["data"][c]["codigo_municipio"]
            }
            dicionarios_municipio["dados"].append(dicionario)
            boleano=True
    if boleano:
        return dicionarios_municipio
    else:
        return "Cidade não encontrada"
#Retorna nome e código de um município específico usando o nome deste como parâmetro
@app.get("/nome_do_municipio={nome}", tags=["Informações dos munícipios"])
def retorna_o_codigo_do_municipio_usando_o_nome(nome):
    dados=requests.get("https://api-dados-abertos.tce.ce.gov.br/municipios")
    dados=dados.json()
    dicionarios_municipio={"dados":[]}
    boleano=False
    for c in range(len(dados["data"])):  
        if dados["data"][c]["nome_municipio"]==nome.upper():
            dicionario={
            "nome_municipio":dados["data"][c]["nome_municipio"],
            "codigo_municipio":dados["data"][c]["codigo_municipio"]
            }
            dicionarios_municipio["dados"].append(dicionario)
            boleano=True
    if boleano:
        return dicionarios_municipio
    else:
        return "Cidade não encontrada"
    

#retorna informações de contas bancarias como mes e valor de abertura, usa-se o código do município e ano como parâmetros
@app.get("/codigo_municipio={codigo_municipio}&ano={ano_exercicio}",tags=["Informações bancárias"], description="Adicione “00” ao final do ano(2007 a 2024). Exemplo: 2010 → 201000.")
def retorna_informaçoes_bancarias_de_municipios(codigo_municipio ,ano_exercicio):
    meses = {
    1: "Janeiro",2: "Fevereiro",3: "Março",4: "Abril",5: "Maio",6: "Junho",7: "Julho",8: "Agosto",9: "Setembro",10: "Outubro",11: "Novembro",12: "Dezembro"
    }
    nome_municipio=Retorna_o_nome_do_municipio_usando_o_codigo(codigo_municipio)["dados"][0]["nome_municipio"]
    dados=requests.get(f"https://api-dados-abertos.tce.ce.gov.br/contas_bancarias?codigo_municipio={codigo_municipio}&exercicio_orcamento={ano_exercicio}")
    dados=dados.json()
    retorno={"dados":[]}
    for c in range(len(dados["data"])):
        #o ano e mes vem no formato 202402, ano = 2024 e mes= 02.
        if dados["data"][c]["data_referencia"]%100 >= 1 and dados["data"][c]["data_referencia"]%100<=12:
            mes_abertura = meses[dados["data"][c]["data_referencia"]%100]
        else:
            mes_abertura = "Mês inválido"
        novo_dicionario={
            "nome_municipio":nome_municipio,
            "codigo_municipio":dados["data"][c]["codigo_municipio"],
            "mes_abertura":mes_abertura,
            "valor_saldo_abertura":dados["data"][c]["valor_saldo_abertura"]
        }
        retorno["dados"].append(novo_dicionario)
    return retorno
#retorna as contas com menor valor de abertura no mês do ano específicado
@app.get("/valor_de_abertura?menor_codigomunicipio={codigo_municipio}&ano={ano_exercicio}&mes={mes_numerico}")
def retorna_as_contas_com_o_menor_valor_de_abertura_no_mes(codigo_municipio,ano_exercicio,mes_numerico:int):
    meses={
    1: "Janeiro",2: "Fevereiro",3: "Março",4: "Abril",5: "Maio",6: "Junho",7: "Julho",8: "Agosto",9: "Setembro",10: "Outubro",11: "Novembro",12: "Dezembro"
    }
    retorno={"dados":[]}
    saldos_de_abertura=[]
    dados=retorna_informaçoes_bancarias_de_municipios(codigo_municipio ,ano_exercicio)
    
    for c in range(len(dados["dados"])):
        if dados["dados"][c]["mes_abertura"]==meses[mes_numerico]:
            saldos_de_abertura.append(dados["dados"][c]["valor_saldo_abertura"])
    saldos_de_abertura.sort()
    menor_saldo_de_abertura=saldos_de_abertura[0]
    for c in range(len(dados["dados"])):

        if dados["dados"][c]["valor_saldo_abertura"]==menor_saldo_de_abertura and dados["dados"][c]["mes_abertura"]==meses[mes_numerico]:
            novo_dicionario={
            "nome_municipio":dados["dados"][c]["nome_municipio"],
            "codigo_municipio":dados["dados"][c]["codigo_municipio"],
            "mes_abertura":dados["dados"][c]["mes_abertura"],
            "valor_saldo_abertura":dados["dados"][c]["valor_saldo_abertura"]
        }
            retorno["dados"].append(novo_dicionario)
    return retorno