import cv2
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

def captch_ex(file_name ):

    img  = cv2.imread(file_name)
    img2gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img2gray, 180, 255, cv2.THRESH_BINARY)
    #image_final = cv2.bitwise_and(img2gray , img2gray , mask =  mask)
    ret, new_img = cv2.threshold(mask, 180 , 255, cv2.THRESH_BINARY_INV)
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(3 , 2)) # to manipulate the orientation of dilution , large x means horizonatally dilating  more, large y means vertically dilating more
    dilated = cv2.dilate(new_img,kernel,iterations = 10)

    image_cont, contours, hierarchy = cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    #cv2.drawContours(image_cont, contours, -1, (0,255,0), 3)



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
        '''
        img_crop = img[y:y + h, x: x + w]
        img_crop = Image.fromarray(img_crop)
        img_crop.save('paper/test_split/crop%s.jpeg' % (j-i-1))
        '''
        [x,y,w,h] = cv2.boundingRect(contours[liste_sort[j-i-1][1]]) #lecture inverse de la liste pour lire les cadres de haut en bas
        # draw rectangle around contour on original image
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),1)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img,'Cadre%s' % (j-i-1) ,(x,y), font, 1,(255,0,0),2,cv2.LINE_AA) # annotation des cadre "cadre0", "cadre1", ect


    cv2.imshow('image',img)
    k = cv2.waitKey(0)
    if k == 27:         # wait for ESC key to exit
        cv2.destroyAllWindows()

for i in range(12):
    file_name ='/Users/Nicolas/Desktop/PDF2JSON/paper/10.1038ncomms14041/page/page%s.jpeg' % i
    captch_ex(file_name)
