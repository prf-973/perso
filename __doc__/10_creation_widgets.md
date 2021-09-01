# Création d'un nouveau widget

Soit :
- `widgetsDict` le dictionnaire contenant tous les widgets et leurs informations de paramétrage.
- `key` la clé de l'enregistrement en cours de traitement.
- `vocabulary` le graphe RDF qui rassemble les valeurs des thésaurus.
- `language` la langue principale de rédaction des métadonnées sélectionnée par l'utilisateur.

Chaque enregistrement du dictionnaire des widgets contrôle un widget principal et, le cas échéant, un ou plusieurs widgets annexes.

[Widget principal](#widget-principal) • [Widget annexe : grille](#widget-annexe--grille) • [Widget annexe : étiquette](#widget-annexe--étiquette) • [Widget annexe : bouton de sélection de la source](#widget-annexe--bouton-de-selection-de-la-source) • [Widget annexe : bouton de sélection de la langue](#widget-annexe--bouton-de-selection-de-la-langue) • [Widget annexe : bouton "moins"](#widget-annexe--bouton-moins)

 
## Widget principal

### Type

Le type du widget principal (QGroupBox, QToolButton, QLineEdit...) est fourni par la clé `'main widget type'` du dictionnaire interne.

```python

widgetsDict[key]['main widget type']

```

**Si `'main widget type'` ne contient aucune valeur, il n'y a pas lieu de créer de widget.** Il s'agit de catégories de métadonnées non répertoriées dans le modèle de formulaire (template), et qui ne doivent donc pas être affichées, mais qui contiennent des valeurs qu'il n'est pas question de perdre.

### Stockage

Le nouveau widget a vocation à être stocké dans la clé `'main widget'` du dictionnaire interne.

```python

widgetsDict[key]['main widget']

```

### Parent

Le widget *parent* est le `'main widget'` de l'enregistrement dont la clé est le second argument du tuple `key`. Il s'agira toujours d'un QGroupBox.

Par exemple, si `key` vaut `(2, (5, (0,)))`,  son parent est le widget principal de la clé `(5, (0,))`.

```python

widgetsDict[key[1]]['main widget']

```

### Widget masqué ?

Certains widgets seront à masquer ou afficher selon les actions de l'utilisateur. Ceci concerne par exemple les boutons de traduction, qui devront être masqués si une traduction a déjà été saisie pour chacune des langues autorisées. Autre cas : lorsqu'une métadonnée peut être saisie au choix sous la forme d'un URI ou d'un ensemble de propriétés littérales, les widgets servant pour la forme non sélectionnée sont masqués tant que l'utilisateur ne décide pas de changer de forme.

Concrètement, le widget principal et tous les widgets annexes d'un enregistrement devront être masqués dès lors que la clé `'hidden'` ou la clé `'hidden M'` vaut `True`.

```python

widgetsDict[key]['hidden'] or widgetsDict[key]['hidden M']

```

### Paramètres spécifiques aux widgets QGroupBox

- L'**étiquette** - paramètre `title` du QGroupBox - est fournie par la clé `'label'` du dictionnaire interne.

```python

widgetsDict[key]['label']

```

Cette clé ne sera renseignée que s'il y a lieu d'afficher un libellé sur le groupe.

- Lorsqu'elle est renseignée, la clé `'help text'` fournit un **texte d'aide** (descriptif de la catégorie de métadonnée), qui pourrait alimenter un `toolTip` (voire un `whatsThis`).

```python

widgetsDict[key]['main widget'].setToolTip(widgetsDict[key]['help text'])

```

### Paramètres spécifiques aux widgets QToolButton

Les seuls cas où le widget principal est un QToolButton sont ceux des "boutons plus" et "boutons de traduction", qui permettent à l'utilisateur d'ajouter réciproquement des valeurs ou traductions supplémentaires. La clé `'object'` vaut alors `'plus button'` ou `'translation button'`.

L'action associée à ce QToolButton sera stockée dans la clé `'main action'` du dictionnaire.

```python

widgetsDict[key]['main action']

```

*Pour la définition de l'action, cf. [15_actions_widgets](/__doc__/15_actions_widgets.md#bouton-plus).*

### Paramètres spécifiques aux widgets de saisie

- Lorsqu'elle existe, soit parce qu'elle était déjà renseignée dans la fiche de métadonnées, soit parce qu'une valeur par défaut est définie pour la catégorie considérée, la **valeur à afficher** dans le widget est fournie par la clé `'value'` du dictionnaire.

À noter que les valeurs par défaut ne sont utilisées que si le groupe de propriétés est vide.

```python

widgetsDict[key]['value']

```

- Si la clé `'read only'` vaut `True`, le widget doit être visible mais désactivé, pour empêcher les modifications manuelles par l'utilisateur.

```python

widgetsDict[key]['read only']

```

- La clé `'is mandatory'` contient un booléen indiquant s'il est obligatoire (valeur `True`) ou non (valeur `False` ou `None`) de saisir une valeur pour la catégorie.

```python

widgetsDict[key]['is mandatory']

```
 

### Paramètres spécifiques aux widgets QLineEdit et QTextEdit

Pour les widgets d'édition de texte, le dictionnaire apporte divers paramètres complémentaires. Ils sont tous optionnels. Si la clé ne contient pas de valeur, c'est qu'il n'y a pas lieu d'utiliser le paramètre.

- `'placeholder text'` donne la **valeur fictive** à afficher dans le widget :

```python

widgetsDict[key]['main widget'].setPlaceholderText(widgetsDict[key]['placeholder text'])

```

- `'input mask'` donne le **masque de saisie** :

```python

widgetsDict[key]['main widget'].setInputMask(widgetsDict[key]['input mask'])

```

- `'type validator'` indique si un **validateur basé sur le type** doit être défini et lequel :

```python

widgetsDict[key]['type validator'] = mTypeValidator

if mTypeValidator == 'QIntValidator':
    widgetsDict[key]['main widget'].setValidator(QIntValidator(widgetsDict[key]['main widget']))
elif mTypeValidator == 'QDoubleValidator':
    widgetsDict[key]['main widget'].setValidator(QDoubleValidator(widgetsDict[key]['main widget']))

```

*Ces validateurs permettent également de définir des valeurs minimum et maximum autorisées. Comme le SHACL le permet également (avec `sh:minInclusive` et `sh:maxInclusive`, car les paramètres `bottom` et `top` de `QIntValidator()` et `QDoubleValidator()` sont inclusifs), cette possibilité pourrait être utilisée à l'avenir, mais aucune clé n'a été prévue en ce sens à ce stade.*

- `'regex validator pattern'` donne l'**expression rationnelle** que doit respecter la valeur saisie et `'regex validator flags'` les options éventuelles :

```python

re = QRegularExpression(widgetsDict[key]['regex validator pattern'])

if "i" in widgetsDict[key]['regex validator flags']:
    re.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
    
if "s" in widgetsDict[key]['regex validator flags']:
    re.setPatternOptions(QRegularExpression.DotMatchesEverythingOption)

if "m" in widgetsDict[key]['regex validator flags']:
    re.setPatternOptions(QRegularExpression.MultilineOption)
    
if "x" in widgetsDict[key]['regex validator flags']:
    re.setPatternOptions(QRegularExpression.ExtendedPatternSyntaxOption)

widgetsDict[key]['main widget'].setValidator(
    QRegularExpressionValidator(re),
    widgetsDict[key]['main widget'])
    )

```

*Seules les options `i`, `s`, `m` et `x` sont à la fois admises en SHACL et par QT, ce sont donc les seules à être gérées.*


### Paramètres spécifiques aux widgets QComboBox

- Pour obtenir la **liste des termes** à afficher dans le QComboBox, on utilisera la fonction `build_vocabulary()`. La clé `'current source'` contient le nom du thésaurus à utiliser.

```python

thesaurus = build_vocabulary(widgetsDict[key]['current source'], vocabulary, language)

```

- Comme les QTextEdit et QLineEdit, les widgets QComboBox peuvent afficher une **valeur fictive** fournie par la clé `'placeholder text'`. Celle-ci sera généralement renseignée car, si ni le schéma des métadonnées communes ni le modèle local ne fournissent de texte fictif, c'est le nom du thésaurus courant qui sera affiché.


```python

widgetsDict[key]['main widget'].setPlaceholderText(widgetsDict[key]['placeholder text'])

```

Autant que possible - considérant la quantité de termes dans certains thésaurus - les QComboBox devraient afficher une ligne de saisie avec **auto-complétion**. Il est par contre important qu'ils **ne permettent pas d'entrer d'autres valeurs que celles des thésaurus**.


### Placement dans la grille

Le nouveau widget doit être placé dans le QGridLayout associé à son parent.

```python

widgetsDict[key[1]]['grid widget']

```

Son placement vertical (paramètre *row* de la méthode addWidget) est donné par la clé `'row'` du dictionnaire interne.

```python

widgetsDict[key]['row']

```

**Pour les widgets QTextEdit uniquement**, La hauteur du widget (paramètre `row span`) est fournie par la clé `'row span'` du dictionnaire interne.

```python

widgetsDict[key]['row span']

```

*Le placement horizontal (paramètre `column`) et la largeur du widget (paramètre `column span`) ne sont pas explicitement définis par le dictionnaire à ce stade, mais pourraient l'être à l'avenir.*

D'une manière générale, `column` vaudra `0`, sauf pour un widget de saisie tel qu'une étiquette est placée sur la même ligne. Dans ce cas, `column` vaut `1`.

```python

column = 1 if widgetsDict[key]['label'] and widgetsDict[key]['label row'] is None else 0

```

*`column span` pourrait dépendre de la présence d'une étiquette et/ou de boutons "moins" ou de sélection de la source.*

[↑ haut de page](#création-dun-nouveau-widget)



## Widget annexe : grille

Pour les groupes de valeurs, groupes de propriétés et groupes de traduction, un widget annexe QGridLayout doit être créé en paralèlle du QGroupBox.

```python

widgetsDict[key]['object'] in ('group of values', 'group of properties', 'translation group')

```

### Stockage

Le widget QGridLayout sera stocké dans la clé `'grid widget'` du dictionnaire interne.

```python

widgetsDict[key]['grid widget']

```

### Parent

Le widget *parent* est le `'main widget'` de l'enregistrement.

```python

widgetsDict[key]['main widget']

```

[↑ haut de page](#création-dun-nouveau-widget)



## Widget annexe : étiquette

**Pour les widgets de saisie uniquement**, un QLabel doit être créé dès lors que la clé `'label'` du dictionnaire interne n'est pas nulle. Le libellé à afficher correspond bien entendu à la valeur de la clé `'label'`.

```python

widgetsDict[key]['label']

```

### Stockage

Le widget QLabel sera stocké dans la clé `'label widget'` du dictionnaire interne.

```python

widgetsDict[key]['label widget']

```

### Parent

Le widget *parent* est le même que pour le widget principal : il s'agit du `'main widget'` de l'enregistrement dont la clé est le second argument de `key`.

```python

widgetsDict[key[1]]['main widget']

```

### Placement dans la grille

Le QLabel doit être placé dans le QGridLayout associé à son parent.

```python

widgetsDict[key[1]]['grid widget']

```

Son placement vertical (paramètre `row` de la méthode addWidget) est donné par :
- la clé `'label row'` si elle n'est pas vide. Cela correspond au cas où le label doit être positionné au-dessus de la zone de saisie ;
- sinon la clé `'row'`. Dans ce cas le label et la zone de saisie sont toujours placés sur la même ligne.

Le paramètre `column` vaut toujours 0.

```python

row = widgetsDict[key]['label row'] or widgetsDict[key]['row']
column = 0

```

*Le paramètre `column span` n'est pas défini par le dictionnaire à ce stade, mais pourrait l'être à l'avenir.*


### Texte d'aide

Lorsqu'elle est renseignée, la clé `'help text'` fournit un **texte d'aide** (descriptif de la catégorie de métadonnée), qui pourrait alimenter un `toolTip` (voire un `whatsThis`).

```python

widgetsDict[key]['label widget'].setToolTip(widgetsDict[key]['help text'])

```


[↑ haut de page](#création-dun-nouveau-widget)




## Widget annexe : bouton de sélection de la source

Un widget QToolButton de sélection de source doit être créé dès lors que la condition suivante est vérifiée :

```python

widgetsDict[key]['multiple sources']

```

### Stockage

Le widget de sélection de la source est stocké dans la clé `'switch source widget'` du dictionnaire interne.

```python

widgetsDict[key]['switch source widget']

```

### Parent

Le widget *parent* est le même que pour le widget principal : il s'agit du `'main widget'` de l'enregistrement dont la clé est le second argument de `key`.

```python

widgetsDict[key[1]]['main widget']

```

### Menu

Le QMenu associé au QToolButton est stocké dans la clé `'switch source menu'` du dictionnaire.

```python

widgetsDict[key]['switch source menu']

```

Ce QMenu contient une QAction par thésaurus utilisable pour la métadonnée. Les QAction sont elles-mêmes stockées dans la clé `'switch source actions'` du dictionnaire, sous la forme d'une liste.

```python

widgetsDict[key]['switch source actions']

```

Les libellés des QAction correspondent aux noms des thésaurus et sont fournis par la liste contenue dans la clé `'sources'` du dictionnaire :

```python

widgetsDict[key]['sources']

```

*Pour la définition des actions, cf. [15_actions_widgets](/__doc__/15_actions_widgets.md#bouton-de-sélection-de-la-source).*

Il serait souhaitable de mettre en évidence le thésaurus courant - celui qui fournit les valeurs du QComboBox - par exemple via une icône (tandis que les autres thésaurus n'en auraient pas). Son nom est donné par la clé `'current source'`.

```python

widgetsDict[key]['current source']

```

### Placement dans la grille

Le QToolButton doit être placé dans le QGridLayout associé à son parent.

```python

widgetsDict[key[1]]['grid widget']

```

Le bouton de sélection de la source est toujours positionné immédiatement à droite de la zone de saisie.

```python

row = widgetsDict[key]['row']
column = 2 if widgetsDict[key]['label'] and widgetsDict[key]['label row'] is None else 1

```

Il n'y a a priori pas lieu de spécifier les paramètres `row span` et `column span`.

[↑ haut de page](#création-dun-nouveau-widget)



## Widget annexe : bouton  de sélection de la langue

Un widget QToolButton de sélection de langue doit être créé dès lors que la condition suivante est vérifiée (ce qui ne se produira que si le mode traduction est actif) :

```python

widgetsDict[key]['authorized languages']

```

### Stockage

Le bouton de sélection de la langue est stocké dans la clé `'language widget'` du dictionnaire interne.

```python

widgetsDict[key]['language widget']

```

### Parent

Le widget *parent* est le même que pour le widget principal : il s'agit du `'main widget'` de l'enregistrement dont la clé est le second argument de `key`.

```python

widgetsDict[key[1]]['main widget']

```

### Menu

Le QMenu associé au QToolButton est stocké dans la clé `'language menu'` du dictionnaire.

```python

widgetsDict[key]['language menu']

```

Ce QMenu contient une QAction par langue disponible. Les QAction sont elles-mêmes stockées dans la clé `'language actions'` du dictionnaire, sous la forme d'une liste.

```python

widgetsDict[key]['language actions']

```

Les libellés des QAction correspondent aux noms abrégés des langues et sont fournis par la liste contenue dans la clé `'authorized languages'` du dictionnaire :

```python

widgetsDict[key]['authorized languages']

```

*Pour la définition des actions, cf. [15_actions_widgets](/__doc__/15_actions_widgets.md#bouton-de-sélection-de-la-langue).*

### Rendu

Au lieu d'une icône, le QToolButton de sélection de la langue montre un texte correspondant au nom abrégé de la langue sélectionnée. Celui-ci est fourni par la clé `'language value'`.

```python

widgetsDict[key]['language value']

```

### Placement dans la grille

Le QToolButton doit être placé dans le QGridLayout associé à son parent.

```python

widgetsDict[key[1]]['grid widget']

```

Le bouton de sélection de la langue est toujours positionné immédiatement à droite de la zone de saisie. Il n'y a pas de conflit possible avec les boutons de sélection de source, car ceux-là ne peuvent apparaître que sur des objets de type *IRI* ou *BlankNode*, alors que spécifier la langue n'est possible que pour les objets de type *Literal*.

```python

row = widgetsDict[key]['row']
column = 2 if widgetsDict[key]['label'] and widgetsDict[key]['label row'] is None else 1

```

Il n'y a a priori pas lieu de spécifier les paramètres `row span` et `column span`.

[↑ haut de page](#création-dun-nouveau-widget)



## Widget annexe : bouton "moins"

Pour les propriétés admettant des valeurs multiples ou des traductions, des widgets QToolButton permettent à l'utilisateur de supprimer les valeurs précédemment saisies.

Un tel widget doit être créé dès lors que le widget appartient à un groupe de valeurs ou groupe de traduction, soit quand :

```python

len(key) > 1 and widgetsDict[key[1]]['object'] in ('translation group', 'group of values')

```

Il ne devra cependant être affiché que si la condition suivante est vérifiée :

```python

widgetsDict[key]['has minus button']

```

### Stockage

Il est stocké dans la clé `'minus widget'` du dictionnaire interne.

```python

widgetsDict[key]['minus widget']

```

### Parent

Le widget *parent* est le même que pour le widget principal : il s'agit du `'main widget'` de l'enregistrement dont la clé est le second argument de `key`.

```python

widgetsDict[key[1]]['main widget']

```

### Action

L'action associée au QToolButton est stockée dans la clé `'minus action'` du dictionnaire.

```python

widgetsDict[key]['minus action']

```

*Pour la définition de l'action, cf. [15_actions_widgets](/__doc__/15_actions_widgets.md#bouton-moins).*

### Placement dans la grille

Le QToolButton doit être placé dans le QGridLayout associé à son parent.

```python

widgetsDict[key[1]]['grid widget']

```

Le bouton "moins" est positionné sur la ligne de la zone de saisie, à droite du bouton de sélection de la source / de la langue s'il y en a un, sinon immédiatement à droite de la zone de saisie. À noter que, par construction, il ne peut jamais y avoir à la fois un bouton de sélection de la langue et un bouton de sélection de la source.

```python

row = widgetsDict[key]['row']
column = ( 2 if widgetsDict[key]['label'] and widgetsDict[key]['label row'] is None else 1 ) \
    + ( 1 if widgetsDict[key]['multiple sources'] else 0 ) \
    + ( 1 if widgetsDict[key]['authorized languages'] else 0 )

```

Il n'y a a priori pas lieu de spécifier les paramètres `row span` et `column span`.

[↑ haut de page](#création-dun-nouveau-widget)