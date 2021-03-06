"""Utilitaires.

"""
import re
from pathlib import Path
from uuid import UUID, uuid4
from html import escape
from datetime import datetime, date, time
from locale import setlocale, LC_NUMERIC, str as locstr
from decimal import Decimal

from plume import __path__
from plume.rdf.rdflib import Literal, URIRef, from_n3, Graph
from plume.rdf.namespaces import RDF, DCAT, XSD

crs_ns = {
    'EPSG': 'http://www.opengis.net/def/crs/EPSG/0/',
    'OGC': 'http://www.opengis.net/def/crs/OGC/1.3/',
    'IGNF': 'https://registre.ign.fr/ign/IGNF/IGNF.xml#'
    }
"""Espaces de nommage des référentiels de coordonnées.

"""

class DatasetId(URIRef):
    """Identifiant de jeu de données.
    
    Parameters
    ----------
    *uuids : str or UUID or rdflib.term.URIRef
        UUID ou chaînes de caractères ou IRI présumés correspondre
        à un UUID. Le premier élément qui s'avère être réellement
        un UUID est conservé. Si aucun n'est valide ou si l'argument
        n'est pas fourni, un nouvel UUID est utilisé pour créer
        l'identifiant.
    
    Attributes
    ----------
    uuid : uuid.UUID
        Représentation de l'identifiant sous forme d'UUID.
    
    Examples
    --------
    >>> DatasetId('4dc72616-7235-461f-95cf-94dfc3cfa629', 
    ...     'urn:uuid:2b4bb94a-c10b-4d99-a0e7-4ee28888e4f4')
    DatasetId('urn:uuid:4dc72616-7235-461f-95cf-94dfc3cfa629')

    >>> DatasetId('pas un UUID', 
    ...     'urn:uuid:2b4bb94a-c10b-4d99-a0e7-4ee28888e4f4')
    DatasetId('urn:uuid:2b4bb94a-c10b-4d99-a0e7-4ee28888e4f4')
    
    >>> DatasetId()
    DatasetId('urn:uuid:...')
    
    """
    def __new__(cls, *uuids):
        if uuids:
            for uuid in uuids:
                if isinstance(uuid, DatasetId):
                    return uuid
                try:
                    u = UUID(str(uuid))
                    return super().__new__(cls, u.urn)
                except:
                    continue
        return super().__new__(cls, uuid4().urn)
    
    def __init__(self, *uuids):
        self.uuid = UUID(str(self))

def data_from_file(filepath):
    """Renvoie le contenu d'un fichier.
    
    Le fichier sera présumé être encodé en UTF-8 et mieux
    vaudrait qu'il le soit.
    
    On pourra utiliser conjointement :py:func:`abspath` pour
    l'import de données du modèle:
    
        >>> data_from_file(abspath('pg/tests/samples/pg_description_1.txt'))
    
    Parameters
    ----------
    filepath : str
        Chemin complet du fichier source.
    
    Returns
    -------
    str
    
    See Also
    --------
    graph_from_file : Import de données RDF.
    
    """
    pfile = Path(filepath)
    
    if not pfile.exists():
        raise FileNotFoundError("Can't find file {}.".format(filepath))
        
    if not pfile.is_file():
        raise TypeError("{} is not a file.".format(filepath))
    
    with pfile.open(encoding='UTF-8') as src:
        data = src.read()
    return data

def abspath(relpath):
    """Déduit un chemin absolu d'un chemin relatif au package.
    
    Parameters
    ----------
    relpath (str):
        Chemin relatif au package. Il n'est ni nécessaire ni
        judicieux d'utiliser la syntaxe Windows à base
        d'antislashs.
    
    Returns
    -------
    pathlib.Path
    
    Examples
    --------
    >>> abspath('rdf/data/vocabulary.ttl')
    WindowsPath('C:/Users/Alhyss/Documents/GitHub/metadata-postgresql/plume/rdf/data/vocabulary.ttl')
    
    """
    return Path(__path__[0]) / relpath

def sort_by_language(litlist, langlist):
    """Trie une liste selon les langues de ses valeurs.
    
    Parameters
    ----------
    litlist : list(rdflib.term.Literal)
        Une liste de valeurs litérales, présumées de type
        ``xsd:string`` ou ``rdf:langString``.
    langlist : list(str) or tuple(str)
        Une liste de langues, triées par priorité décroissante.

    """
    litlist.sort(key=lambda v: langlist.index(v.language) \
        if isinstance(v, Literal) and v.language in langlist else 9999)

