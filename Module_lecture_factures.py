#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      GAUTHIER
#
# Created:     11/09/2019
# Copyright:   (c) GAUTHIER 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from pdf2image import convert_from_path
import pytesseract
import cv2
import re
from PIL import Image
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\GAUTHIER\AppData\Local\Tesseract-OCR\tesseract.exe'


"""TODO :
    - Correction des erreurs lors de la lecture, voir pour faire un ocr avec une autre méthode et comparer les résultats.
    -
"""


def convertion_pdf_jpg(path_pdf):
    #On converti le pdf en jpg
    pages = convert_from_path(PATH_PDF, 850)
    i=1
    for page in pages:
        filename_jpg = 'out_facture'+str(i)+'.jpg'
        page.save(filename_jpg, 'JPEG')
        i+=1

    return filename_jpg



def recuperation_position_depuis_pourcentage(filename_jpg, positions_pourcentages):
    im = Image.open(filename_jpg)
    width, height = im.size

    for nom, pourcentages in positions_pourcentages.items():
        print(nom, pourcentages)
        liste_positions_pixels = []
        parite = "impaire"
        for pourcentage in pourcentages:
            if parite == "impaire":
                positions_pixel = int((float(pourcentage)*int(width))/100)
                parite = "paire"

            elif parite == "paire":
                positions_pixel = int((float(pourcentage)*int(height))/100)
                parite = "impaire"

            liste_positions_pixels.append(positions_pixel)

        positions[nom] = liste_positions_pixels

    return positions

def recuperation_position_depuis_pourcentage_gimp(filename_jpg, positions_pourcentages_gimp):
    im = Image.open(filename_jpg)
    width, height = im.size

    for nom, pourcentages in positions_pourcentages_gimp.items():
        liste_positions_pixels = []

        x_pos = int((float(pourcentages[0])*int(width))/100)
        y_pos = int((float(pourcentages[1])*int(height))/100)
        x_pos_larg = int(x_pos + (float(pourcentages[2])*int(width))/100)
        y_pos_hauteur = int(y_pos + (float(pourcentages[3])*int(height))/100)
        liste_positions_pixels = [x_pos, y_pos, x_pos_larg, y_pos_hauteur]

        positions[nom] = liste_positions_pixels

    return positions



def decoupe_image(positions):
    #On coupe le jpg master en petites zones avec les informations importantes
    liste_fichiers = []
    for nom, position in positions.items():
        im = Image.open('out_facture1.jpg').convert('L')
        im = im.crop(position)

        filename = '_'+str(nom)+'.jpg'
        liste_fichiers.append((nom,filename))

        im.save('_'+str(nom)+'.jpg')
    return liste_fichiers


def texte_zones(liste_fichiers):
    #On recupère le texte des zones
    for nom, fichier in liste_fichiers:
        img = cv2.imread(fichier)
        print("---" + str(nom) + "---")
        data = pytesseract.image_to_string(img)
        if nom == "numero_facture":
            data = re.sub("[^0-9]", "", data)
        print(data)


#On supprime les images des zones crées



PATH_DOSSIER = """C:\\Users\\GAUTHIER\\Documents\\Programmation\\Python\\OCR_TEST"""
PATH_PDF = PATH_DOSSIER + "\\test_facture.pdf"



positions = {"total" : [5550, 8770, 5550+1000, 8770+450],
            "numero_facture" : [150, 2380, 150+1000, 2400+200]}

positions_pourcentages = {"total" : [83.9, 93.7, 99.1, 98.5],
            "numero_facture" : [2, 25.4, 17.4, 27.8]}

positions_pourcentages_gimp = {"total" : [83.8, 93.8, 15.0, 4.70],
            "numero_facture" : [3.81, 25.61, 12.10, 1.80]}

positions_pourcentages_gimp = {"total" : [85.24, 94.7, 12.7, 2.27],
            "numero_facture" : [4, 25.5, 12, 1.80]}


filename_jpg = convertion_pdf_jpg(PATH_PDF)
nouvelle_position_gimp = recuperation_position_depuis_pourcentage_gimp(filename_jpg, positions_pourcentages_gimp)
liste_fichiers = decoupe_image(nouvelle_position_gimp)
texte_zones(liste_fichiers)


