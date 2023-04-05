# ======================================== #
# Fichier principal (et unique) du projet) #
# ======================================== #

def main():
    ENCODER_FICHIER = 1
    DECODER_FICHIER = 2
    while(enco_deco<1 or enco_deco>2):
        print("1: encoder")
        print("2: decoder")
        enco_deco = int(input("Faites votre choix: "))

    fichier_chemin = input("Quel fichier voulez-vous coder ou décoder?: ")
    fichier_sortie = input("Quel est le nom du fichier compressé/décompressé?: ")
    if enco_deco == ENCODER_FICHIER:
        contenu_fichier = load_file(fichier_chemin)
        table, texte_comp = code(contenu_fichier)
        save_file_encode(fichier_sortie, table, texte_comp)
    elif enco_deco == DECODER_FICHIER:
        table, contenu_compressed = load_file_decode(fichier_chemin)
        texte_decomp = decoder_txt(table,contenu_compressed)
        save_file(fichier_sortie, texte_decomp)


def code(texte):
    dic = compte(texte)
    arbre = creer_arbre(dic)
    table = creer_table(arbre)
    return table, encoder_txt(table, texte)


def compte(texte):
    dic = {}
    for caractere in texte:
        if caractere in dic:
            dic[caractere] += 1
        else:
            dic[caractere] = 1
    return dic


class Arbre:
    """
    Code d'un arbre binaire spécialisé dans la **compression** de fichiers.
    Une feuille représente une lettre et le chemin jusqu'à la racine son code compréssé.
    Si ce n'est pas une feuille, la node ne DOIT pas contenir une lettre
    """

    def __init__(self, gauche, droit, lettre=None, poid=0):
        """
        Permet d'initialiser l'arbre. Un arbre peut-être noeud d'un autre arbre.

        :param gauche: noeud gauche de l'arbre, si c'est une lettre vide
        :param droite: noeud droit de l'arbre, vide si c'est une lettre
        :param lettre: Indique si c'est une lettre, vide sinon
        :param poid: le poids du noeud dans l'algorithme de création de l'arbre, vide si ce n'est pas une feuille car il sera automatiquement rempli avec le poids de ses fils
        """
        self.gauche = gauche
        self.droit = droit
        self.lettre = lettre
        # Poids des fils
        if self.gauche:
            poid += self.gauche.poid
        if self.droit:
            poid += self.droit.poid
        self.poid = poid

    def afficher(self):
        """
        Permet d'afficher l'arbre pendant le debug sous forme d'un arbre, racine en haut, et en minimisant la place occupée
        """
        # Lignes à remplir en auxiliaire
        strings = {}
        # On commence par la racine
        self.auxiliaire_afficher(0, 0, strings)
        for texte in strings:
            print(texte)

    def auxiliaire_afficher(self, etage_noeud, decalage, liste_etages):
        """
        Fonction auxiliaire récursive de afficher, avec un parcours infixe

        :param etage_noeud: étage actuel du noeud, 1 de + que son père, et position dans liste_etage du string à modifier
        :param decalage: permet décaler sur la droite l'affichage du nom du noeud, ainsi permet d'aligner tout
        :param liste_etages: dictionnaire des strings donnée récursivement à modifier
        """

        # Permet de gérer le cas de None
        lettre = (self.lettre if self.lettre else "")

        # Début de l'infixe : on print le noeud de gauche et on décale
        if self.gauche is not None:
            decalage = self.gauche.auxiliaire_afficher(etage_noeud + 1, decalage, liste_etages)

        # Permet de s'ajouter à la liste tout en gardant les nœuds à gauche et en prenant en compte le décalage
        liste_etages[etage_noeud] = \
            ( # Décalage
                (
                        liste_etages[etage_noeud] + " " * (decalage - len(liste_etages[etage_noeud]))
                ) if (
                        etage_noeud in liste_etages
                ) else " " * decalage
            ) + str(self.poid) + lettre # Affichage
        decalage += len(str(self.poid) + lettre)

        # Même chose pour droit
        if self.droit is not None:
            decalage = self.droit.auxiliaire_afficher(etage_noeud + 1, decalage, liste_etages)

        return decalage