def pick_translation(litlist, langlist):
    """Renvoie l'élément de la liste dont la langue est la mieux adaptée.
    
    Parameters
    ----------
    litlist : list(rdflib.term.Literal)
        Une liste de valeurs litérales, présumées de type
        ``xsd:string`` ou ``rdf:langString``.
    langlist : list(str) or tuple(str) or str
        Une langue ou une liste de langues triées par priorité
        décroissante.
    
    Returns
    -------
    rdflib.term.Literal
        Un des éléments de `litlist`, qui peut être :
        
        * le premier dont la langue est la première valeur
          de `langlist` ;
        * le premier dont la langue est la deuxième valeur
          de `langlist` ;
        * et ainsi de suite jusqu'à épuisement de `langlist` ;
        * à défaut, le premier élément de `litlist`.

    Notes
    -----
    Cette fonction peut ne pas renvoyer un objet de classe
    :py:class:`rdflib.term.Literal` si `litlist` ne contenait
    que des valeurs non litérales.

    """
    if not litlist:
        return
    if not isinstance(langlist, (list, tuple)):
        langlist = [langlist] if langlist else []
    
    val = None
    
    for language in langlist:
        for l in litlist:
            if isinstance(l, Literal) and l.language == language:
                val = l
                break
        if val:
            break
    
    if val is None:
        # à défaut, on prend la première valeur de la liste
        val = litlist[0]
        
    return val

def main_datatype(values):
    """Renvoie le type de littéral pré-dominant d'une liste de valeurs.
    
    Parameters
    ----------
    values : list(rdflib.term.Literal or rdflib.term.URIRef or rdflib.term.BNode)
        Une liste de valeurs.
    
    Returns
    -------
    rdflib.term.URIRef
        Un type de valeur littérale, sous la forme d'un
        IRI RDF.
    
    Notes
    -----
    La fonction renvoie ``None`` si la liste ne contenait aucune
    valeur littérale (y compris pour une liste vide).
    Sinon, le type sera :
    
        * ``rdf:langString`` si la liste contient au moins une
          valeur littérale dont la langue est déclarée.
        * Si toutes les valeurs sont littérales et de même type,
          ledit type.
        * ``xsd:decimal`` si toutes les valeurs sont littérales
          et de type ``xsd:decimal`` ou ``xsd:integer``.
        * ``xsd:dateTime`` si toutes les valeurs sont littérales
          et de type ``xsd:date`` ou ``xsd:dateTime``.
        * ``xsd:string`` dans tous les autres cas.
    
    """
    datatype = None
    other = False
    for v in values:
        if isinstance(v, Literal):
            if other:
                return XSD.string
            vdt = RDF.langString if v.language else (v.datatype or XSD.string)
            if not datatype:
                datatype = vdt
            elif datatype != vdt:
                if datatype in (XSD.decimal, XSD.integer) \
                    and vdt in (XSD.decimal, XSD.integer):
                        datatype = XSD.decimal
                elif datatype in (XSD.date, XSD.dateTime) \
                    and vdt in (XSD.date, XSD.dateTime):
                        datatype = XSD.dateTime
                elif datatype == RDF.langString or vdt == RDF.langString:
                    return RDF.langString
                else:
                    return XSD.string
        else:
            other = True
    return datatype

def path_n3(path, nsm):
    """Renvoie la représentation N3 d'un chemin d'IRI.
    
    Parameters
    ----------
    path : rdflib.term.URIRef or rdflib.paths.Path
        Un chemin d'IRI.
    nsm : plume.rdf.namespaces.PlumeNamespaceManager
        Un gestionnaire d'espaces de nommage.
    
    Returns
    -------
    str
    
    Notes
    -----
    RDFLib propose bien une méthode :py:meth:`rdflib.paths.Path.n3`
    pour transformer les chemins d'IRI... mais elle ne prend pas
    d'espace de nommage en argument à ce stade (v 6.0.1). Son
    autre défaut est d'écrire les chemins sans espaces avant et
    après les slashs.
    
    """
    if isinstance(path, URIRef):
        return path.n3(nsm)
    return ' / '.join(path_n3(c, nsm) for c in path.args)

def path_from_n3(path_n3, nsm):
    """Renvoie un chemin d'IRI reconstruit à partir de sa représentation N3.
    
    Parameters
    ----------
    path_n3 : str
        Représentation N3 d'un chemin d'IRI. Les préfixes
        utilisés doivent impérativement être ceux du
        gestionnaire d'espaces de nommage, et a fortiori de
        Plume (:py:data:`plume.rdf.namespaces.namespaces`).
    nsm : plume.rdf.namespaces.PlumeNamespaceManager
        Un gestionnaire d'espaces de nommage.
    
    Returns
    -------
    URIRef or rdflib.paths.Path
        Le chemin d'IRI. ``None`` si la reconstruction a
        échoué, soit parce que `path_n3` n'était pas
        vraiment la représentation N3 d'un chemin d'IRI,
        soit parce que tous les préfixes utilisés n'ont pas
        été reconnus.
    
    """
    namespaces = nsm.namespaces()
    l = re.split(r"\s*[/]\s*", path_n3)
    path = None
    for elem in l:
        try:
            iri = from_n3(elem, nsm=nsm)
        except:
            return
        path = (path / iri) if path else iri
    return path

def forbidden_char(anystr):
    """Le cas échéant, renvoie le premier caractère de la chaîne qui ne soit pas autorisé dans un IRI.
    
    Parameters
    ----------
    anystr : str
        La chaîne de caractères à tester.
    
    Returns
    -------
    str
        Si la chaîne contient au moins un caractère interdit, l'un
        de ces caractères.
    
    Examples
    --------
    >>> forbidden_char('avec des espaces')
    ' '
    
    """
    r = re.search(r'([<>"\s{}|\\^`])', anystr)
    return r[1] if r else None

