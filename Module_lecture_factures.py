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
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\GAUTHIER\AppData\Local\Tesseract-OCR\tesseract.exe'


"""TODO :
    - Correction des erreurs lors de la lecture, voir pour faire un ocr avec une autre méthode et comparer les résultats.
    - Voir pour faire du preprocessing des images pour améliorer le résultat de la lecture
    - Voir pour faire du processing sur chaque zones d'images au lieu de la grande.

    AMELIORATIONS :
        - GUI qui permet de paramètrer facilement les zones de recherches avec des rectangles associés à des noms
"""

class Coordonnees:
    def __init__(self, x_coord=-1, y_coord=-1, x_coord_final=-1, y_coord_final=-1):
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.x_coord_final = x_coord_final
        self.y_coord_final = y_coord_final

    def coordonnees_valides(self):
        valid = True
        for (nom, coord) in self.__dict__.items():
            if coord == -1:
                valid = False

        if self.x_coord >= self.x_coord_final or self.y_coord >= self.y_coord_final:
            valid = False

        return valid

    def liste_coordonnees(self):
        if self.coordonnees_valides == False:
            print("coordonnées non valides")
            return False

        return [self.x_coord, self.y_coord, self.x_coord_final, self.y_coord_final]


def convertion_pdf_jpg(path_pdf):
    #On converti le pdf en jpg
    pages = convert_from_path(PATH_PDF, 850)
    path_folder_pdf = os.path.dirname(os.path.abspath(path_pdf))

    i=1
    for page in pages:
        filename_jpg = path_folder_pdf + '\out_facture'+str(i)+'.jpg'
        page.save(filename_jpg, 'JPEG')
        i+=1

    return filename_jpg

def preprocessing(path_image):
    image = cv2.imread(path_image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    kernel = np.ones((5,5), np.uint8)

    gray = cv2.dilate(gray, kernel, iterations=2)
    gray = cv2.erode(gray, kernel, iterations=2)

##    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

##    gray = cv2.threshold(gray, 0, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C | cv2.THRESH_OTSU)[1]

##    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.ADAPTIVE_THRESH_GAUSSIAN_C)[1]
##    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]



    blur = cv2.GaussianBlur(gray,(5,5),0)
    gray = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]

##    image = cv2.imread(path_image, 0)
##    gray = cv2.medianBlur(image, 5)
##    gray = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)

    filename = os.path.basename(path_image)
    cv2.imwrite(path_image, gray)

    return path_image


def recuperation_position_depuis_pourcentage(filename_jpg, positions_pourcentages):
    im = Image.open(filename_jpg)
    width, height = im.size

    positions = {}

    for nom, pourcentages in positions_pourcentages_gimp.items():

        coord = Coordonnees()
        coord.x_coord = int((float(pourcentages[0])*int(width))/100)
        coord.y_coord = int((float(pourcentages[1])*int(height))/100)
        coord.x_coord_final = int((float(pourcentages[2])*int(width))/100)
        coord.y_coord_final = int((float(pourcentages[3])*int(height))/100)

        positions[nom] = coord.liste_coordonnees()

    return positions


def recuperation_position_depuis_pourcentage_gimp(filename_jpg, positions_pourcentages_gimp):
    im = Image.open(filename_jpg)
    width, height = im.size

    positions = {}

    for nom, pourcentages in positions_pourcentages_gimp.items():

        coord = Coordonnees()
        coord.x_coord = int((float(pourcentages[0])*int(width))/100)
        coord.y_coord = int((float(pourcentages[1])*int(height))/100)
        coord.x_coord_final = int(coord.x_coord + (float(pourcentages[2])*int(width))/100)
        coord.y_coord_final = int(coord.y_coord + (float(pourcentages[3])*int(height))/100)

        positions[nom] = coord.liste_coordonnees()

    return positions