def creer_arbre(dictionnaire_lettres):
    """
    Permet de créer l'arbre de compréssion d'après l'algorithme

    :param dictionnaire_lettres: lettre -> nombre d'occurences
    """

    # Initialisation : chaque lettre devient un noeud de poid occurence
    arbres = []
    for item in dictionnaire_lettres.items():
        arbres.append(Arbre(None, None, lettre=item[0], poid=item[1]))

    # Fonction pour comparer
    def poid(arbre):
        return arbre.poid

    arbres.sort(key=poid)

    # Boucle principale : on fusionne deux par deux les arbres jusqu'à obtenir un unique arbre
    while len(arbres) > 1:
        a0 = arbres.pop(0)
        a1 = arbres.pop(0)

        nouveau_arbre = Arbre(a0, a1)

        index = 0
        while index < len(arbres) and nouveau_arbre.poid > arbres[index].poid:
            index += 1

        if index == len(arbres):
            arbres.append(nouveau_arbre)
        else:
            arbres.insert(index, nouveau_arbre)

    return arbres[0]


def creer_table(arbre):
    '''Cette fonction prend en paramètre un arbre.
    Elle permet de créer un dictionnaire associant un caractère à une suite de nombre binaire.
    Elle renvoie un dictionnaire.
    '''
    dico1 = creer_table_auxiliaire(arbre.gauche, "0")  # initialise dico1 en appelant la fonction creer_table_auxiliaire avec en paramètre arbre.gauche et "0"
    dico1.update(creer_table_auxiliaire(arbre.droit, "1"))  # modifie dico1 en appelant creer_table_auxiliaire avec en paramètre arbre.droit et "1"
    return dico1  # renvoie le dictionnaire dico1


def creer_table_auxiliaire(arbre, cle):
    if arbre.lettre:
        return {arbre.lettre: cle}
    else:
        dico1 = creer_table_auxiliaire(arbre.gauche, cle + "0")
        dico1.update(creer_table_auxiliaire(arbre.droit, cle + "1"))
        return dico1


def encoder_txt(tab, txt):
    liste = ''
    for c in txt:
        liste += tab[c]
    return liste


def decoder_txt(tab, texte):
    '''Cette fonction prend en paramètre une liste et une suite de caractères de nombre binaire.

    Elle permet de traduire le texte binaire.
    Elle renvoie un texte.
    '''
    txt = ''  # initialise txt et num en chaine de caractères vides
    num = ''
    for c in texte:  # parcours des éléments de texte
        num += c  # ajoute un élément de texte dans num
        for item in tab.items():  # .items() récupère une liste de tuples (cle, valeur)
            if num == item[1]:  # si num est égale à l'une des valeurs de tab
                txt += item[0]  # récupère la clé associé à cette valeur dans txt
                num = ''  # affecte une chaine de caractères vide à num
    return txt  # renvoie le txt


