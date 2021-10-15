"""
Utilitaires pour la maintenance du schéma SHACL décrivant les métadonnées communes.

"""

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import NamespaceManager

from plume.bibli_rdf.rdf_utils import load_shape


def check_shape(shape, vocabulary, mIssues=None, mShape=None):
    """Contrôle du schéma SHACL.
    
    ARGUMENTS
    ---------
    - metagraph (rdflib.graph.Graph) : un graphe de métadonnées, extrait du commentaire
    d'un objet PostgreSQL.
    - shape (rdflib.graph.Graph) : schéma SHACL augmenté décrivant les catégories
    de métadonnées communes.
    - vocabulary (rdflib.graph.Graph) : graphe réunissant le vocabulaire de toutes
    les ontologies pertinentes.
    
    RESULTAT
    --------
    Si une anomalie est détectée, la fonction renvoie une liste de tuples
    constitués de :
    [0] le nom de la forme incriminée ;
    [1] le nom de la propriété concernée, le cas échéant ;
    [2] une description succinte du problème.
    
    Concrètement, [2] vaudra :
    - "not a NodeShape" si une forme n'est pas identifiée comme telle ;
    - "no targetClass" si une forme n'a pas de classe cible ;
    - "not closed" si une forme autre que DatasetShape n'est pas fermée ;
    - "type isn't ignored in closed shape" si la forme est fermée et
    rdf:type n'est pas marqué comme à ignorer ;
    - "no property" si une forme n'a pas de propriété associée ;
    - "no path" si sh:path est manquant pour la propriété ;
    - "repeated path" si une autre propriété de la même forme porte
    le même chemin ;
    - "no name" si sh:name est manquant pour la propriété ;
    - "repeated name" si une autre propriété de la même forme porte
    le même nom ;
    - "repeated description" si une autre propriété de la même
    forme porte la même description ;
    - "no order" si sh:order est manquant pour la propriété ;
    - "repeated order" si une autre propriété de la même forme a le
    même numéro d'ordre ;
    - "no nodeKind" si la propriété n'a pas de type de noeud ;
    - "invalid nodeKind", si le type de noeud n'est pas sh:Literal ou
    sh:IRI ou sh:BlankNode ou sh:BlankNodeOrIRI ;
    - "Literal without datatype" si le noeud est un litéral, et
    qu'aucun type de valeur n'est fourni ;
    - "IRI or BlankNode with datatype" si le noeud n'est pas un
    litéral mais un type de valeur est fourni ;
    - "IRI or BlankNode with uniqueLang" si le noeud n'est pas un
    litéral mais est marqué comme traduisible ;
    - "illegal minCount" si minCount est présent ailleurs que sur le
    libellé et la description du dataset ;
    - "maxCount and uniqueLang" si ces deux paramètres sont
    fournis simultanément ;
    - "maxCount should be 1 or nothing" si maxCount est présent et
    ne vaut pas 1 ;
    - "uniqueLang can only be applied on rdf:langString" si
    uniqueLang est utilisé avec un autre datatype ;
    - "Literal or IRI without widget" si la propriété n'est pas
    un noeud vide mais n'a pas de widget associé ;
    - "BlankNode with widget" si la propriété est un noeud vide et
    a un widget de saisie associé ;
    - "BlankNode with defaultValue" si la propriété est un noeud vide
    et a une valeur par défaut associée ;
    - "unknown widget" si le widget n'est pas "QLineEdit", "QTextEdit",
    "QComboBox", "QCheckBox", "QDateEdit" ou "QDateTimeEdit" ;
    - "IRI or BlankNode without class" si la propriété est un noeud vide
    ou un IRI et n'a pas de classe associée ;
    - "BlankNode without shape" si la propriété est un noeud vide
    (ou BlankNodeOrIRI) et qu'il n'y a pas de forme pour la classe
    associée ;
    - "BlankNode with inputMask" si un masque de saisie est fourni sur un
    neud vide ;
    - "BlankNode with placeholder" si une valeur exemple est fournie sur un
    neud vide ;
    - "BlankNode with pattern" si un schéma de validation est fourni sur un
    neud vide ;
    - "Literal or BlankNode with ontology" si une ontologie est
    renseignée pour autre chose qu'un IRI ;
    - "unlisted ontology" si l'ontologie n'est pas référencée dans
    vocabulary.
    """
    
    ns = shape.namespace_manager
    
    if mShape is None:
        mShape = URIRef("http://snum.scenari-community.org/Metadata/Vocabulaire/#DatasetShape")
        
    if mIssues is None:
        mIssues = []
    
    e = shape.value(mShape, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"))
    if not e == URIRef("http://www.w3.org/ns/shacl#NodeShape"):
        mIssues.append((mShape.n3(ns), None, "not a NodeShape"))
    
    shapePredicates = [p.n3(ns) for p in shape.predicates(mShape, None)]
    
    if not "sh:targetClass" in shapePredicates:
        mIssues.append((mShape.n3(ns), None, "no targetClass"))

    if not mShape == URIRef("http://snum.scenari-community.org/Metadata/Vocabulaire/#DatasetShape"):
    
        e = shape.value(mShape, URIRef("http://www.w3.org/ns/shacl#closed"))
        if not str(e).lower() == 'true':
            mIssues.append((mShape.n3(ns), None, "not closed"))
        
        b = shape.value(mShape, URIRef("http://www.w3.org/ns/shacl#ignoredProperties"))
        e = shape.value(b, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#first"))
        if not e == URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'):
            mIssues.append((mShape.n3(ns), None, "type isn't ignored in closed shape"))
    
    if not "sh:property" in shapePredicates:
        mIssues.append((mShape.n3(ns), None, "no property"))
    
    names = []
    descriptions = []
    rows = []
    paths =[]
    
    for prop in shape.objects(mShape, URIRef("http://www.w3.org/ns/shacl#property")):

        propPredicates = [p.n3(ns) for p in shape.predicates(prop, None)]
        
        if not "sh:path" in propPredicates:
            mIssues.append((mShape.n3(ns), path.n3(ns), "no path"))
        else:
            path = shape.value(prop, URIRef("http://www.w3.org/ns/shacl#path"))
            if path in paths:
                mIssues.append((mShape.n3(ns), path.n3(ns), "repeated path"))
            else:
                names.append(path)
            
        if not "sh:name" in propPredicates:
            mIssues.append((mShape.n3(ns), path.n3(ns), "no name"))
        else:   
            e = shape.value(prop, URIRef("http://www.w3.org/ns/shacl#name"))
            if e in names:
                mIssues.append((mShape.n3(ns), path.n3(ns), "repeated name"))
            else:
                names.append(e)
        
        e = shape.value(prop, URIRef("http://www.w3.org/ns/shacl#description"))
        if e in descriptions:
            mIssues.append((mShape.n3(ns), path.n3(ns), "repeated description"))
        elif e:
            names.append(e)
        
        if not "sh:order" in propPredicates:
            mIssues.append(mShape.n3(ns), path.n3(ns), "no order")
        else:
            e = shape.value(prop, URIRef("http://www.w3.org/ns/shacl#order"))
            if e in rows:
                mIssues.append((mShape.n3(ns), path.n3(ns), "repeated order"))
            else:
                names.append(e)
            
        if not "sh:nodeKind" in propPredicates:
            mIssues.append(mShape.n3(ns), path.n3(ns), "no nodeKind")
        else:  
            nk = shape.value(prop, URIRef("http://www.w3.org/ns/shacl#nodeKind")).n3(ns)
            if not nk in ("sh:Literal", "sh:IRI", "sh:BlankNode", "sh:BlankNodeOrIRI"):
                mIssues.append((mShape.n3(ns), path.n3(ns), "invalid nodeKind"))
                
            if nk == "sh:Literal" \
                and not "sh:datatype" in propPredicates:
                mIssues.append((mShape.n3(ns), path.n3(ns), "Literal without datatype"))
            
            if not nk == "sh:Literal" \
                and "sh:datatype" in propPredicates:
                mIssues.append((mShape.n3(ns), path.n3(ns), "IRI or BlankNode with datatype"))
                
            if not nk == "sh:Literal" \
                and "sh:uniqueLang" in propPredicates:
                mIssues.append((mShape.n3(ns), path.n3(ns), "IRI or BlankNode with uniqueLang"))
                
            if not nk == "sh:BlankNode" \
                and not "snum:widget" in propPredicates:
                mIssues.append((mShape.n3(ns), path.n3(ns), "Literal or IRI without widget"))
                
            if nk == "sh:BlankNode" \
                and "snum:widget" in propPredicates:
                mIssues.append((mShape.n3(ns), path.n3(ns), "BlankNode with widget"))
                
            if nk == "sh:BlankNode" \
                and "sh:defaultValue" in propPredicates:
                mIssues.append((mShape.n3(ns), path.n3(ns), "BlankNode with defaultValue"))
                
            if nk == "sh:BlankNode" \
                and "snum:inpuMask" in propPredicates:
                mIssues.append((mShape.n3(ns), path.n3(ns), "BlankNode with inputMask"))
                
            if nk == "sh:BlankNode" \
                and "snum:placeholder" in propPredicates:
                mIssues.append((mShape.n3(ns), path.n3(ns), "BlankNode with placeholder"))
                
            if nk == "sh:BlankNode" \
                and "snum:pattern" in propPredicates:
                mIssues.append((mShape.n3(ns), path.n3(ns), "IRI or BlankNode with pattern"))
                
            if nk in ("sh:Literal", "sh:BlankNode") \
                and "snum:ontology" in propPredicates:
                mIssues.append((mShape.n3(ns), path.n3(ns), "Literal or BlankNode with ontology"))
                
            if not nk == "sh:Literal" \
                and not "sh:class" in propPredicates:
                mIssues.append((mShape.n3(ns), path.n3(ns), "IRI or BlankNode without class"))
        
            if nk in ("sh:BlankNode", "sh:BlankNodeOrIRI") \
                and "sh:class" in propPredicates :
                
                childrenShapes = [ s for s in shape.subjects(
                    URIRef("http://www.w3.org/ns/shacl#targetClass"),
                    shape.value(prop, URIRef("http://www.w3.org/ns/shacl#class"))
                    ) ]
                if childrenShapes == []:
                    mIssues.append((mShape.n3(ns), path.n3(ns), "BlankNode without shape"))
                else:
                    for s in childrenShapes:
                        check_shape(shape=shape, vocabulary=vocabulary, mIssues=mIssues,
                            mShape=s)
        
        if "snum:widget" in propPredicates \
            and not str(shape.value(prop, URIRef("http://snum.scenari-community.org/Metadata/Vocabulaire/#widget"))) \
                in ("QLineEdit", "QTextEdit", "QComboBox", "QCheckBox", "QDateEdit", "QDateTimeEdit"):
                mIssues.append((mShape.n3(ns), path.n3(ns), "unknown widget"))
            
        if not mShape.n3(ns) == "sh:DatasetShape" \
            and not path in (
                URIRef("http://purl.org/dc/terms/title"),
                URIRef("http://purl.org/dc/terms/description")
                ) \
            and "sh:minCount" in propPredicates:
            mIssues.append((mShape.n3(ns), path.n3(ns), "illegal minCount"))
            
        if "sh:maxCount" in propPredicates \
            and "sh:uniqueLang" in propPredicates:
            mIssues.append((mShape.n3(ns), path.n3(ns), "maxCount and uniqueLang"))
    
        if "sh:maxCount" in propPredicates:
            e = shape.value(prop, URIRef("http://www.w3.org/ns/shacl#maxCount"))
            if not e == Literal('1', datatype=URIRef('http://www.w3.org/2001/XMLSchema#integer')):
                mIssues.append((mShape.n3(ns), path.n3(ns), "maxCount should be 1 or nothing"))
    
        if "sh:datatype" in propPredicates:
            dt = shape.value(prop, URIRef("http://www.w3.org/ns/shacl#datatype"))
            if not dt.n3(ns) == "rdf:langString" \
                and "sh:uniqueLang" in propPredicates:
                mIssues.append((mShape.n3(ns), path.n3(ns), "uniqueLang can only be applied on rdf:langString"))
        
        if "snum:ontology" in propPredicates:
            for o in shape.objects(
                prop, URIRef("http://snum.scenari-community.org/Metadata/Vocabulaire/#ontology")
                ):
                if not (
                    o,
                    URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                    URIRef("http://www.w3.org/2004/02/skos/core#ConceptScheme")
                    ) in vocabulary:
                    mIssues.append((mShape.n3(ns), path.n3(ns), "unlisted ontology '{}'".format(str(o))))
    
    if mIssues:
        return mIssues
    
    

def table_from_shape(
    mList=None, mPath=None, mNSManager=None,
    mTargetClass=URIRef("http://www.w3.org/ns/dcat#Dataset")
    ):
    """Représentation du schéma SHACL sous forme de table.
    
    ARGUMENTS
    ---------
    Néant.
    NB. mList, mPath, etc. servent aux appels récursifs, ils n'ont
    aucunement vocation à être renseignés manuellement.
    
    RESULTAT
    --------
    Une liste de tuples correspondant aux enregistrements de la table
    z_metadata.meta_shared_categorie hors champ serial (en vue de la
    mise à jour de celle-ci).
    """
    if mList is None:
        mList = []
    
    shape = load_shape()
    
    nsm = mNSManager or shape.namespace_manager
    
    q_tp = shape.query(
        """
        SELECT
            ?property ?name ?kind
            ?class ?order ?widget ?descr
            ?default ?min ?max
            ?placeholder ?rowspan ?mask
        WHERE
            { ?u sh:targetClass ?c ;
                 sh:property ?x .
              ?x sh:path ?property ;
                 sh:name ?name ;
                 sh:nodeKind ?kind ;
                 sh:order ?order .
              OPTIONAL { ?x snum:widget ?widget } .
              OPTIONAL { ?x sh:class ?class } .
              OPTIONAL { ?x sh:description ?descr } .
              OPTIONAL { ?x snum:placeholder ?placeholder } .
              OPTIONAL { ?x snum:inputMask ?mask } .
              OPTIONAL { ?x sh:defaultValue ?default } .
              OPTIONAL { ?x snum:rowSpan ?rowspan } .
              OPTIONAL { ?x sh:minCount ?min } .
              OPTIONAL { ?x sh:maxCount ?max } . }
        ORDER BY ?order
        """,
        initBindings = { 'c' : mTargetClass }
        )
    
    for p in q_tp:
        
        mKind = p['kind'].n3(nsm)
        mNPath = ( mPath + " / " if mPath else '') + p['property'].n3(nsm)
        
        mList.append((
            'shared',
            mNPath,
            mKind == 'sh:BlankNode',
            str(p['name']) if p['name'] else None,
            str(p['widget']) if p['widget'] else None,
            int(p['rowspan']) if p['rowspan'] else None,
            str(p['descr']) if p['descr'] else None,
            str(p['default']) if p['default'] else None,
            str(p['placeholder']) if p['placeholder'] else None,
            str(p['mask']) if p['mask'] else None,
            int(p['max']) > 1 if p['max'] is not None else True,
            int(p['min']) >= 1 if p['min'] is not None else False,
            int(p['order']) if p['order'] is not None else None
            ))
        
        if mKind in ('sh:BlankNode', 'sh:BlankNodeOrIRI'):
            table_from_shape(mList, mNPath, nsm, p['class'])
            
    return mList ;
    
    
    