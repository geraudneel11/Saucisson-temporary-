# ============================================================
# OPTIONS DU JEU : langue (FR/EN), touches re-mappables,
# musique/sons on-off, sauvegarde dans settings.json
# Langue par defaut : ANGLAIS. tr(x) renvoie la bonne langue.
# ============================================================
import json
import os
import pygame

LANGUE = "en"          # "en" (defaut) ou "fr"
MUSIQUE_ACTIF = True
SONS_ACTIF = True

CHEMIN_REGLAGES = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "settings.json")

TOUCHES = {
    "gauche": pygame.K_q,
    "droite": pygame.K_d,
    "haut": pygame.K_z,
    "bas": pygame.K_s,
    "interaction": pygame.K_e,
    "attaque": None,          # clic gauche natif ; touche en plus
    "mute": pygame.K_m,
}
TOUCHES_DEFAUT = dict(TOUCHES)
ORDRE_TOUCHES = ("gauche", "droite", "haut", "bas", "interaction",
                 "attaque", "mute")

TRAD = {
    "PLAY": ("PLAY", "JOUER"),
    "SETTINGS": ("SETTINGS", "REGLAGES"),
    "QUIT": ("QUIT", "QUITTER"),
    "BACK": ("BACK", "RETOUR"),
    "CONTINUE": ("CONTINUE", "CONTINUER"),
    "WITH SAVE": ("WITH SAVE", "AVEC SAUVEGARDE"),
    "WITHOUT SAVE": ("WITHOUT SAVE", "SANS SAUVEGARDE"),
    "DEV MODE": ("DEV MODE", "MODE DEV"),
    "HITBOXES": ("HITBOXES", "HITBOXES"),
    "MUSIC": ("MUSIC", "MUSIQUE"),
    "SOUND": ("SOUND", "SONS"),
    "LANGUAGES": ("LANGUAGES", "LANGUES"),
    "KEYS": ("KEYS", "TOUCHES"),
    "ON": ("ON", "ON"),
    "OFF": ("OFF", "OFF"),
    "RESET": ("RESET", "REINITIALISER"),
    "CHANGE": ("CHANGE", "CHANGER"),
    "HARDCORE MODE": ("HARDCORE MODE", "MODE HARDCORE"),
    "LEVEL": ("LEVEL", "NIVEAU"),
    "WAVE": ("WAVE", "VAGUE"),
    "LVL": ("LVL", "NIV"),
    "SHOP": ("SHOP", "BOUTIQUE"),
    "COINS:": ("COINS:", "PIECES :"),
    "SKILLS: LVL {}": ("SKILLS: LVL {}", "COMPETENCES : NIV {}"),
    "LOADING": ("LOADING", "CHARGEMENT"),
    "YOU ARE DEAD": ("YOU ARE DEAD", "VOUS ETES MORT"),
    "RESPAWN": ("RESPAWN", "REAPPARAITRE"),
    "TO DELETE A SAVE, DELETE ITS JSON FILE": (
        "TO DELETE A SAVE, DELETE ITS JSON FILE",
        "POUR SUPPRIMER UNE SAUVEGARDE, SUPPRIME SON FICHIER JSON"),
    "F1 TO SHOW IN GAME - MAX 15": (
        "F1 TO SHOW IN GAME - MAX 15",
        "F1 POUR AFFICHER EN JEU - MAX 15"),
    "GAME LANGUAGE: {}": ("GAME LANGUAGE: {}",
                          "LANGUE ACTUELLE DU JEU : {}"),
    "PRESS ANY KEY...": ("PRESS ANY KEY...", "APPUIEZ SUR UNE TOUCHE..."),
    "VAGUES": ("WAVES", "VAGUES"),
    "BOUTIQUE": ("SHOP", "BOUTIQUE"),
    "MAISON": ("HOUSE", "MAISON"),
    "CHAPELLE": ("CHAPEL", "CHAPELLE"),
    "LEFT": ("LEFT", "GAUCHE"),
    "RIGHT": ("RIGHT", "DROITE"),
    "UP": ("UP", "HAUT"),
    "DOWN": ("DOWN", "BAS"),
    "INTERACT": ("INTERACT", "INTERAGIR"),
    "ATTACK": ("ATTACK", "ATTAQUE"),
    "MUTE": ("MUTE", "MUET"),
    "LEFT CLICK": ("LEFT CLICK", "CLIC GAUCHE"),
    "RIGHT CLICK": ("RIGHT CLICK", "CLIC DROIT"),
    "SPACE": ("SPACE", "ESPACE"),
    "ESCAPE": ("ESCAPE", "ECHAP"),
    "TAB": ("TAB", "TAB"),
    "RETURN": ("ENTER", "ENTREE"),
    "BACKSPACE": ("BACKSPACE", "RET. ARRIERE"),
    "VITESSE JOUEUR": ("PLAYER SPEED", "VITESSE JOUEUR"),
    "FORCE JOUEUR": ("PLAYER STRENGTH", "FORCE JOUEUR"),
    "PV ENNEMIS (BASE)": ("ENEMY HP (BASE)", "PV ENNEMIS (BASE)"),
    "DEGATS ENNEMIS (BASE)": ("ENEMY DAMAGE (BASE)",
                              "DEGATS ENNEMIS (BASE)"),
    "VITESSE ENNEMIS (BASE)": ("ENEMY SPEED (BASE)",
                               "VITESSE ENNEMIS (BASE)"),
    "OR DE DEPART": ("STARTING GOLD", "OR DE DEPART"),
    "NIV. COMPETENCES": ("SKILL LEVEL", "NIV. COMPETENCES"),
    "POTIONS DE DEPART": ("STARTING POTIONS", "POTIONS DE DEPART"),
    "LIEU D'APPARITION": ("SPAWN LOCATION", "LIEU D'APPARITION"),
    "TAUX POMMES (%)": ("APPLE RATE (%)", "TAUX POMMES (%)"),
    "TAUX POMMES DOREES (%)": ("GOLDEN APPLE RATE (%)",
                               "TAUX POMMES DOREES (%)"),
    "IMMORTALITE": ("IMMORTALITY", "IMMORTALITE"),
    "SPACE KILL": ("SPACE KILL", "SPACE KILL"),
    "Se soigner.": ("Heal myself.", "Se soigner."),
    "Confirmer": ("Confirm", "Confirmer"),
    "Bonjour voyageur. Je me nomme Geovah.": (
        "Hello traveler. My name is Geovah.",
        "Bonjour voyageur. Je me nomme Geovah."),
    "Bienvenue. J'espere pouvoir t'etre utile.": (
        "Welcome. I hope I can be of use to you.",
        "Bienvenue. J'espere pouvoir t'etre utile."),
    "Je soigne les aventuriers qui passent par ici.": (
        "I heal the adventurers who come through here.",
        "Je soigne les aventuriers qui passent par ici."),
    "Tu sembles en pleine forme.": (
        "You seem in great shape.", "Tu sembles en pleine forme."),
    "Tu n'as pas besoin de mes soins.": (
        "You don't need my care.", "Tu n'as pas besoin de mes soins."),
    "Garde ton or, tu en auras besoin.": (
        "Keep your gold, you will need it.",
        "Garde ton or, tu en auras besoin."),
    "Par les anciens... tu tiens encore debout ?": (
        "By the ancients... you're still standing?",
        "Par les anciens... tu tiens encore debout ?"),
    "Tes blessures sont graves.": (
        "Your wounds are serious.", "Tes blessures sont graves."),
    "Tu arrives juste a temps.": (
        "You arrived just in time.", "Tu arrives juste a temps."),
    "Bonjour, que puis-je faire pour toi ?": (
        "Hello, what can I do for you?",
        "Bonjour, que puis-je faire pour toi ?"),
    "Je peux soigner tes blessures.": (
        "I can heal your wounds.", "Je peux soigner tes blessures."),
    "Tu sembles fatigue.": ("You seem tired.", "Tu sembles fatigue."),
    "Au revoir.": ("Goodbye.", "Au revoir."),
    "Prends soin de toi.": ("Take care of yourself.",
                            "Prends soin de toi."),
    "Que les dieux te protegent.": ("May the gods protect you.",
                                    "Que les dieux te protegent."),
    "Bonne chance.": ("Good luck.", "Bonne chance."),
    "Reviens quand tu voudras.": ("Come back whenever you like.",
                                  "Reviens quand tu voudras."),
    "Acheter": ("Buy", "Acheter"),
    "La case est vide": ("Slot is empty", "La case est vide"),
    "Rupture de stock.": ("Out of stock.", "Rupture de stock."),
    "Salut guerrier, comment vas-tu ?": (
        "Hi warrior, how are you?", "Salut guerrier, comment vas-tu ?"),
    "Salut, moi c'est Languillan. Je suis marchand et apprenti alchimiste.": (
        "Hi, I'm Languillan. I'm a merchant and apprentice alchemist.",
        "Salut, moi c'est Languillan. Je suis marchand et apprenti "
        "alchimiste."),
    "Cela faisait longtemps que je n'avait pas vu de guerriers.": (
        "It had been a long time since I'd seen warriors.",
        "Cela faisait longtemps que je n'avait pas vu de guerriers."),
    "Te revoila, j'ai fais le plein de produits.": (
        "There you are, I've restocked my goods.",
        "Te revoila, j'ai fais le plein de produits."),
    "Je dois m'absenter un moment. Affaire importante, tu vois ?": (
        "I have to step away for a moment. Important business, you see?",
        "Je dois m'absenter un moment. Affaire importante, tu vois ?"),
    "Je pars en voyage des demain... retrouvez-moi apres votre prochaine victoire.": (
        "I'm leaving on a trip tomorrow... meet me after your next victory.",
        "Je pars en voyage des demain... retrouvez-moi apres votre "
        "prochaine victoire."),
    "Que puis-je faire pour toi ?": (
        "What can I do for you?", "Que puis-je faire pour toi ?"),
    "Achetez d'abord l'armure precedente.": (
        "Buy the previous armor first.",
        "Achetez d'abord l'armure precedente."),
    "Vous n'avez pas assez d'or.": (
        "You don't have enough gold.", "Vous n'avez pas assez d'or."),
    "Vous achetez {} !": ("You buy {} !", "Vous achetez {} !"),
    "Vous achetez {}.": ("You buy {}.", "Vous achetez {}."),
    "Votre inventaire est plein.": (
        "Your inventory is full.", "Votre inventaire est plein."),
    "Tu équipes {} !": ("Equipped {} !", "Tu équipes {} !"),
    "Vous ne pouvez lancer la dynamite que dans le monde.": (
        "You can only throw the dynamite in the world.",
        "Vous ne pouvez lancer la dynamite que dans le monde."),
    "{}: {} or": ("{}: {} gold", "{} : {} or"),
    "{} (Rupture de stock)": ("{} (Out of stock)",
                              "{} (Rupture de stock)"),
    "MOINE": ("MONK", "MOINE"),
    "Payer (1 or)": ("Pay (1 gold)", "Payer (1 or)"),
    "Bonjour voyageur. Je veille sur ces ouvrages depuis de nombreuses annees.": (
        "Hello traveler. I have watched over these books for many years.",
        "Bonjour voyageur. Je veille sur ces ouvrages depuis de "
        "nombreuses annees."),
    "Contre une piece d'or, tu peux consulter notre bibliotheque.": (
        "For one gold coin, you can consult our library.",
        "Contre une piece d'or, tu peux consulter notre bibliotheque."),
    "Il te faut au moins une piece d'or pour consulter les livres.": (
        "You need at least one gold coin to read the books.",
        "Il te faut au moins une piece d'or pour consulter les livres."),
    "Nos ouvrages n'attendent que toi.": (
        "Our books are waiting for you.",
        "Nos ouvrages n'attendent que toi."),
    "Que la lecture t'ait ete profitable.": (
        "May this reading have served you well.",
        "Que la lecture t'ait ete profitable."),
    "Tu souhaites de nouveau consulter les livres ?": (
        "Want to read the books again?",
        "Tu souhaites de nouveau consulter les livres ?"),
    "Botanique : les pommes": ("Botany: apples", "Botanique : les pommes"),
    "Guide de certaines mécaniques": ("Guide to some mechanics",
                                      "Guide de certaines mécaniques"),
    "Les pommiers sont des arbres communs dans ce monde. On en trouve dans les villages, les vergers et parfois meme à l’etat sauvage. Pourtant, ils entretiennent un lien etrange avec la magie. Lorsqu’une ame s’envole pres d’un pommier, l’arbre semble en garder une trace, melee a sa seve. Mais lorsque trois": (
        "Apple trees are common trees in this world. They can be found "
        "in villages, orchards and sometimes even in the wild. Yet they "
        "hold a strange bond with magic. When a soul flies away near an "
        "apple tree, the tree seems to keep a trace of it, mixed into "
        "its sap. But when three",
        "Les pommiers sont des arbres communs dans ce monde. On en "
        "trouve dans les villages, les vergers et parfois meme à "
        "l’etat sauvage. Pourtant, ils entretiennent un lien etrange "
        "avec la magie. Lorsqu’une ame s’envole pres d’un pommier, "
        "l’arbre semble en garder une trace, melee a sa seve. Mais "
        "lorsque trois"),
    "ames s’envolent a proximite du meme arbre, il peut alors produire un fruit impregne de magie. Ces fruits sont rares et leur pouvoir varie selon les emes qui ont nourri l’arbre. Certains peuvent guerir, d’autres transmettre un pouvoir ou provoquer des phenomenes inexplicables. Ainsi, derriere leur apparence": (
        "souls fly away near the same tree, it can then produce a fruit "
        "steeped in magic. These fruits are rare and their power varies "
        "with the souls that fed the tree. Some can heal, others pass on "
        "a power or trigger unexplainable phenomena. Thus, behind their "
        "ordinary look,",
        "ames s’envolent a proximite du meme arbre, il peut alors "
        "produire un fruit impregne de magie. Ces fruits sont rares et "
        "leur pouvoir varie selon les emes qui ont nourri l’arbre. "
        "Certains peuvent guerir, d’autres transmettre un pouvoir ou "
        "provoquer des phenomenes inexplicables. Ainsi, derriere leur "
        "apparence"),
    "ordinaire, les pommiers cachent une capacite que peu de personnes connaissent.": (
        "apple trees hide an ability few people know about.",
        "ordinaire, les pommiers cachent une capacite que peu de "
        "personnes connaissent."),
    "DIVINITE": ("DEITY", "DIVINITE"),
    "Competences": ("Skills", "Competences"),
    "Force": ("Strength", "Force"),
    "PV max": ("MAX HP", "PV max"),
    "Slots": ("SLOTS", "SLOTS"),
    "Items par slot": ("ITEMS PER SLOT", "ITEMS PAR SLOT"),
    "Degats d'attaque.": ("Attack damage.", "Degats d'attaque."),
    "Emplacements d'inventaire.": ("Inventory slots.",
                                   "Emplacements d'inventaire."),
    "Items max par slot.": ("Max items per slot.",
                            "Items max par slot."),
    "Points de vie maximum.": ("Maximum health points.",
                               "Points de vie maximum."),
    "L'autel frissonne. La divinite te regarde, voyageur.": (
        "The altar shivers. The deity is watching you, traveler.",
        "L'autel frissonne. La divinite te regarde, voyageur."),
    "Les dieux t'attendent, toujours.": (
        "The gods await you, always.", "Les dieux t'attendent, toujours."),
    "Que ma lumiere veille sur ta route, enfant.": (
        "May my light watch over your path, child.",
        "Que ma lumiere veille sur ta route, enfant."),
    "Reviens quand ton ame cherchera a grandir.": (
        "Come back when your soul seeks to grow.",
        "Reviens quand ton ame cherchera a grandir."),
    "Tu sens un regard bienveillant poser sur toi...": (
        "You feel a kind gaze resting on you...",
        "Tu sens un regard bienveillant poser sur toi..."),
    "Une presence ancienne s'eveille a ton approche...": (
        "An ancient presence awakens at your approach...",
        "Une presence ancienne s'eveille a ton approche..."),
    "Niv. {}": ("Lvl. {}", "Niv. {}"),
    "Cout : {} niv": ("Cost: {} lvl", "Cout : {} niv"),
    "Cout : {} XP": ("Cost: {} XP", "Cout : {} XP"),
    "{} sur {}": ("{} of {}", "{} sur {}"),
    "little heal potion": ("small healing potion",
                           "petite potion de soin"),
    "dynamite": ("dynamite", "dynamite"),
    "Retour": ("BACK", "Retour"),
    "Quitter": ("QUIT", "Quitter"),
    "POMMIER": ("APPLE TREE", "POMMIER"),
    "PORTAIL": ("PORTAL", "PORTAIL"),
    "Bienvenue. Je peux te vendre ce que tu veux.": (
        "Welcome. I can sell you whatever you want.",
        "Bienvenue. Je peux te vendre ce que tu veux."),
}
_INDEX = {}
for _en, _fr in TRAD.values():
    _INDEX[_en] = (_en, _fr)
    _INDEX[_fr] = (_en, _fr)