def text_with_link(anystr, anyiri):
    """Génère un fragment HTML définissant un lien.
    
    Parameters
    ----------
    anystr : str
        La chaîne de caractères porteuse du lien.
    anyiri : rdflib.term.URIRef
        Un IRI quelconque correspondant à la cible du lien.
    
    Returns
    -------
    str
        Une chaîne de caractère correspondant à un élément A,
        qui sera interprétée par les widgets comme du texte riche.
    
    Examples
    --------
    >>> text_with_link(
    ...     "Documentation de PostgreSQL 10",
    ...     URIRef("https://www.postgresql.org/docs/10/index.html")
    ...     )
    '<A href="https://www.postgresql.org/docs/10/index.html">Documentation de PostgreSQL 10</A>'
    
    """
    return """<a href="{}">{}</a>""".format(
        escape(str(anyiri), quote=True),
        escape(anystr, quote=True)
        )
    
def email_from_owlthing(thing_iri):
    """Renvoie la transcription sous forme de chaîne de caractères d'un IRI représentant une adresse mél.

    Cette fonction très basique se contente de retirer le préfixe
    "mailto:" s'il était présent.

    Parameters
    ----------
    thing_iri : rdflib.term.URIRef
        IRI supposé correspondre à une adresse mél (classe
        RDF  ``owl:Thing``).

    Returns
    -------
    str

    Examples
    --------
    >>> email_from_owlthing(URIRef('mailto:jon.snow@the-wall.we'))
    'jon.snow@the-wall.we'
    
    """
    # à partir de Python 3.9
    # str(thingIRI).removeprefix("mailto:") serait plus élégant
    return re.sub('^mailto[:]', '', str(thing_iri))

def owlthing_from_email(email_str):
    """Construit un IRI valide à partir d'une chaîne de caractères représentant une adresse mél.

    La fonction ne fait aucun contrôle de validité sur l'adresse si ce
    n'est vérifier qu'elle ne contient aucun caractère interdit pour
    un IRI.

    Parameters
    ----------
    email_str : str
        Une chaîne de caractère supposée correspondre à une adresse mél.

    Returns
    -------
    rdflib.term.URIRef
        Un IRI respectant grosso modo le schéma officiel des URI pour
        les adresses mél : ``mailto:<email>``.

    Examples
    --------
    >>> owlthing_from_email('jon.snow@the-wall.we')
    rdflib.term.URIRef('mailto:jon.snow@the-wall.we')
    
    """
    email_str = re.sub('^mailto[:]', '', email_str)
    f = forbidden_char(email_str)
    if f:
        raise ValueError("Le caractère '{}' " \
            "de l'adresse '{}' n'est pas autorisé dans " \
            'un IRI.'.format(f, email_str))
    if email_str:
        return URIRef('mailto:' + email_str)

def tel_from_owlthing(thing_iri):
    """Renvoie la transcription sous forme de chaîne de caractères d'un IRI représentant un numéro de téléphone.

    Contrairement à :py:func:`owlthing_from_tel`, cette fonction très basique
    ne standardise pas la forme du numéro de téléphone. Elle se contente
    de retirer le préfixe ``'tel:'`` s'il était présent.

    Parameters
    ----------
    thing_iri : rdflib.term.URIRef
        IRI supposé correspondre à un numéro de téléphone (classe
        RDF ``owl:Thing``).

    Returns
    -------
    str

    Examples
    --------
    >>> tel_from_owlthing(URIRef('tel:+33-1-23-45-67-89'))
    '+33-1-23-45-67-89'
    
    """
    return re.sub('^tel[:]', '', str(thing_iri))

def owlthing_from_tel(tel_str, add_fr_prefix=True):
    """Construit un IRI valide à partir d'une chaîne de caractères représentant un numéro de téléphone.

    Si le numéro semble être un numéro de téléphone français valide,
    il est standardisé sous la forme ``<tel:+33-x-xx-xx-xx-xx>``.

    Parameters
    ----------
    tel_str : str
        Une chaîne de caractère supposée correspondre à un numéro de téléphone.
    add_fr_prefix : bool, default True
        ``True`` si la fonction doit tenter de transformer les numéros de téléphone
        français locaux ou présumés comme tels (un zéro suivi de neuf chiffres)
        en numéros globaux (``'+33'`` suivi des neuf chiffres). ``True`` par défaut.

    Returns
    -------
    rdflib.term.URIRef
        Un IRI respectant grosso modo le schéma officiel des URI pour les
        numéros de téléphone : ``tel:<phonenumber>``.

    Examples
    --------
    >>> owlthing_from_tel('0123456789')
    rdflib.term.URIRef('tel:+33-1-23-45-67-89')
    
    """
    tel_str = re.sub('^tel[:]', '', tel_str)
    red = re.sub(r'[.\s-]', '', tel_str)
    tel = ''

    if add_fr_prefix:
        a = re.match(r'0(\d{9})$', red)
        # numéro français local
        if a:
            red = '+33' + a[1]
    
    if re.match(r'[+]33\d{9}$', red):
        # numéro français global
        for i in range(len(red)):
            if i == 3 or i > 2 and i%2 == 0:
                tel = tel + "-" + red[i]
            else:
                tel = tel + red[i]
    else:
        tel = re.sub(r'(\d)\s(\d)', r'\1-\2', tel_str).strip(' ')
        # les espaces entre les chiffres sont remplacés par des tirets,
        # ceux en début et fin de chaine sont supprimés
        f = forbidden_char(tel)
        if f:
            raise ValueError("Le caractère '{}' " \
                "du numéro de téléphone '{}' n'est pas autorisé dans " \
                'un IRI.'.format(f, tel_str))
    if tel:
        return URIRef('tel:' + tel)

