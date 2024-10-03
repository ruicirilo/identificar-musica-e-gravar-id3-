import os
import requests
import json
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, ID3NoHeaderError

API_KEY = 'e68c503d771bf8503c3479c08ec1390b'  # Substitua pela sua chave de API do audD

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

def download_album_cover(album_cover_url, title):
    try:
        response = requests.get(album_cover_url)
        if response.status_code == 200:
            # Salva a imagem com o título da música
            cover_filename = f"{title}_cover.jpg"
            with open(cover_filename, 'wb') as cover_file:
                cover_file.write(response.content)
            print(f"Capa do Álbum baixada como: {cover_filename}")
        else:
            print("Erro ao baixar a capa do álbum:", response.status_code)
    except Exception as e:
        print(f"Erro ao baixar a capa do álbum: {e}")

def main():
    file_path = input("Insira o caminho do arquivo MP3: ")
    if not os.path.isfile(file_path):
        print("Arquivo não encontrado. Por favor, insira um caminho válido.")
        return

    title, artist = get_audio_info(file_path)
    print(f"Tentando identificar a música: {title} - {artist}")

    response = upload_audio(file_path)

    # Imprimindo a resposta da API para depuração
    print("Resposta da API:", json.dumps(response, indent=4))

    if response.get("status") == "success":
        song_info = response.get("result", {})
        identified_title = song_info.get('title', 'Título não disponível')
        identified_artist = song_info.get('artist', 'Artista não disponível')
        album_cover = song_info.get('image', 'Capa do álbum não disponível')

        print(f"Música identificada: {identified_title}")
        print(f"Cantor: {identified_artist}")

        # Tenta baixar a capa do álbum
        if album_cover and album_cover != 'Capa do álbum não disponível':
            download_album_cover(album_cover, identified_title)
        else:
            print("Capa do Álbum não disponível.")
    else:
        print("Erro ao identificar a música:", response.get("error", {}).get("error_message"))

if __name__ == "__main__":
    main()

