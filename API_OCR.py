import requests
import json


#https://ocr.space/ocrapi

def ocr_space_file(filename, overlay=False, api_key='a13ae1e05b*****', language='eng', path=''):
    """ OCR.space API request with local file.
        Python3.5 - not tested on 2.7
    :param filename: Your file path & name.
    :param overlay: Is OCR.space overlay required in your response.
                    Defaults to False.
    :param api_key: OCR.space API key.
                    Defaults to 'helloworld'.
    :param language: Language code to be used in OCR.
                    List of available language codes can be found on https://ocr.space/OCRAPI
                    Defaults to 'en'.
    :return: Result in JSON format.
    """

    payload = {'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': language,
               }
    with open(path + filename, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={filename: f},
                          data=payload,
                          )
    json_file = r.content.decode()
    data = json.loads(json_file)
    text = data['ParsedResults'][0]['ParsedText']


    return text

texte = ocr_space_file(filename='block6.jpeg', path = '/Users/Nicolas/Desktop/PDF2JSON/paper/10.1038ncomms14041/page/textpage0/' )
texte = texte.replace('\n', '')
texte = texte.replace('\r', '')

print(texte)
