
import os
import shutil
import subprocess
import cv2
import requests
import json
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
from PyPDF2 import PdfFileWriter, PdfFileReader


"""
tree :
PDF2Json
|
|-main.py
|-paper
    |
    |-folder_named_as_DOI
               |
               |- filename.pdf
               |-page
                   |-page0.pdf
                   |-page1.pdf
                   ...
                   |-textpage0
                         |-block0.txt
                         |-block1.txt
                         ...
                   ...
                   |-textpageN
"""

# : Le DOI peut contient des / ce qui interfere avec les path, on le supprime en attendant d etrouver un caractere qui n'interfere pas non plus avec le bash (pas de $ ou | )
def pdf2jpeg(pdf_path = 'pdfname', folder_page =''):
    '''
    etape 1 : lecture du fichier PDF et split en plusieur pdf de 1 page
    etape 2 : conversion des PDF en image jpeg
    '''
    inputpdf = PdfFileReader(open(pdf_path, "rb"))
    for i in range(inputpdf.numPages):
        output = PdfFileWriter()
        output.addPage(inputpdf.getPage(i))
        with open(folder_page + "/page%s.pdf" % i, "wb") as outputStream: #split des pdf en plusier pdf de 1 page
            output.write(outputStream)
    subprocess.call('bash PDF2img.sh %s' % ('/Users/Nicolas/Desktop/PDF2JSON/' + folder_page), shell=True ) # conversion des pdf en jpeg par un programme shell




def block_text(path='path/without/end_file', pathsave='', file_name='file_name'):

    img  = cv2.imread(path + file_name)
    img2gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img2gray, 180, 255, cv2.THRESH_BINARY)
    #image_final = cv2.bitwise_and(img2gray , img2gray , mask =  mask)
    ret, new_img = cv2.threshold(mask, 180 , 255, cv2.THRESH_BINARY_INV)
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(6 , 3)) # to manipulate the orientation of dilution , large x means horizonatally dilating  more, large y means vertically dilating more
    dilated = cv2.dilate(new_img,kernel,iterations = 9)

    image_cont, contours, hierarchy = cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

    index = -1
    j = 0
    liste_y = []

    for contour in contours: #ici construction et tri des rectangle et construction de la liste des index en fonction de la position vertical du cadre
        # get rectangle bounding contour
        [x,y,w,h] = cv2.boundingRect(contour)
        index += 1 #index dans la liste contours non triée

        #Don't plot small false positives that aren't text
        if w < 35 and h < 35 : # /!\ condition du tri important pour évité les faux positif
            continue
        liste_y.append((y, index)) #liste de type L = [(y,index), ...] ou y est la position verticale du haut du cadre
        j += 1 #compteur après le tri de if
    liste_sort = sorted(liste_y) #tri de la liste en fonction de y, les y les plus petit (en bas de page) en premier. Note: pas d'inversion car pas trouver comment faire donc lecture inverse plus tard dans la boucle for à l'aide des indice i et j
    for i in range(j): #lecture des cadres trié

        [x,y,w,h] = cv2.boundingRect(contours[liste_sort[j-i-1][1]]) #lecture inverse de la liste pour lire les cadres de haut en bas
        # draw rectangle around contour on original image
        #cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),1)
        #font = cv2.FONT_HERSHEY_SIMPLEX
        #cv2.putText(img,'Cadre%s' % (j-i-1) ,(x,y), font, 1,(255,0,0),2,cv2.LINE_AA) # annotation des cadre "cadre0", "cadre1", ect

        img_crop = img[y:y + h, x: x + w]
        img_crop = Image.fromarray(img_crop)
        img_crop.save( pathsave + 'block%s.jpeg' % (j-i-1))

    #cv2.imshow('image',img)
    #k = cv2.waitKey(0)
    #if k == 27:         # wait for ESC key to exit
        #cv2.destroyAllWindows()
def ocr_api(filename, overlay=False, api_key='a13ae1e05b88957', language='eng', path=''):
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

# Les input sont le path du fichier et le DOI de l'article
#pdf2jpeg('/Users/Nicolas/Desktop/test.pdf', '10.1038ncomms14041' )

def main(path = 'path', DOI = 'doi'):
    '''
    ouverture du fichier et création d'un doseier avec le nom du DOI
    '''
    inputpdf = PdfFileReader(open(path, "rb"))
    file_name = os.path.basename(path)
    folder_DOI = "paper/"+ DOI
    folder_page = "paper/"+ DOI + "/page"
    pdf_path = folder_DOI + '/' + DOI + '.pdf'

    if not os.path.isdir(folder_page):
       os.makedirs(folder_page) #création du path folder_path qui correspond a : /paper/DOI/page/
       try: #copie du fichier dans le nouveau path et renomé en son DOI
           shutil.copy2( path, '/Users/Nicolas/Desktop/PDF2JSON/paper/'+ DOI)
           os.rename('/Users/Nicolas/Desktop/PDF2JSON/paper/' + DOI + '/' + file_name  , '/Users/Nicolas/Desktop/PDF2JSON/paper/'+ DOI + '/' + DOI + '.pdf')
       except Error:
           None

    pdf2jpeg(pdf_path, folder_page)
    for i in range(inputpdf.numPages):
        if not os.path.isdir(folder_page + '/textpage%s' % i ):
            os.makedirs(folder_page + '/textpage%s' % i ) #création des dossier pour les block de text
        block_text(folder_page +'/',folder_page + '/textpage%s/' % i, 'page%s.jpeg' % i) #fonction block text qui prend une image en entré (une page) et qui en ressort les block de text
        nb_block = len([f for f in os.listdir(folder_page + '/textpage%s/' % i) if os.path.isfile(os.path.join(folder_page + '/textpage%s/' % i, f)) and f[0] != '.'])
 #count the number of block for iteration
        textpage = open(folder_page + '/textpage%s.txt' % i, 'a' )
        for j in range(nb_block):

            text = ocr_api(filename='block%s.jpeg' % j ,path = folder_page + '/textpage%s/' % i)
            text = text.replace('\n', '')
            text = text.replace('\r', '')
            textpage.write(text + '\n')
            print('block %s in page %s done' % (j, i))
        textpage.close
        print('---- page %s Done ----' % i)


main('/Users/Nicolas/Desktop/test.pdf', '10.1038ncomms14041' )
