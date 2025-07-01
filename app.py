from flask import Flask, request, jsonify
from zeep import Client
from zeep.transports import Transport
import requests

app = Flask(__name__)

wsdl = 'https://api.sponteeducacional.net.br/WSAPIEdu.asmx?WSDL'
client = Client(wsdl=wsdl, transport=Transport(timeout=10))

sedes = {
    "Aldeota": {"codigo": "72546", "token": "QZUSqqgsLA63"},
    "Sul": {"codigo": "74070", "token": "jVNLW7IIUXOh"},
    "Bezerra": {"codigo": "488365", "token": ""},
}

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
                    resultados.append({
                        "sede": nome_sede,
                        "nome": aluno.Nome,
                        "cpf": aluno.CPF,
                        "turma_atual": aluno.TurrmaAtual,
                        "nascimento": aluno.DataNascimento.strftime("%Y-%m-%d") if aluno.DataNascimento else None
                    })

        except Exception as e:
            resultados.append({
                "sede": nome_sede,
                "erro": f"Erro ao buscar alunos na sede {nome_sede}: {str(e)}"
            })

    if not resultados:
        return jsonify({"mensagem": "Nenhum aluno encontrado com esse CPF."}), 404

    return jsonify(resultados)

if __name__ == '__main__':
    app.run(debug=True)
