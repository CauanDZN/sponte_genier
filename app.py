import os
import time
from flask import Flask, request, jsonify
from zeep import Client
from zeep.transports import Transport
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

WSDL_URL = 'https://api.sponteeducacional.net.br/WSAPIEdu.asmx?WSDL'
WSDL_LOCAL_FILE = 'WSAPIEdu.wsdl'

sedes = {
    "Aldeota": {"codigo": "72546", "token": "QZUSqqgsLA63"},
    "Sul": {"codigo": "74070", "token": "jVNLW7IIUXOh"},
    "Bezerra": {"codigo": "488365", "token": ""},
}

app = Flask(__name__)

def baixar_wsdl(url, arquivo_saida):
    if os.path.exists(arquivo_saida):
        print(f'{arquivo_saida} já existe. Pulando download.')
        return

    print('Baixando WSDL com Selenium...')
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        time.sleep(5)  # espera carregar a página
        wsdl_element = driver.find_element('tag name', 'pre')
        wsdl_text = wsdl_element.text

        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            f.write(wsdl_text)
        print(f'WSDL salvo em {arquivo_saida}')
    finally:
        driver.quit()

print('Iniciando aplicação...')
baixar_wsdl(WSDL_URL, WSDL_LOCAL_FILE)

client = Client(wsdl=WSDL_LOCAL_FILE, transport=Transport(timeout=10))

@app.route('/buscar-aluno', methods=['GET'])
def buscar_aluno():
    cpf = request.args.get('cpf', '').strip()
    if not cpf:
        return jsonify({"erro": "CPF é obrigatório"}), 400

    resultados = []

    for nome_sede, dados in sedes.items():
        try:
            parametros_busca = f"CPF={cpf};"
            resposta = client.service.GetAlunos(
                nCodigoCliente=dados["codigo"],
                sToken=dados["token"],
                sParametrosBusca=parametros_busca
            )

            if resposta:
                for aluno in resposta:
                    responsaveis = []
                    r_data = getattr(aluno, "Responsaveis", [])
                    if isinstance(r_data, list):
                        for r in r_data:
                            responsaveis.append({
                                "ResponsavelID": getattr(r, "ResponsavelID", None),
                                "Nome": getattr(r, "Nome", None),
                                "Parentesco": getattr(r, "Parentesco", None)
                            })

                    resultado = {
                        "sede": nome_sede,
                        "OperacaoRealizada": getattr(aluno, "OperacaoRealizada", None),
                        "CPF": getattr(aluno, "CPF", None),
                        "RG": getattr(aluno, "RG", None),
                        "ResponsavelFinanceiroID": getattr(aluno, "ResponsavelFinanceiroID", None),
                        "AlunoID": getattr(aluno, "AlunoID", None),
                        "Nome": getattr(aluno, "Nome", None),
                        "Midia": getattr(aluno, "Midia", None),
                        "DataNascimento": getattr(aluno, "DataNascimento", None),
                        "CEP": getattr(aluno, "CEP", None),
                        "Endereco": getattr(aluno, "Endereco", None),
                        "NumeroEndereco": getattr(aluno, "NumeroEndereco", None),
                        "ResponsavelDidaticoID": getattr(aluno, "ResponsavelDidaticoID", None),
                        "Email": getattr(aluno, "Email", None),
                        "DataCadastro": getattr(aluno, "DataCadastro", None),
                        "NumeroMatricula": getattr(aluno, "NumeroMatricula", None),
                        "RA": getattr(aluno, "RA", None),
                        "LoginPortal": getattr(aluno, "LoginPortal", None),
                        "SenhaPortal": getattr(aluno, "SenhaPortal", None),
                        "TurmaAtual": getattr(aluno, "TurmaAtual", None),
                        "Responsaveis": responsaveis,
                        "Observacao": getattr(aluno, "Observacao", None),
                        "Telefone": getattr(aluno, "Telefone", None),
                        "Cidade": getattr(aluno, "Cidade", None),
                        "Bairro": getattr(aluno, "Bairro", None),
                        "CidadeNatal": getattr(aluno, "CidadeNatal", None),
                        "Celular": getattr(aluno, "Celular", None),
                        "Genero": getattr(aluno, "Genero", None),
                        "Situacao": getattr(aluno, "Situacao", None),
                        "Inadimplente": getattr(aluno, "Inadimplente", None),
                        "NomeOrigem": getattr(aluno, "NomeOrigem", None),
                        "OrigemID": getattr(aluno, "OrigemID", None),
                        "CursoInteresse": getattr(aluno, "CursoInteresse", "").split(";") if getattr(aluno, "CursoInteresse", "") else []
                    }

                    resultados.append(resultado)

        except Exception as e:
            resultados.append({
                "sede": nome_sede,
                "erro": f"Erro ao buscar alunos na sede {nome_sede}: {str(e)}"
            })

    if not resultados:
        return jsonify({"mensagem": "Nenhum aluno encontrado com esse CPF."}), 404

    return jsonify(resultados)

if __name__ == '__main__':
    app.run(debug=True, port=5050)
