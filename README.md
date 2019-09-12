# OCR-Factures
Un module qui permet de récupérer des informations depuis un document scanné (pdf ou jpg)


Ce module nécessite tesseract : https://fr.osdn.net/projects/sfnet_tesseract-ocr-alt/downloads/tesseract-ocr-setup-3.02.02.exe/

Le module va convertir un fichier pdf en jpg
Il va ensuite découper ce jpg avec les coordonnées fournies 
Il va récupérer les informations de chaques découpes

Pour les découpes, on peut utiliser le logiciel GIMP : https://www.gimp.org/downloads/ , ouvrir le document initial et sélectionner avec une zone rectangle les zones qui sont importante. GIMP affiche les coordonnées de départs de ce rectangle ainsi que ses dimensions. Il est préférable de récupérer ces dimensions en pourcentages.
