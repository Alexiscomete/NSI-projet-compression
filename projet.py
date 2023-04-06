# ======================================== #
# Fichier principal (et unique) du projet) #
# ======================================== #

def main():
    ENCODER_FICHIER = 1
    DECODER_FICHIER = 2
    enco_deco = ENCODER_FICHIER + DECODER_FICHIER
    while not (enco_deco in [ENCODER_FICHIER, DECODER_FICHIER]):
        print(ENCODER_FICHIER, ": encoder")
        print(DECODER_FICHIER, ": decoder")
        enco_deco = int(input("Faites votre choix : "))

    fichier_chemin = input("Quel fichier voulez-vous coder ou décoder ?: ")
    fichier_sortie = input("Quel est le nom du fichier compressé/décompressé ?: ")
    if enco_deco == ENCODER_FICHIER:
        contenu_fichier = load_file(fichier_chemin)
        table, texte_comp = code(contenu_fichier)
        save_file_encode(fichier_sortie, table, texte_comp)
    elif enco_deco == DECODER_FICHIER:
        table, contenu_compressed = load_file_decode(fichier_chemin)
        texte_decomp = decoder_txt(table, contenu_compressed)
        save_file(fichier_sortie, texte_decomp)


def compte(texte):
    """
    Cette fonction prend en paramètre une chaîne de caractères 'texte'
    et renvoie un dictionnaire 'dic' où les clés sont les caractères de la chaîne
    et les valeurs, le nombre d'occurrences de chaque caractère.
    """
    dic = {}
    for caractere in texte:  # Parcours chaque caractères du texte
        if caractere in dic:  # Condition qui vérifie si le caractère est déjà présent dans le dictionnaire
            dic[caractere] += 1  # Si oui, la fonction incrémente de 1 la valeur associée à cette clé
        else:
            dic[caractere] = 1  # Sinon, elle crée une nouvelle clé dont la valeur est initialisée à 1
    return dic