def int_from_duration(duration):
    """Extrait un nombre entier et son unité d'un littéral représentant une durée.
    
    Cette fonction renvoie ``(None, None)`` si la valeur fournie
    en argument n'était pas un littéral de type ``xsd:duration``
    ou si, parce qu'il n'était pas correctement formé, il n'a pas
    été possible d'en extaire une valeur.
    
    Les durées complexes faisant appel à plusieurs unités sont
    tronquées. La fonction conserve l'entier associé à l'unité
    la plus grande.
    
    Parameters
    ----------
    duration : rdflib.term.Literal
        Un littéral de type ``xsd:duration``.
    
    Returns
    -------
    tuple(int, {'ans', 'mois', 'jours', 'heures', 'min.', 'sec.'})
        Un tuple dont le premier élément est l'entier correspondant
        à la valeur de la durée et le second l'unité de cette
        durée.
    
    Examples
    --------
    >>> int_from_duration(Literal('P2Y', datatype=XSD.duration))
    (2, 'ans')
    
    """
    if not duration or not isinstance(duration, Literal) \
        or not duration.datatype == XSD.duration:
        return (None, None)
    
    r = re.split('T', str(duration).lstrip('P'))
    if len(r) == 2:
        date, time = r
    elif len(r) == 1:
        date, time = (r[0], None)
    else:
        return (None, None)
    
    if date:
        date_map = {'Y': 'ans', 'M': 'mois', 'D': 'jours'}
        for u in date_map.keys():
            r = re.match('([0-9]+){}'.format(u), date)
            if r:
                return (int(r[1]), date_map[u])
    if time:
        time_map = {'H': 'heures', 'M': 'min.', 'S': 'sec.'}
        for u in time_map.keys():
            r = re.match('([0-9]+){}'.format(u), time)
            if r:
                return (int(r[1]), time_map[u])
    return (None, None) 

def duration_from_int(value, unit):
    """Renvoie la représentation RDF d'une durée exprimée sous la forme d'une valeur entière et d'une unité.
    
    Parameters
    ----------
    value : int or str
        La valeur de la durée. Elle peut être de type ``int``
        ou ``str``, tant qu'il s'agit bien d'un nombre. Les
        durées négative sont prises en charge.
    unit : {'ans', 'mois', 'jours', 'heures', 'min.', 'sec.'}
        L'unité de la durée. La fonction renverra ``None``
        si la valeur renseignée n'est pas dans la liste
        des unités prises en charge.
    
    Returns
    -------
    rdflib.term.Literal
        Un littéral de type ``xsd:duration``.
    
    Examples
    --------
    >>> duration_from_int(2, 'ans')
    rdflib.term.Literal('P2Y', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#duration'))
    
    """
    if isinstance(value, str) and re.match('^-?[0-9]+$', value):
        value = int(value)
    if not isinstance(value, int):
        return None
    if value < 0:
        value = - value
        signe = '-'
    else:
        signe = ''
    date_map = {'ans': 'Y', 'mois': 'M', 'jours': 'D'}
    if unit in date_map:
        return Literal('{}P{}{}'.format(signe, value, date_map[unit]),
            datatype=XSD.duration)
    time_map = {'heures': 'H', 'min.': 'M', 'sec.': 'S'}
    if unit in time_map:
        return Literal('{}PT{}{}'.format(signe, value, time_map[unit]),
            datatype=XSD.duration)

def str_from_duration(duration):
    """Représentation d'une durée sous forme de chaîne de caractères.
    
    Parameters
    ----------
    duration : rdflib.term.Literal
        Un littéral de type ``xsd:duration``.
    
    Returns
    -------
    str
    
    Examples
    --------
    >>> str_from_duration(Literal('P2Y', datatype=XSD.duration))
    '2 ans'
    
    Notes
    -----
    Cette fonction produit des valeurs pour un affichage en
    lecture seule. Il n'existe pas de fonction retour pour
    reconstruire un littéral de type ``xsd:duration`` à partir
    d'une représentation de cette forme.
    
    """
    value, unit = int_from_duration(duration)
    if value is None:
        return
    if value in (0, 1, -1) and unit in ('ans', 'jours', 'heures'):
        unit = unit.rstrip('s')
    return '{} {}'.format(value, unit)