def decoupe_image(path_image, positions):
    #Permet de découper une images en plusieurs zones spécifiques définies par le paramètre "positions" qui est un dictionnaire
    path_folder_image = os.path.dirname(os.path.abspath(path_image))

    liste_fichiers = []
    for nom, position in positions.items():
        im = Image.open(path_image).convert('L')
        im = im.crop(position)

        filename = path_folder_image + '\_'+str(nom)+'.jpg'
        liste_fichiers.append((nom,filename))

        im.save(filename)
    return liste_fichiers


def texte_zones(liste_fichiers):
    #Permet de récupèrer le texte écrit sur une image
    liste_output_data = []
    for nom, fichier in liste_fichiers:
        fichier = preprocessing(fichier)
        img = cv2.imread(fichier)
        data = pytesseract.image_to_string(img)
        liste_output_data.append((nom, data))

    return liste_output_data

def correction_data(liste_output_data, dict_corrections={}):
    #Fonction assez spécifique qui permet de corriger d'éventuelles erreurs de lecture en savant quel type
    # d'information on attend,en éviter d'avoir des charactères parasites qui peuvent avoir été lu.
    #ex : dict_corrections =  {"numero_facture": "[^0-9]"} est un dictionnaire qui permet de corriger pour chaque information
    for (nom, data) in liste_output_data:
        if nom in dict_corrections:
            new_data = re.sub(dict_corrections[nom], "", data)
            liste_output_data[liste_output_data.index((nom, data))] = (nom, new_data)

    return liste_output_data

def positions_double_verification(dict_positions):
    increment = float(0.1)
    nbr_increments = 4
    nouveau_dict_positions = {}
    for (nom, position) in dict_positions.items():
        for i in range(nbr_increments):
            nouvelle_position = [position[0], position[1] + float((i+1)*increment), position[2], position[3]]
            nouveau_dict_positions[str(nom) + "_" + str(i+1)] = nouvelle_position

        for i in range(nbr_increments):
            nouvelle_position = [position[0], position[1] - (i+1)*increment, position[2], position[3]]
            nouveau_dict_positions[str(nom) + "_-" + str(i+1)] = nouvelle_position

    return nouveau_dict_positions




#On supprime les images des zones crées


if __name__ == '__main__':

    #Emplacement de la facture a traiter
    PATH_DOSSIER = """C:\\Users\\GAUTHIER\\Documents\\Programmation\\Python\\OCR_TEST\\Factures"""
    PATH_PDF = PATH_DOSSIER + "\\test_facture3.pdf"

    #dictionnaire des positions en pourcentages (type gimp)
    positions_pourcentages_gimp = {"total" : [85.24, 94.7, 12.7, 2.27], #ok pour y_coord = 94, 94.1, 94.2, 94.3
                "numero_facture" : [2.9, 25.35, 14.3, 2.51],
                "date" : [3.3, 28.5, 9.75, 2.37],
                "prix_ht" : [87.6, 86.87, 10.28, 2.17],
                "prix_tva" : [88.26, 89.73, 8.43, 1.81],
                "nom" : [45.78, 1.65, 53.18, 2.29]}

    #dictionnaire de correction
    dict_corrections =  {"numero_facture": "[^0-9]"}

    #Convertion du pdf en jpg
    filename_jpg = convertion_pdf_jpg(PATH_PDF)

    positions_double_verif = positions_double_verification(positions_pourcentages_gimp)

    #Positions en pixel des emplacements
    nouvelle_position_gimp = recuperation_position_depuis_pourcentage_gimp(filename_jpg, positions_double_verif)

    #On fait plusieurs lecture de la même zone en utilisant un offset
##    positions_double_verif = positions_double_verification(nouvelle_position_gimp)

    #Decoupe des zones interessantes
    liste_fichiers = decoupe_image(filename_jpg, nouvelle_position_gimp)

    #Données contenues dans ces zones
    liste_output_data = texte_zones(liste_fichiers)

    #Correction éventuelles de ces données
    cleaned_data = correction_data(liste_output_data, dict_corrections)

    #Affichage des données finales
    print(cleaned_data)


