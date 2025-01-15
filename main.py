import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Link da página a ser analisada
URL = "https://www.letras.mus.br/mais-acessadas/rock/"

# Faz a requisição para o endereço e armazena a resposta
response = requests.get(URL)

# Converte a resposta (response) para o formato de texto para facilitar a leitura do Beautifulsoup
html_response = response.text

# Cria um objeto BeautifulSoup com o HTML da resposta, usando o parser html.parser
soup = BeautifulSoup(html_response, 'html.parser')

# Obter todos os registros de músicas encontrados com a tag <ol> e a classe "top-list_mus --top"
musicas_ol = soup.find(name="ol", class_="top-list_mus --top")

# Obter todos os <li> dentro de <ol>
musicas_li = musicas_ol.find_all(name="li")

# Login no Spotify utilizando o módulo Spotipy
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id="SEU_CLIENT_ID",
        client_secret="SEU_CLIENT_SECRET",
        show_dialog=True,
        cache_path="token.txt",
        username="SEU_USER_NAME",
    )
)

# Obter o ID do usuário no Spotify
user_id = sp.current_user()["id"]

# Lista para armazenar as URIS das musicas encontradas
song_uris = []

# Extrair os nomes das músicas e seus respectivos artistas
# O strip=True remove os espaços em branco das strings de nome da música e nome do artista
for musica in musicas_li:
    nome_musica = musica.find("b").get_text(strip=True)
    nome_artista = musica.find("span").get_text(strip=True)

    # Utiliza o metodo search() da biblioteca Spotipy para realizar uma busca por faixas (tracks)
    # que correspondem a um nome de música e a um nome de artista
    result = sp.search(q=f"track:{nome_musica} artist:{nome_artista}", type="track")

    # Imprimir o resultado da busca da musica
    print(result)

    # Tenta obter a URI da musica e adiciona-la na lista de URIs
    # caso a musica nao tenha sido encontrada exibe uma mensagem de que vai pular para a proxima
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"A múscia '{nome_musica}' naõ existe no Spotify. Pulando para a próxima.")


# Criar a playlist
playlist = sp.user_playlist_create(user=user_id, name=f"Rock - As mais acessadas letras.br", public=False)

# Verificar se a playlist foi criada com sucesso
if playlist and "id" in playlist:
    print(f"\nA playlist '{playlist['name']}' foi criada com sucesso!")
else:
    print("Erro ao criar a playlist!")

# Dividir a lista de URIs em blocos de 100 músicas, pois o Spotify so permite enviar 100 musicas de uma vez
batch_size = 100
try:
    for i in range(0, len(song_uris), batch_size):
        batch = song_uris[i:i + batch_size]
        sp.playlist_add_items(playlist_id=playlist["id"], items=batch)

    print(f"\nTodas as músicas encontradas foram adicionadas à playlist '{playlist['name']}' com sucesso!")
except spotipy.exceptions.SpotifyException as e:
    print(f"\nErro ao adicionar músicas à playlist: {e}")
except Exception as e:
    print(f"\nOcorreu um erro inesperado: {e}")