if __name__ == "__main__":
    assert compte('') == {}
    assert compte('texte') == {'t': 2, 'e': 2, 'x': 1}


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
        :param droit: noeud droit de l'arbre,
        vide si c'est une lettre
        :param lettre: Indique si c'est une lettre, vide sinon
        :param poid: le poids du noeud dans l'algorithme de création de l'arbre, vide si ce n'est pas une feuille, car
        il sera automatiquement rempli avec le poids de ses fils
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
        Permet d'afficher l'arbre pendant le debug sous forme d'un arbre, racine en haut, et en minimisant la place
        occupée
        """
        # Lignes à remplir en auxiliaire
        strings = {}
        # On commence par la racine
        self.auxiliaire_afficher(0, 0, strings)
        for texte in strings:
            print(texte)

    def auxiliaire_afficher(self, etage_noeud, decalage, liste_etages):
        """
        Fonction auxiliaire récursive d'afficher, avec un parcours infixe
        :param etage_noeud: étage actuel du nœud, 1 de + que son père et position dans liste_etage du string à modifier
        :param decalage: permet décaler sur la droite l'affichage du nom du nœud, ainsi permet d'aligner tout
        :param liste_etages: dictionnaire des strings donné récursivement à modifier
        """

        # Permet de gérer le cas de None
        lettre = (self.lettre if self.lettre else "")

        # Début de l'infixe : on print le nœud de gauche et on décale
        if self.gauche is not None:
            decalage = self.gauche.auxiliaire_afficher(etage_noeud + 1, decalage, liste_etages)

        # Permet de s'ajouter à la liste tout en gardant les nœuds à gauche et en prenant en compte le décalage
        liste_etages[etage_noeud] = \
            (  # Décalage
                (
                        liste_etages[etage_noeud] + " " * (decalage - len(liste_etages[etage_noeud]))
                ) if (
                        etage_noeud in liste_etages
                ) else " " * decalage
            ) + str(self.poid) + lettre  # Affichage
        decalage += len(str(self.poid) + lettre)

        # Même chose pour droit
        if self.droit is not None:
            decalage = self.droit.auxiliaire_afficher(etage_noeud + 1, decalage, liste_etages)

        return decalage

    def somme_poids(self):
        somme = self.poid
        if self.droit:
            somme += self.droit.somme_poids()
        if self.gauche:
            somme += self.gauche.somme_poids()
        return somme

    def lettres(self, liste):
        if self.lettre:
            liste.append(self.lettre)
        else:
            if self.droit:
                self.droit.lettres(liste)
            if self.gauche:
                self.gauche.lettres(liste)

    def __eq__(self, arbre):
        liste1 = []
        liste2 = []
        self.lettres(liste1)
        arbre.lettres(liste2)
        for element in liste1:
            if element not in liste2:
                return False
        return arbre.somme_poids() == self.somme_poids()


def creer_arbre(dictionnaire_lettres):
    """
    Permet de créer l'arbre de compréssion d'après l'algorithme
    :param dictionnaire_lettres: lettre → nombre d'occurences
    """

    # Initialisation : chaque lettre devient un noeud de poid "occurences"
    arbres = []
    for item in dictionnaire_lettres.items():
        arbres.append(Arbre(None, None, lettre=item[0], poid=item[1]))

    if len(arbres) == 0:
        return None

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
    """Cette fonction prend en paramètre un arbre.
    Elle permet de créer un dictionnaire associant un caractère à une suite de nombre binaire.
    Elle renvoie un dictionnaire.
    """
    # initialise dico1 en appelant la fonction creer_table_auxiliaire avec en paramètre arbre.gauche et "0"
    dico1 = creer_table_auxiliaire(arbre.gauche, "0")
    # modifie dico1 en appelant creer_table_auxiliaire avec en paramètre arbre.droit et "1"
    dico1.update(creer_table_auxiliaire(arbre.droit, "1"))
    return dico1  # renvoie le dictionnaire dico1


def creer_table_auxiliaire(arbre, cle):
    """Cette fonction prend en entrée un noeud arbre et une chaîne de caractères cle
    qui représente le code binaire associé à la lettre en cours d'exploration.
    Si arbre correspond à une feuille, c'est-à-dire si le noeud contient une lettre,
    alors on retourne un dictionnaire contenant cette lettre comme clé et cle comme valeur."""

    # À chaque appel de la fonction, elle vérifie si le noeud courant contient un caractère).
    if arbre.lettre:
        # Si oui, elle retourne un dictionnaire qui contient la correspondance entre le caractère et le code binaire
        # représenté par la clé "cle".
        return {arbre.lettre: cle}
    else:
        """Sinon, on appelle récursivement creer_table_auxiliaire sur le fils gauche de arbre
        en ajoutant "0" à la fin de cle, puis sur le fils droit de arbre en ajoutant "1" à la
        fin de cle. On combine ensuite les deux dictionnaires retournés à l'aide de la méthode
        update et on retourne le dictionnaire résultant."""
        dico1 = creer_table_auxiliaire(arbre.gauche, cle + "0")
        dico1.update(creer_table_auxiliaire(arbre.droit, cle + "1"))
        return dico1


def encoder_txt(tab, texte):
    """
    Cette fonction prend en paramètre un dictionnaire 'tab' et une chaîne
    de caractères 'texte' et renvoie le texte codé.
    """
    txt = ''
    for c in texte:  # Parcours chaque caractère du texte
        txt += tab[c]  # Ajoute dans 'txt' la valeur associée à la clé 'c' dans 'tab'
    return txt


if __name__ == "__main__":
    print("Testing encoder_txt ...")
    assert encoder_txt({'e': '0', 'x': '10', 't': '11'}, 'texte') == '11010110'


def code(texte):
    """
    Cette fonction prend en paramètre une chaîne de caractères 'texte'
    et renvoie un dictionnaire 'table' où les clés sont les caractères de la chaîne
    et les valeurs, le code binaire de chaque caractère, et le texte encodé.
    """
    if texte == '':  # Cas du texte vide
        return None
    dic = compte(texte)  # Initialise la variable 'dic' à un dictionnaire d’occurrence des caractères de 'texte'
    arbre = creer_arbre(
        dic)  # Initialise la variable 'arbre' à un arbre binaire des occurrences des caractères de 'texte'
    table = creer_table(
        arbre)  # Initialise la variable 'table' à un dictionnaire des codes binaires des caractères de 'texte'
    return table, encoder_txt(table, texte)

def decoder_txt(tab, texte):
    """
    Cette fonction prend en paramètre un dictionnaire 'tab' et une chaîne
    de nombres binaire 'texte' et renvoie le texte décodé.
    """
    txt = ''
    num = ''
    for c in texte:  # Parcours chaque caractère du texte
        num += c  # Ajoute le caractère dans 'num'
        for item in tab.items():  # Parcours chaque tuples (clé, valeur) de 'tab'
            if num == item[1]:  # Si num est égale à l'une des valeurs de 'tab'
                txt += item[0]  # Ajoute la clé associée à cette valeur dans txt
                num = ''  # Reset la variable afin de passer au caractère suivant du texte d'origine
    return txt


if __name__ == "__main__":
    print("Testing decoder_txt ...")
    assert decoder_txt({'e': '0', 'x': '10', 't': '11'}, '11010110') == 'texte'


def save_file(path, s):
    """
    sauvegarde une string (format ascii) dans un fichier, grâce au chemin fourni.
    paramètre path: chemin d'accès du fichier
    paramètre s: string à sauvegarder
    :return: None
    """
    file_bytes = s.encode("cp437")
    with open(path, "wb") as fichier:
        fichier.write(file_bytes)


def load_file(path):
    """
    crèe un string (format ascii) en ouvrant un fichier, grâce au chemin fourni.
    paramètre path: chemin d'accès du fichier
    return: string représentant l'entièretée du fichier.
    """
    with open(path, "rb") as fichier:
        file_string = fichier.read().decode("cp437")
    return file_string


def bin_to_int(s):
    """
    Permet de convertir une chaine caractère (de taille infini) en un seul et unique grand nombre qui pourra être séparé
    en bytes ensuite. Python permet de stocker des nombres infinis
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
    for i in range(len(encodeds) // 8 + 1):
        binstring = ""
        for j in range(8):
            if i == len(encodeds) // 8 and j >= len(encodeds) % 8:
                for _ in range(8 - len(encodeds) % 8):
                    binstring += "0"
                break
            binstring += encodeds[i * 8 + j]
        bytearr.append(bin_to_int(binstring))

    with open(path, "wb+") as f:
        # header:
        f.write(b"HCS")
        f.write((len(bink) * 3).to_bytes(4, "little"))
        f.write(len(encodeds).to_bytes(4, "little"))

        # table:
        for el in k:
            f.write(len(table[el]).to_bytes(1, "little"))
            f.write(bink[el].to_bytes(len(table[el]//8+1), "little"))
            f.write(el.encode("cp437"))

        # chaine: Convertit un entier en bytes. Le nombre de bytes est calculé de façon à diviser en groupes de 8,
        # avec un groupe minimum. Rappel : le // est prioritaire.
        for i in range(len(encodeds) // 8 + 1):
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
    while n > 0 or s == "":
        s = str(n % 2) + s
        n = n // 2
    return s


def int_to_bin_padding(n, size):
    """
    convertis d'un int vers une chaine de caractère binaire, ajoute des 0 à la fin jusqu'à atteindre
    la taille binaire demandée
    paramètre:
    n: notre int à convertir
    size: la taille finale de notre chaine
    :return: chaine de caractère composée de "0" et de "1"
    """
    s = ""
    while n > 0 or s == "":
        s = str(n % 2) + s
        n = n // 2
        size -= 1
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
    :return: (bink: table de codage, pour décompresser les données data: nos données compressées) ou None si le
    fichier n'est pas valide (aucune vérification n'est faite mise à part l'en-tête du fichier, du moins pour
    l'instant)
    """

    table_retour = {}  # ce sera notre table

    with open(path, "rb") as fichier:
        # read permet de lire n octet.s
        if fichier.read(3) != b"HCS":  # verifier que le fichier soit bien à notre format
            print("Le fichier n'est pas au format HCS")
            return None  # il faudra détecter que la fonction ne retourne pas None.
        taille_table = int.from_bytes(fichier.read(4), "little")
        taille_donnees = int.from_bytes(fichier.read(4), "little")

        for _ in range(taille_table // 3):  # boucle pour récupérer notre table, et en faire un dictionnaire
            taille_cle = int.from_bytes(fichier.read(1), "little")
            cle_binaire = int_to_bin_padding(int.from_bytes(fichier.read(taille_cle//8+1), "little"), taille_cle)
            lettre = fichier.read(1).decode("cp437")

            table_retour[lettre] = cle_binaire

        data = ""
        for _ in range(taille_donnees // 8 + 1):
            data += int_to_bin_padding(int.from_bytes(fichier.read(1), "little"), 8)
    return table_retour, data

if __name__ == "__main__":
    print("Testing code function ...")
    assert code('') is None
    assert code('texte') == ({'e': '0', 'x': '10', 't': '11'}, '11010110')
    
if __name__ == "__main__":
    # Fonction main

    assert main() is None

    # Fonction creer_arbre

    assert creer_arbre({}) is None
    assert creer_arbre({"a": 3, "b": 3}) == Arbre(Arbre(None, None, "a", 3), Arbre(None, None, "b", 3))
