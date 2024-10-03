import os
import requests
import json
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, ID3NoHeaderError

# Defina sua chave de API do Spotify e AudD aqui
SPOTIFY_TOKEN = 'BQAln43LetHIQZzPUSVXUutuEQ-wljzWmdMu3YF1OGD-ibKgUmMdXddwPy0l53GIHRFcxSQVoSLxGWXVb78sRWX-zHYQV-ITKBat8Y1QqvpGoXNa5UfrIFvqGqnFjcKIalzQLvoer2rnIUydXglr28GkjiAFgSKIEGErz7l2jvbFU98RMQatpBIbyYeoHf3L2rFTaUwnCqKLUJ-7nx9wnh0XskymkDt5xNBE1TlUecChUE7iousVFVjMv8AOGy2WrSHehkonfKCvuhP_2fpXBCKO3dwQKm_y'
API_KEY = 'e68c503d771bf8503c3479c08ec1390b'  # Corrigido para string

def get_audio_info(file_path):
    try:
        audio = MP3(file_path, ID3=ID3)
        title = audio.get("TIT2", "Unknown Title").text[0] if "TIT2" in audio else "Unknown Title"
        artist = audio.get("TPE1", "Unknown Artist").text[0] if "TPE1" in audio else "Unknown Artist"
        return title, artist
    except ID3NoHeaderError:
        return "Unknown Title", "Unknown Artist"
    except Exception as e:
        print(f"Error reading audio info: {e}")
        return "Unknown Title", "Unknown Artist"

def upload_audio(file_path):
    url = 'https://api.audd.io/'
    with open(file_path, 'rb') as file:
        files = {'file': file}
        data = {'api_token': API_KEY}  # Corrigido para usar API_KEY
        response = requests.post(url, files=files, data=data)
        return response.json()

def search_album_cover(identified_title, identified_artist):
    # Busca a música no Spotify usando o título e o artista
    search_url = 'https://api.spotify.com/v1/search'
    headers = {
        'Authorization': f'Bearer {SPOTIFY_TOKEN}'
    }
    params = {
        'q': f'track:{identified_title} artist:{identified_artist}',
        'type': 'track',
        'limit': 1
    }
    response = requests.get(search_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['tracks']['items']:
            # Retorna a URL da capa do álbum
            return data['tracks']['items'][0]['album']['images'][0]['url']  # URL da imagem
    else:
        print(f"Erro ao buscar capa do álbum: {response.status_code} - {response.text}")
    return None

def main():
    file_path = input("Insira o caminho do arquivo MP3: ")
    if not os.path.isfile(file_path):
        print("Arquivo não encontrado. Por favor, insira um caminho válido.")
        return

    title, artist = get_audio_info(file_path)
    print(f"Tentando identificar a música: {title} - {artist}")

    response = upload_audio(file_path)

    print("Resposta da API:", json.dumps(response, indent=4))

    if response.get("status") == "success":
        song_info = response.get("result", {})
        identified_title = song_info.get('title', 'Título não disponível')
        identified_artist = song_info.get('artist', 'Artista não disponível')

        # Busca a capa do álbum na API do Spotify
        album_cover = search_album_cover(identified_title, identified_artist)

        if album_cover:
            print(f"Capa do Álbum: {album_cover}")
        else:
            print("Capa do álbum não encontrada na API do Spotify.")

        print(f"Música identificada: {identified_title}")
        print(f"Cantor: {identified_artist}")
    else:
        print("Erro ao identificar a música:", response.get("error", {}).get("error_message"))

if __name__ == "__main__":
    main()
