from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request

class PokemonRequestHandler(BaseHTTPRequestHandler):

    def _set_header(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*') # Permite acesso de navegadores
        self.end_headers()

    def do_GET(self):
        # 1. Limpeza da URL para evitar erros de barra extra
        path_limpo = self.path.strip('/') 
        partes = path_limpo.split('/')

        # Mensagens de Debug 
        print(f"\n--- Nova requisição recebida ---")
        print(f"URL completa: {self.path}")
        print(f"Segmentos da URL: {partes}")

        # 2. Roteamento: Verifica se o primeiro nome na URL é 'pokemon'
        if partes[0] == 'pokemon' and len(partes) > 1:
            nome_pokemon = partes[1].lower()
            print(f"Identificado: Usuário quer buscar o pokemon '{nome_pokemon}'")
            
            # 3. Busca na PokeAPI
            dados_pokemon = self.buscar_pokemon(nome_pokemon)

            if dados_pokemon:
                print(f"Sucesso: Dados de {nome_pokemon} obtidos com sucesso!")
                self._set_header(200)
                self.wfile.write(json.dumps(dados_pokemon).encode())
            else:
                print(f"Erro: A PokeAPI não retornou dados para '{nome_pokemon}'.")
                self._set_header(404)
                self.wfile.write(json.dumps({'error': 'Pokemon nao encontrado na PokeAPI'}).encode())
        
        else:
            # Caso o usuário digite apenas http://localhost:8080/ ou algo errado
            print(f"Erro: Rota '{self.path}' não é válida.")
            self._set_header(404)
            self.wfile.write(json.dumps({'error': 'Endpoint invalido. Use /pokemon/nome'}).encode())

    def buscar_pokemon(self, nome):
        
        url = f"https://pokeapi.co/api/v2/pokemon/{nome}"
        
        # Criamos uma requisição com um "User-Agent" (Disfarce de navegador)
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        try:
            # Agora usamos a 'req' em vez de apenas a 'url'
            with urllib.request.urlopen(req) as response:
                dados = json.loads(response.read().decode())
                
                return {
                    'nome': dados['name'],
                    'id': dados['id'],
                    'tipo': [t['type']['name'] for t in dados['types']],
                    'foto': dados['sprites']['front_default']
                }
        except Exception as e:
            print(f"Falha na conexão com PokeAPI: {e}")
            return None

def run(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, PokemonRequestHandler)
    print(f'Servidor da Oficina rodando em http://localhost:{port}')
    print(f"Teste este link: http://localhost:8080/pokemon/pikachu")
    httpd.serve_forever()

if __name__ == '__main__':
    run()