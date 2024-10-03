import os
import requests
import json
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, ID3NoHeaderError

# Defina sua chave de API do audD aqui
API_KEY = 'e68c503d771bf8503c3479c08ec1390b'

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
        data = {'api_token': API_KEY}
        response = requests.post(url, files=files, data=data)
        return response.json()

def search_album_cover(title, artist):
    itunes_url = 'https://itunes.apple.com/search'
    params = {
        'term': f"{title} {artist}",
        'entity': 'album',
        'limit': 1
    }
    response = requests.get(itunes_url, params=params)
    data = response.json()

    if data['resultCount'] > 0:
        # Retorna a URL da capa do álbum
        return data['results'][0]['artworkUrl100']  # URL da imagem em 100x100
    else:
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

        # Busca a capa do álbum na API do iTunes
        album_cover = search_album_cover(identified_title, identified_artist)

        if album_cover:
            print(f"Capa do Álbum: {album_cover}")
        else:
            print("Capa do álbum não encontrada na API do iTunes.")

        print(f"Música identificada: {identified_title}")
        print(f"Cantor: {identified_artist}")
    else:
        print("Erro ao identificar a música:", response.get("error", {}).get("error_message"))

if __name__ == "__main__":
    main()