def str_from_decimal(decimal):
    """Représentation d'un nombre décimal sous forme de chaîne de caractères.
    
    Parameters
    ----------
    decimal : rdflib.term.Literal
        Un littéral de type ``xsd:decimal``. Les valeurs
        de type ``xsd:integer`` sont tolérées.
    
    Returns
    -------
    str
    
    Examples
    --------
    >>> str_from_decimal(Literal('1.25', datatype=XSD.decimal))
    '1,25'
    
    Notes
    -----
    La fonction renvoie ``None`` pour une valeur mal formée
    ou qui n'est pas un littéral de type ``xsd:decimal``.
    
    Elle prend en compte les paramètres de localisation
    système pour choisir le séparateur (virgule ou
    point) à utiliser.
    
    """
    if decimal is None or not isinstance(decimal, Literal) \
        or not decimal.datatype in (XSD.decimal, XSD.integer):
        return
    trans = decimal.toPython()
    if isinstance(trans, (float, Decimal, int)):
        setlocale(LC_NUMERIC, '')
        return locstr(trans)

def decimal_from_str(value):
    """Renvoie la représentation RDF d'un nombre décimal exprimé comme chaîne de caractères.
    
    Parameters
    ----------
    value : str
        Le nombre décimal. La virgule et le point
        sont tous deux acceptés comme séparateurs
        entre la partie entière et la partie
        décimale.
    
    Returns
    -------
    rdflib.term.Literal
        Un littéral de type ``xsd:decimal``.
    
    Examples
    --------
    >>> decimal_from_str('-1,25')
    rdflib.term.Literal('-1.25', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#decimal'))
    
    Notes
    -----
    La fonction renvoie ``None`` pour une valeur mal formée.
    
    """
    if value is None:
        return
    clean_value = str(value).replace(' ', '').replace(',', '.')
    if not re.match('^([+]|-)?([0-9]+([.][0-9]*)?|[.][0-9]+)$', clean_value):
        return
    return Literal(clean_value, datatype=XSD.decimal)

def str_from_date(datelit):
    """Représentation d'une date sous forme de chaîne de caractères.
    
    Parameters
    ----------
    datelit : rdflib.term.Literal
        Un littéral de type ``xsd:date``. Les valeurs
        de type ``xsd::dateTime`` sont tolérées (et
        seront tronquées).
    
    Returns
    -------
    str
    
    Examples
    --------
    >>> str_from_date(Literal('2022-02-12', datatype=XSD.date))
    '12/02/2022'
    
    Notes
    -----
    La fonction renvoie ``None`` pour une valeur mal formée
    ou qui n'est pas un littéral de type ``xsd:date``.
    
    """
    if not datelit or not isinstance(datelit, Literal) \
        or not datelit.datatype in (XSD.date, XSD.dateTime):
        return
    trans = datelit.toPython()
    if isinstance(trans, (date, datetime)):
        return trans.strftime('%d/%m/%Y')

def date_from_str(value):
    """Renvoie la représentation RDF d'une date exprimée comme chaîne de caractères.
    
    Parameters
    ----------
    value : str
        La date, sous la forme `'jj/mm/aaaa'`, sans quoi
        la fonction renverra ``None``.
    
    Returns
    -------
    rdflib.term.Literal
        Un littéral de type ``xsd:date``.
    
    Examples
    --------
    >>> date_from_str('13/02/2022')
    rdflib.term.Literal('2022-02-13', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#date'))
    
    Notes
    -----
    La fonction tolère des informations excédentaires après la date
    (par exemple une heure). Elle tronque alors la valeur pour ne
    conserver que la date.
    
    """
    if not value:
        return
    r = re.match('^((?:0[1-9]|[12][0-9]|3[01])[/]' \
        '(?:0[1-9]|1[0-2])[/](?:[1-9][0-9]{3}|0[0-9]{3}))',
        value)
    if not r:
        return
    return Literal(datetime.strptime(r[1], '%d/%m/%Y').date(), datatype=XSD.date)

def str_from_datetime(datetimelit):
    """Représentation d'une date avec heure sous forme de chaîne de caractères.
    
    Parameters
    ----------
    datetimelit : rdflib.term.Literal
        Un littéral de type ``xsd:dateTime``. Les valeurs
        de type ``xsd::date`` sont tolérées.
    
    Returns
    -------
    str
    
    Examples
    --------
    >>> str_from_datetime(Literal('2022-02-12T00:00:00', datatype=XSD.dateTime))
    '12/02/2022 00:00:00'
    
    Notes
    -----
    La fonction renvoie ``None`` pour une valeur mal formée
    ou qui n'est pas un littéral de type ``xsd:dateTime`` ou
    ``xsd:date``.
    
    À ce stade, les heures sont tronquées à la seconde et
    les fuseaux horaires effacés.
    
    """
    if not datetimelit or not isinstance(datetimelit, Literal) \
        or not datetimelit.datatype in (XSD.dateTime, XSD.date):
        return
    trans = datetimelit.toPython()
    if isinstance(trans, datetime):
        return trans.strftime('%d/%m/%Y %H:%M:%S')
    elif isinstance(trans, date):
        return '{} 00:00:00'.format(trans.strftime('%d/%m/%Y'))
    # La méthode `Literal.toPython` de RDFLib
    # ne reconnaître pas les date+heure sans heure,
    # quand bien même c'est permis par le standard.
    # On teste donc ce cas manuellement :
    trans = str_from_date(Literal(str(datetimelit), datatype=XSD.date))
    if trans:
        return '{} 00:00:00'.format(trans)