def set_langue(langue):
    global LANGUE
    LANGUE = "fr" if langue == "fr" else "en"


def tr(texte):
    """Renvoie le texte dans la langue courante (defaut : anglais).
    Accepte une chaine source en FR ou EN (index bilingue)."""
    paire = _INDEX.get(texte) or TRAD.get(texte)
    if paire is None:
        return texte
    return paire[1] if LANGUE == "fr" else paire[0]


def nom_touche(code):
    """Nom lisible d'une touche (code pygame.K_x) dans la langue
    courante ; None = action a la souris."""
    if code is None:
        return ""
    return tr(pygame.key.name(code).upper())


def touches_conflit():
    """Renvoie {code: [actions...]} pour les touches utilisees par
    2 actions ou plus."""
    vu = {}
    for action in ORDRE_TOUCHES:
        code = TOUCHES.get(action)
        if code is None:
            continue
        vu.setdefault(code, []).append(action)
    return {c: a for c, a in vu.items() if len(a) >= 2}


def action_en_conflit(action):
    """True si la touche de cette action est partagee avec une autre."""
    code = TOUCHES.get(action)
    if code is None:
        return False
    return len(touches_conflit().get(code, [])) >= 2


def reinitialiser_touches():
    global TOUCHES
    TOUCHES = dict(TOUCHES_DEFAUT)
    sauver()


def sauver():
    """Ecrit settings.json (langue, musique, sons, touches)."""
    data = {"langue": LANGUE, "musique": MUSIQUE_ACTIF,
            "sons": SONS_ACTIF, "touches": dict(TOUCHES)}
    with open(CHEMIN_REGLAGES, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=True, indent=2)


def charger():
    """Lit settings.json s'il existe et applique les valeurs."""
    global LANGUE, MUSIQUE_ACTIF, SONS_ACTIF, TOUCHES
    if not os.path.exists(CHEMIN_REGLAGES):
        return
    try:
        with open(CHEMIN_REGLAGES, encoding="utf-8") as f:
            data = json.load(f)
    except (ValueError, OSError):
        return
    set_langue(data.get("langue", "en"))
    MUSIQUE_ACTIF = bool(data.get("musique", True))
    SONS_ACTIF = bool(data.get("sons", True))
    t = data.get("touches", {})
    for action in ORDRE_TOUCHES:
        if action in t:
            TOUCHES[action] = t[action]