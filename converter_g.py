import binascii
import m3u8

from Crypto.Cipher import AES
from urllib.request import urlopen


def get_key(data):
    host_uri = None
    for i in range(data.media_sequence):
        try:
            key_uri = data.keys[i].uri
            host_uri = "/".join(key_uri.split("/")[:-1])
            return host_uri
        except Exception as e:
            continue


def read_keys(path):
    content = b""

    data_response = urlopen(path)
    content = data_response.read()

    return content


def get_ts(url):
    data = m3u8.load(url)
    key_link = get_key(data)
    ts_content = b""
    key = None

    for i, segment in enumerate(data.segments):
        decrypt_func = lambda x: x
        if segment.key.method == "AES-128":
            if not key:
                key_uri = segment.key.uri
                key = read_keys(key_uri)
            ind = i + data.media_sequence
            iv = binascii.a2b_hex('%032x' % ind)
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            decrypt_func = cipher.decrypt

        ts_url = f'{key_link}/{segment.uri}'
        coded_data = read_keys(ts_url)
        ts_content += decrypt_func(coded_data)
    return ts_content


def m3u8_to_mp3_converter(name, url):
    ts_content = get_ts(url)
    if ts_content is None:
        raise TypeError("Empty mp3 content to save.")
    with open(f'{name}.mp3', 'wb') as out:
        out.write(ts_content)


def m3u8_to_mp3_advanced(name, url):
    ts_content = get_ts(url)
    if ts_content is None:
        raise TypeError("Empty mp3 content to save.")
    with open(f'{name}x.mp3', 'wb') as out:
        out.write(ts_content)
    audioclip = AudioFileClip(f'{name}x.mp3')
    audioclip.write_audiofile(f'{name}.mp3')
    audioclip.close()


if __name__ == '__main__':
    url = input('Type m3u8 url: ')
    name = input('Type filename: ')
    m3u8_to_mp3_advanced(name, url)