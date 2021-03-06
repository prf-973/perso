"""Carnets d'actions.

Les carnets d'actions - objets de classe `ActionsBook` -
servent à répertorier les actions réalisée sur les dictionnaires
de widgets qui devront se retraduire en actions sur les widgets
eux-mêmes.

Chaque attribut du carnet d'actions correspond à un type d'action,
il prend pour valeur une liste de clés - `WidgetKey` - pour
laquelle l'action est à accomplir.

Pour faciliter leur exploitation, les `ActionsBook` sont
traduits en dictionnaires par la méthode `actionsbook_to_dict`
de la classe `WidgetsDict`.

Les carnets d'actions sont supposés être lus et réinitialisés
après chaque commande, sans quoi ils finiront immanquablement par
contenir des informations contradictoires ou fausses.

"""

class ActionsBook:
    """Classe pour les carnets d'actions.
    
    Attributes
    ----------
    modified : NoGhostKeyList
        Liste de toutes les clés modifiées (excluant les créations
        et les suppressions).
    show : VisibleKeyList
        Liste des clés dont les widgets doivent être rendus visibles.
    show_minus_button : TrueMinusButtonKeyList
        Liste des clés dont le bouton moins doit être rendu visible,
        s'il existe.
    hide : NoGhostKeyList
        Liste des clés dont les widgets doivent être masqués.
    hide_minus_button : TrueMinusButtonKeyList
        Liste des clés dont le bouton moins doit être masqué, s'il existe.
    create : NoGhostKeyList
        Liste des clés dont les widgets doivent être créés.
    move : NoGhostKeyList
        Liste des clés dont les widgets doivent être déplacés dans la grille.
    languages : NoGhostKeyList
        Liste des clés dont le menu des langues doit être mis à jour.
    units : NoGhostKeyList
        Liste des clés dont le menu des unités doit être mis à jour.
    sources : NoGhostKeyList
        Liste des clés dont le menu des sources doit être mis à jour.
    thesaurus : NoGhostKeyList
        Liste des clés dont la liste de valeurs doit être recalculée.
    drop : NoGhostKeyList or KeyList
        Liste des clés dont les widgets doivent être supprimés. `drop`
        est une liste sans fantômes (:py:class:`NoGhostKeyList`),
        sauf si le carnet d'actions a été initialisé avec le paramètre
        `allow_ghosts` valant ``True``.
    update : NoGhostKeyList
        Liste de clés dont les valeurs doivent être mises à jour.

    Parameters
    ----------
    allow_ghosts : bool, default False
        La liste de l'attribut `drop` peut-elle contenir des clés
        fantômes ? D'une manière générale, ce paramètre ne devrait pas
        être utilisé, car `drop` risquerait de contenir des clés qui
        ne sont pas référencées dans le dictionnaire de widgets. Il
        sert lorsque des clés non fantômes (et donc potentiellement
        référencées) deviennent des fantômes (et doivent donc être
        déréférencées), soit essentiellement pour la méthode
        :py:meth:`plume.rdf.widgetkey.RootKey.clean`.
    
    """
    
    def __init__(self, allow_ghosts=False):
        self.modified = NoGhostKeyList(actionsbook=self)
        self.show = VisibleKeyList(actionsbook=self, erase=['hide',
            'show_minus_button'])
        self.show_minus_button = TrueMinusButtonKeyList(actionsbook=self,
            erase=['hide_minus_button'])
        self.hide = NoGhostKeyList(actionsbook=self, erase=['show',
            'show_minus_button', 'hide_minus_button'])
        self.hide_minus_button = TrueMinusButtonKeyList(actionsbook=self,
            erase=['show_minus_button'])
        self.create = NoGhostKeyList(actionsbook=self, erase=['show',
            'show_minus_button', 'hide', 'hide_minus_button', 'move',
            'languages', 'units', 'sources', 'thesaurus', 'modified',
            'update'])
        self.move = NoGhostKeyList(actionsbook=self)
        self.languages = NoGhostKeyList(actionsbook=self)
        self.units = NoGhostKeyList(actionsbook=self)
        self.sources = NoGhostKeyList(actionsbook=self)
        self.thesaurus = NoGhostKeyList(actionsbook=self)
        self.update = NoGhostKeyList(actionsbook=self)
        l=['show', 'show_minus_button', 'hide', 'hide_minus_button',
            'create', 'move', 'languages', 'units', 'sources',
            'thesaurus', 'modified', 'update']
        if allow_ghosts:
            self.drop = KeyList(actionsbook=self, erase=l)
        else:
            self.drop = NoGhostKeyList(actionsbook=self, erase=l)

    def __bool__(self):
        return sum(len(getattr(self, a)) for a in self.__dict__.keys()) > 0


class KeyList(list):
    """Liste de clés.
    
    Parameters
    ----------
    actionsbook : ActionsBook
        Le carnet d'actions auquel appartient la liste.
    erase : list of str, optional
        La liste des attributs où la clé doit être supprimée
        dès lors qu'elle apparaît dans la présente liste.
    
    Attributes
    ----------
    actionsbook : ActionsBook
        Le carnet d'actions auquel appartient la liste. Cet
        attribut sert à croiser les listes pour veiller
        à leur cohérence.
    erase : list of str
        La liste des attributs où la clé doit être supprimée
        dès lors qu'elle apparaît dans la présente liste.
    
    Notes
    -----
    Les clés en cours d'initialisation ne sont jamais
    ajoutées aux listes de clés.
    
    """
    def __init__(self, actionsbook, erase=None):
        self.actionsbook = actionsbook
        self.erase = erase or []
        super().__init__(self)
    
    def append(self, value):
        if not value._is_unborn:
            if not value in self and \
                not value in self.actionsbook.create:
                super().append(value)
            if not value in self.actionsbook.modified \
                and not value in self.actionsbook.create \
                and not value in self.actionsbook.drop:
                self.actionsbook.modified.append(value)
            for a in self.erase:
                l = getattr(self.actionsbook, a)
                if value in l:
                    l.remove(value)

class NoGhostKeyList(KeyList):
    """Liste de clés garantie sans fantôme.
    
    """
    def append(self, value):
        if value:
            super().append(value)

class VisibleKeyList(NoGhostKeyList):
    """Liste de clés garanties visibles.
    
    """
    def append(self, value):
        if not value.is_hidden:
            super().append(value)

class TrueMinusButtonKeyList(VisibleKeyList):
    """Liste de clés garanties visibles et avec un bouton moins.
    
    Ceci ne présage pas de la visibilité du bouton moins
    lui-même.
    
    """
    def append(self, value):
        if value.has_minus_button:
            super().append(value)