def datetime_from_str(value):
    """Renvoie la représentation RDF d'une date exprimée comme chaîne de caractères.
    
    Parameters
    ----------
    value : str
        La date, sous la forme `'jj/mm/aaaa hh:mm:ss'`, sans
        quoi la fonction renverra ``None``.
    
    Returns
    -------
    rdflib.term.Literal
        Un littéral de type ``xsd:dateTime``.
    
    Examples
    --------
    >>> datetime_from_str('13/02/2022 15:30:14')
    rdflib.term.Literal('2022-02-13T15:30:14', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#dateTime'))
    
    Notes
    -----
    La fonction tolère qu'on ne lui fournisse qu'une date (informations
    relatives à l'heure manquantes). Il est alors considéré que
    l'heure était ``'00:00:00'``.
    
    La fonction tolère des informations excédentaires après
    la valeur des secondes (ou après la date sans heure),
    mais elles seront silencieusement effacées.
    
    """
    if not value:
        return
    r = re.match(r'^((?:0[1-9]|[12][0-9]|3[01])' \
        r'[/](?:0[1-9]|1[0-2])[/](?:[1-9][0-9]{3}|0[0-9]{3}))' \
        r'(?:[T\s](([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]|(24:00:00)))?', value)
    if not r:
        return
    value = '{} {}'.format(r[1], r[2] or '00:00:00')
    return Literal(datetime.strptime(value, '%d/%m/%Y %H:%M:%S'), datatype=XSD.dateTime)

def str_from_time(timelit):
    """Représentation d'une heure sous forme de chaîne de caractères.
    
    Parameters
    ----------
    timelit : rdflib.term.Literal
        Un littéral de type ``xsd:time``.
    
    Returns
    -------
    str
    
    Examples
    --------
    >>> str_from_time(Literal('15:30:14', datatype=XSD.time))
    '15:30:14'
    
    Notes
    -----
    La fonction renvoie ``None`` pour une valeur mal formée
    ou qui n'est pas un littéral de type ``xsd:time``.
    
    À ce stade, les heures sont tronquées à la seconde et
    les fuseaux horaires effacés.
    
    """
    if not timelit or not isinstance(timelit, Literal) \
        or not timelit.datatype == XSD.time:
        return
    trans = timelit.toPython()
    if isinstance(trans, time):
        return trans.strftime('%H:%M:%S')

def time_from_str(value):
    """Renvoie la représentation RDF d'une heure exprimée comme chaîne de caractères.
    
    Parameters
    ----------
    value : str
        L'heure, sous la forme `'hh:mm:ss'`, sans quoi
        la fonction renverra ``None``.
    
    Returns
    -------
    rdflib.term.Literal
        Un littéral de type ``xsd:time``.
    
    Examples
    --------
    >>> time_from_str('15:30:14')
    rdflib.term.Literal('15:30:14', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#time'))
    
    Notes
    -----
    La fonction tolère des informations excédentaires après
    la valeur des secondes, mais elles ne seront pas prises
    en compte.
    
    """
    if not value:
        return
    r = re.match('^(([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]|(24:00:00))', value)
    if not r:
        return
    return Literal(datetime.strptime(r[1], '%H:%M:%S').time(), datatype=XSD.time)

def wkt_with_srid(wkt, srid):
    """Ajoute un référentiel de coordonnées à la représentation WKT d'une géométrie.
    
    Parameters
    ----------
    wkt : str
        Représentation WKT (Well Known Text) d'une géométrie.
        La validité de ladite représentation n'est pas
        vérifiée par la fonction.
    srid : str
        L'identifiant du référentiel de coordonnées utilisé
        pour la représentation WKT, sous la forme ``'Autorité:Code'``.
        À ce stade, ne sont reconnus que les codes EPSG
        (ex : ``'EPSG:2154'``), les identifiants OGC (ex :
        ``'OGC:CRS84'``) et les identifiants du registre IGN (ex :
        ``'IGNF:WGS84G'``).
    
    Returns
    -------
    str
        La représentation WKT de la géométrie avec le référentiel
        explicitement déclaré, comme attendu en RDF.
    
    Examples
    --------
    >>> wkt_with_srid(
    ...     'POINT(651796.32814998598769307 6862298.58582336455583572)',
    ...     'EPSG:2154'
    ...      )
    '<http://www.opengis.net/def/crs/EPSG/0/2154> POINT(651796.32814998598769307 6862298.58582336455583572)'
    
    Notes
    -----
    La fonction renvoie ``None`` si l'autorité n'a pas
    été reconnue.
    
    """
    if not srid or not wkt:
        return wkt
    r = re.match('^([A-Z]+)[:]([a-zA-Z0-9.]+)$', srid)
    if r and r[1] in crs_ns:
        return '<{}{}> {}'.format(crs_ns[r[1]], r[2], wkt)

