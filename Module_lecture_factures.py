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
    i=1
    for page in pages:
        filename_jpg = 'out_facture'+str(i)+'.jpg'
        page.save(filename_jpg, 'JPEG')
        i+=1

    return filename_jpg


def recuperation_position_depuis_pourcentage(filename_jpg, positions_pourcentages):
    im = Image.open(filename_jpg)
    width, height = im.size

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
    liste_fichiers = []
    for nom, position in positions.items():
        im = Image.open(path_image).convert('L')
        im = im.crop(position)

        filename = '_'+str(nom)+'.jpg'
        liste_fichiers.append((nom,filename))

        im.save('_'+str(nom)+'.jpg')
    return liste_fichiers


def texte_zones(liste_fichiers):
    #Permet de récupèrer le texte écrit sur une image
    liste_output_data = []
    for nom, fichier in liste_fichiers:
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


#On supprime les images des zones crées




if __name__ == '__main__':

    #Emplacement de la facture a traiter
    PATH_DOSSIER = """C:\\Users\\GAUTHIER\\Documents\\Programmation\\Python\\OCR_TEST"""
    PATH_PDF = PATH_DOSSIER + "\\test_facture.pdf"

    #dictionnaire des positions en pourcentages (type gimp)
    positions_pourcentages_gimp = {"total" : [85.24, 94.7, 12.7, 2.27],
                "numero_facture" : [4, 25.5, 12, 1.80]}

    #dictionnaire de correction
    dict_corrections =  {"numero_facture": "[^0-9]"}

    #Convertion du pdf en jpg
    filename_jpg = convertion_pdf_jpg(PATH_PDF)

    #Positions en pixel des emplacements
    nouvelle_position_gimp = recuperation_position_depuis_pourcentage_gimp(filename_jpg, positions_pourcentages_gimp)

    #Decoupe des zones interessantes
    liste_fichiers = decoupe_image(filename_jpg, nouvelle_position_gimp)

    #Données contenues dans ces zones
    liste_output_data = texte_zones(liste_fichiers)

    #Correction éventuelles de ces données
    cleaned_data = correction_data(liste_output_data, dict_corrections)

    #Affichage des données finales
    print(cleaned_data)


