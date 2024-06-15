import random
import string

from flask import Flask, jsonify, request, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# Swagger config
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL,
                                              API_URL,
                                              config={'app_name': "SUA API"})

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

senhas = {}

# Token management
tokens = {}


def generate_password(comprimento,
                      use_uppercase=True,
                      use_lowercase=True,
                      use_numbers=True,
                      use_special_characters=True):
  characters = ""

  if use_uppercase:
    characters += string.ascii_uppercase
  if use_lowercase:
    characters += string.ascii_lowercase
  if use_numbers:
    characters += string.digits
  if use_special_characters:
    characters += string.punctuation

  password = ''.join(random.choice(characters) for _ in range(comprimento))
  return password


def generate_token(length=20):
  random_bytes = bytes(random.getrandbits(8) for _ in range(length // 2))
  return random_bytes.hex()


@app.route('/static/swagger.json')
def serve_swagger():
  return send_from_directory('static', 'swagger.json')


@app.route('/token', methods=['POST'])
def register():
  data = request.get_json()
  username = data.get('username')
  data.get('password')

  token = generate_token(20)
  tokens[username] = token
  return jsonify({"token": token})


@app.route('/senhas', methods=['GET'])
def get_senha():
  return jsonify({"senha": senhas})


@app.route('/senhas', methods=['POST'])
def gerar_senha():
  token_received = request.headers.get('Authorization')
  if token_received and token_received in tokens.values():

    data = request.get_json()
    senhaId = generate_token(20)

    comprimento = data.get('comprimento')
    use_uppercase = data.get('use_uppercase')
    use_lowercase = data.get('use_lowercase')
    use_numbers = data.get('use_numbers')
    use_special_characters = data.get('use_special_characters')

    senha = generate_password(comprimento, use_uppercase, use_lowercase,
                              use_numbers, use_special_characters)

    senhas[senhaId] = senha

    if (use_uppercase is False and use_lowercase is False
        and use_numbers is False and use_special_characters is False):
      return jsonify({
          "error":
          "Pelo menos uma categoria de caracteres deve ser selecionada."
      }), 403
    else:
      return jsonify({
          "mensagem": "Senha gerada com sucesso",
          "senhaId": senhaId,
          "senha": senha
      })

  else:
    return jsonify({"error": "Token inválido ou ausente"}), 403


@app.route('/senhas/<senhaId>', methods=['PUT'])
def update_senha(senhaId):
  token_received = request.headers.get('Authorization')
  if token_received and token_received in tokens.values():
    if senhaId in senhas:
      data = request.get_json()

      comprimento = data.get('comprimento')
      use_uppercase = data.get('use_uppercase')
      use_lowercase = data.get('use_lowercase')
      use_numbers = data.get('use_numbers')
      use_special_characters = data.get('use_special_characters')

      nova_senha = generate_password(comprimento, use_uppercase, use_lowercase,
                                     use_numbers, use_special_characters)

      senhas[senhaId] = nova_senha
      return jsonify({
          "message": "Senha atualizada com sucesso",
          "nova_senha": nova_senha
      })
    else:
      return jsonify({"error": "Senha não encontrada"}), 404
  else:
    return jsonify({"error": "Token inválido ou ausente"}), 403


@app.route('/senhas/<senhaId>', methods=['DELETE'])
def delete_senha(senhaId):
  token_received = request.headers.get('Authorization')
  if token_received and token_received in tokens.values():
    if senhaId in senhas:
      del senhas[senhaId]
      return jsonify({"message": "Senha excluída com sucesso"})
    else:
      return jsonify({"error": "Senha não encontrada"}), 404
  else:
    return jsonify({"error": "Token inválido ou ausente"}), 403


# Rota para a página web (coloque o código HTML aqui)
@app.route('/')
def serve_webpage():
  return '''
    <html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cadastro</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f4f4f4;
        }

        .container {
            max-width: 400px;
            margin: 100px auto;
            background-color: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        h1 {
            color: #333;
        }

        label, input {
            display: block;
            margin: 10px 0;
        }

        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }

        input[type="submit"] {
            background-color: #007bff;
            color: #fff;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }

        input[type="submit"]:hover {
            background-color: #0056b3;
        }

        .token {
            margin-top: 20px;
            font-size: 18px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Cadastro</h1>
        <form action="/token" method="post">
            <label for="username">Nome de Usuário:</label>
            <input type="text" id="username" name="username">
            <label for="password">Senha:</label>
            <input type="password" id="password" name="password">
            <br><br>
            <input type="submit" value="Cadastrar">
        </form>

        <div class="token" id="token" style="display:none;">
            Seu token é: <span id="tokenValue"></span>
        </div>
    </div>

    <script>
        document.querySelector('form').addEventListener('submit', function(event) {
            event.preventDefault();

            // Simulando o envio do formulário
            var data = {
                username: document.getElementById('username').value,
                password: document.getElementById('password').value
            };

            // Enviando requisição POST
            fetch('/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('tokenValue').textContent = data.token;
                document.getElementById('token').style.display = 'block';
            })
            .catch(error => console.error('Erro:', error));
        });
    </script>
</body>
</html>
    '''


if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0')