def split_rdf_wkt(rdf_wkt):
    """Extrait le référentiel et la géométrie d'un littéral WKT.
    
    Parameters
    ----------
    rdf_wkt : str or rdflib.term.Literal
        Une représentation WKT de la géométrie avec le référentiel
        explicitement déclaré, comme attendu en RDF pour le
        type ``gsp:wktLiteral``. Par défaut, le référentiel
        sera supposé être ``'OGC:CRS84'``.
    
    Returns
    -------
    tuple(str, str)
        Un tuple dont le premier élément est la géométrie,
        toujours encodée en WKT mais sans référentiel, et le
        second élément est le référentiel, sous la forme
        ``'Autorité:Code'``.
    
    Examples
    --------
    >>> split_rdf_wkt('<http://www.opengis.net/def/crs/EPSG/0/2154> ' \
    ...     'POINT(651796.32814998598769307 6862298.58582336455583572)')
    ('POINT(651796.32814998598769307 6862298.58582336455583572)', 'EPSG:2154')
    
    >>> split_rdf_wkt('POINT(651796.32814998598769307 6862298.58582336455583572)')
    ('POINT(651796.32814998598769307 6862298.58582336455583572)', 'OGC:CRS84')
    
    Notes
    -----
    La fonction renvoie ``None`` si l'autorité n'a pas été
    reconnue, mais ne fait qu'un contrôle de forme superficiel
    sur l'identifiant du référentiel (qui pourrait donc ne pas
    être une valeur référencée). La validité de la géométrie
    n'est pas vérifiée.
    
    """
    if not rdf_wkt:
        return
    rdf_wkt = str(rdf_wkt)
    r = re.match(r'^(?:<([^>]+)>\s+)?(.+)$', rdf_wkt)
    if not r or not r[2] or not r[2].strip():
        return
    if not r[1]:
        return (r[2], 'OGC:CRS84')
    for auth, url in crs_ns.items():
        if r[1].startswith(url):
            code = r[1][len(url):]
            if re.match('^[a-zA-Z0-9.]+$', code):
                return (r[2], '{}:{}'.format(auth, code))
            else:
                return

def geomtype_from_wkt(wkt):
    """Déduit le type de géométrie d'une représentation WKT.
    
    Si le type de géométrie n'est pas l'un des types
    gérés par Plume, la fonction renvoie ``None``.
    
    Parameters
    ----------
    wkt : str or rdflib.term.Literal
        Une représentation WKT de géométrie (avec ou sans
        référentiel explicitement déclaré).
    
    Returns
    -------
    str
        Le type de géométrie, parmi `'polygon'`, `'point'`,
        `'linestring'` et `'circularstring'`.
    
    """
    if not wkt:
        return
    l = ('polygon', 'point', 'linestring', 'circularstring')
    for t in l:
        if re.match(r'^(.*[\s\n])?{}'.format(t), wkt.lower()):
            return t

def get_datasetid(anygraph):
    """Renvoie l'identifiant du jeu de données éventuellement contenu dans le graphe.
    
    Parameters
    ----------
    anygraph : rdflib.graph.Graph
        Un graphe quelconque, présumé contenir la description d'un
        jeu de données (``dcat:Dataset``).
    
    Returns
    -------
    URIRef
        L'identifiant du jeu de données. None si le graphe ne contenait
        pas de jeu de données.
    
    """
    for s in anygraph.subjects(RDF.type, DCAT.Dataset):
        return s

def graph_from_file(filepath, format=None):
    """Désérialise le contenu d'un fichier sous forme de graphe.
    
    Le fichier sera présumé être encodé en UTF-8 et mieux
    vaudrait qu'il le soit.
    
    Parameters
    ----------
    filepath : str
        Chemin complet du fichier source, supposé contenir des
        métadonnées dans un format RDF, sans quoi l'import échouera.
    format : str, optional
        Le format des métadonnées. Si non renseigné, il est autant que
        possible déduit de l'extension du fichier, qui devra donc être
        cohérente avec son contenu. Pour connaître la liste des valeurs
        acceptées, on exécutera :py:func:`import_formats`.
    
    Returns
    -------
    rdflib.graph.Graph
        Un graphe.
    
    See Also
    --------
    plume.rdf.metagraph.metagraph_from_file
        Désérialise le contenu d'un fichier sous forme de graphe
        de métadonnées.
    
    """
    pfile = Path(filepath)
    
    if not pfile.exists():
        raise FileNotFoundError("Can't find file {}.".format(filepath))
        
    if not pfile.is_file():
        raise TypeError("{} is not a file.".format(filepath))
    
    if format and not format in import_formats():
        raise ValueError("Format '{}' is not supported.".format(format))
    
    if not format:
        if not pfile.suffix in import_extensions_from_format():
            raise TypeError("Couldn't guess RDF format from file extension." \
                            "Please use format to declare it manually.")
                            
        else:
            format = import_format_from_extension(pfile.suffix)
            # NB : en théorie, la fonction parse de RDFLib est censée
            # pouvoir reconnaître le format d'après l'extension, mais à
            # ce jour elle n'identifie même pas toute la liste ci-avant.
    
    with pfile.open(encoding='UTF-8') as src:
        g = Graph().parse(data=src.read(), format=format)
    return g

def import_formats():
    """Renvoie la liste de tous les formats disponibles pour l'import.
    
    Returns
    -------
    list of str
        La liste des formats reconnus par RDFLib à l'import.
    
    """
    return [ k for k, v in rdflib_formats.items() if v['import'] ]