def save_file(path, s):
    """
    sauvegarde une string (format ascii) dans un fichier, grâce au chemin fourni.
    paramètre path: chemin d'accès du fichier
    paramètre s: string à sauvegarder
    return: None
    """
    for i in range(len(s)//8):
        binstring = ""
        for j in range(8):
            binstring += s[i*8+j]
    file_bytes = s.encode("ascii")
    with open(path, "wb") as f:
        f.write(file_bytes)
    return


def load_file(path):
    """
    crèe un string (format ascii) en ouvrant un fichier, grâce au chemin fourni.
    paramètre path: chemin d'accès du fichier
    return: string représentant l'entièretée du fichier.
    """
    with open(path, "rb") as f:
        str = f.read().decode("ascii")
    return str


def bin_to_int(s):
    """
    Permet de convertir une chaine caractère (de taille infini) en un seul et unique grand nombre qui pourra être séparé en bytes ensuite. Python permet de stocker des nombres infinis
    """
    val = 0
    for i in range(len(s)):
        val += 2 ** i if s[len(s) - i - 1] == "1" else 0
    return val

def save_file_encode(path, table, encodeds):
    """
    sauvegarde la table et la chaine encodée dans le fichier spécifié
    format:
        header:
            identifieur "HCS" (Huffman Compressing System)
            taille table (bytes)
            taille chaine compressée (bits)
        entrée de table:
            taille clé de table
            clé de table
            caractère ASCII
        chaine compressée:
            valeur binaire
            (optionel) padding
    paramètres:
    path: chemin d'accès vers le fichier dans lequel nous souhaitons sauvegarder notre compression
    table: notre table, qui encode nos différents caractères en chaines de bits
    encodeds: string contenant des 1 et des 0, donc les bits une fois notre texte encodé
    return: None
    """
    k = table.keys()
    bink = {}
    for el in k:
        bink[el] = bin_to_int(table[el])

    bytearr = []
    for i in range(len(encodeds)//8+1):
        binstring = ""
        for j in range(8):
            if i==len(encodeds)//8 and j>=len(encodeds)%8:
                for _ in range(8-len(encodeds)%8):
                    binstring+="0"
                break
            binstring+=encodeds[i*8+j]
        bytearr.append(bin_to_int(binstring))
    

    with open(path, "wb+") as f:
        # header:
        f.write(b"HCS")
        f.write((len(bink) * 3).to_bytes(4, "little"))
        f.write(len(encodeds).to_bytes(4, "little"))

        # table:
        for el in k:
            f.write(len(table[el]).to_bytes(1, "little"))
            f.write(bink[el].to_bytes(1, "little"))
            f.write(el.encode("ascii"))

        # chaine: Convertit un entier en bytes. Le nombre de bytes est calculé de façon à diviser en groupes de 8,
        # avec un groupe minimum. Rappel : le // est prioritaire.
        for i in range(len(encodeds)//8+1):
            f.write(bytearr[i].to_bytes(
                1,
                "little")
            )


def int_to_bin(n):
    """
    convertis d'un int vers une chaine de caractère binaire
    paramètre:
    n: notre int à convertir
    return: chaine de caractère composée de "0" et de "1"
    """
    s = ""
    while n>0 or s=="":
        s = str(n%2) + s
        n = n//2
    return s

def int_to_bin_padding(n, size):
    """
    convertis d'un int vers une chaine de caractère binaire, ajoute des 0 à la fin jusqu'à atteindre la taille binaire demandée
    paramètre:
    n: notre int à convertir
    size: la taille finale de notre chaine
    return: chaine de caractère composée de "0" et de "1"
    """
    s = ""
    while n>0 or s=="":
        s = str(n%2) + s
        n = n//2
        size-=1
    for i in range(size):
        s = "0" + s
    return s

def load_file_decode(path):
    """
    charge la table et la chaine encodée depuis un fichier spécifié
    format:
        header: 
            identifieur "HCS" (Huffman Compressing System)  (3 octets)
            taille table (octets)                           (4 octets)
            taille chaine compressée (bits)                 (4 octets)
        entrée de table:
            taille clé de table                             (1 octet)
            clé de table                                    (1 octet)
            caractère ASCII                                 (1 octet)
        chaine compressée:
            valeur binaire                                  (équivalente à (taille chaine compressée)//8 + 1 bytes)
            (optionel) padding                              (équivalente à (7-(taille chaine compressée))%8 bytes)
    paramètres:
    path: chemin d'accès vers le fichier depuis lequel nous souhaitons récupérer nos données compressées
    return:
    (bink: table de codage, pour décompresser les données
    data: nos données compressées) ou None si le fichier n'est pas valide (aucune vérification n'est faite mise à part l'en-tête du fichier, du moins pour l'instant)
    """

    table_retour = {} #ce sera notre table

    with open(path, "rb") as fichier:
        # read permet de lire n octet.s
        if fichier.read(3)!=b"HCS": #verifier que le fichier soit bien à notre format
            print("Le fichier n'est pas au format HCS")
            return None #il faudra détecter que la fonction ne retourne pas None.
        taille_table = int.from_bytes(fichier.read(4),"little") 
        taille_donnees = int.from_bytes(fichier.read(4),"little") 

        for _ in range(taille_table//3): #boucle pour récupérer notre table, et en faire un dictionnaire
            taille_cle = int.from_bytes(fichier.read(1), "little")
            cle_binaire = int_to_bin_padding(int.from_bytes(fichier.read(1), "little"),taille_cle)
            lettre = fichier.read(1).decode("ascii")
            
            table_retour[lettre] = cle_binaire
        
        data = ""
        for _ in range(taille_donnees//8+1):
            data += int_to_bin_padding(int.from_bytes(fichier.read(1), "little"),8)
    return table_retour,data


if __name__ == "__main__":
    main()