def export_formats(no_duplicate=False, format=None):
    """Renvoie la liste de tous les formats disponibles pour l'export.
    
    Parameters
    ----------
    no_duplicate : bool, default False
        Si ``True``, lorsque plusieurs formats disponibles
        utilise la même extension (cas notamment de ``'xml'`` et
        ``'pretty-xml'``), la fonction n'en renvoie qu'un.
    format : str, optional
        Un format d'export à prioriser. `format` ne sera
        jamais éliminé par la suppression de pseudo-doublons
        effectuée lorsque `no_duplicate` vaut ``True``. Il
        s'agira toujours de la première valeur de la liste
        renvoyée, sauf s'il ne s'agissait pas d'un format
        d'export disponible (auquel cas il ne sera pas du tout
        dans la liste renvoyée).
    
    Returns
    -------
    list of str
        La liste des formats reconnus par RDFLib à l'export.
    
    """
    l = []
    if format and format in rdflib_formats:
        format_ext = export_extension_from_format(format)
    else:
        format_ext = None
    for k, v in rdflib_formats.items():
        if k == format:
            l.insert(0, k)
        elif not no_duplicate or (v['export default']
            and not export_extension_from_format(k) == format_ext):
            l.append(k)
    return l

def import_extensions_from_format(format=None):
    """Renvoie la liste des extensions associées à un format d'import.
    
    Parameters
    ----------
    format : str, optional
        Un format d'import présumé inclus dans la liste des formats
        reconnus par les fonctions de RDFLib (:py:data:`rdflib_formats`
        avec ``import`` valant ``True``).
    
    Returns
    -------
    list of str
        La liste de toutes les extensions associées au format considéré,
        avec le point.
        Si `format` n'est pas renseigné, la fonction renvoie la liste
        de toutes les extensions reconnues pour l'import.
    
    Examples
    --------
    >>> import_extensions_from_format('xml')
    ['.rdf', '.xml']
    
    """
    if not format:
        l = []
        for k, d in rdflib_formats.items():
            if d['import']:
                l += d['extensions']
        return l
    
    d = rdflib_formats.get(format)
    if d and d['import']:
        return d['extensions']

def export_extension_from_format(format):
    """Renvoie l'extension utilisée pour les exports dans le format considéré.
    
    Parameters
    ----------
    format : str
        Un format d'export présumé inclus dans la liste des formats
        reconnus par les fonctions de RDFLib (:py:data:`rdflib_formats`).
    
    Returns
    -------
    str
        L'extension à utiliser pour le format considéré, avec le point.
    
    Examples
    --------
    >>> rdf_utils.export_extension('pretty-xml')
    '.rdf'
    
    """
    d = rdflib_formats.get(format)
    if d:
        return d['extensions'][0]

def import_format_from_extension(extension):
    """Renvoie le format d'import correspondant à l'extension.
    
    Parameters
    ----------
    extension : str
        Une extension (avec point).
    
    Returns
    -------
    str
        Un nom de format. La fonction renvoie ``None`` si l'extension
        n'est pas reconnue.
    
    """
    for k, d in rdflib_formats.items():
        if d['import'] and extension in d['extensions']:
            return k

def export_format_from_extension(extension, default_format=None):
    """Renvoie le format d'export correspondant à l'extension.
    
    Parameters
    ----------
    extension : str
        Une extension (avec point).
    default_format : str, optional
        Un format d'export présumé inclus dans la liste des formats
        reconnus par les fonctions de RDFLib (:py:data:`rdflib_formats`).
        Si renseigné, le format par défaut est utilisé lorsqu'il n'est
        pas possible de déduire un format de l'extension ou lorsque
        plusieurs formats sont possibles pour l'extension (le format
        par défaut est alors privilégié s'il fait partie des formats
        en question).
    
    Returns
    -------
    str
        Un nom de format. La fonction renvoie ``None`` si l'extension
        n'est pas reconnue.
    
    """
    if not default_format in export_formats():
        default_format = None
    rdf_format = default_format
    for k, d in rdflib_formats.items():
        if extension in d['extensions']:
            if k == default_format:
                return default_format
            elif d['export default']:
                rdf_format = k
    return rdf_format

rdflib_formats = {
    'turtle': {
        'extensions': ['.ttl'],
        'import': True,
        'export default': True
        },
    'n3': {
        'extensions': ['.n3'],
        'import': True,
        'export default': True
        },
    'json-ld': {
        'extensions': ['.jsonld', '.json'],
        'import': True,
        'export default': True
        },
    'xml': {
        'extensions': ['.rdf', '.xml'],
        'import': True,
        'export default': False
        },
    'pretty-xml': {
        'extensions': ['.rdf', '.xml'],
        'import': False,
        'export default': True
        },
    'nt': {
        'extensions': ['.nt'],
        'import': True,
        'export default': True
        },
    'trig': {
        'extensions': ['.trig'],
        'import': True,
        'export default': True
        }
    }
"""Formats reconnus par les fonctions de RDFLib.

Si la clé ``import`` vaut ``False``, le format n'est pas reconnu
à l'import. Si ``export default`` vaut ``True``, il s'agit du
format d'export privilégié pour les extensions listées
par la clé ``extension``.

"""

