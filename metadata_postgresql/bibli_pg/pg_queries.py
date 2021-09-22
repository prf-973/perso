"""
Requêtes prêtes à être envoyées au serveur PostgreSQL.

Selon le cas, les paramètres doivent être passés :
- soit en argument de la fonction qui crée la requête (cas
des identifiants d'objets PostgreSQL) ;
- soit dans le tuple qui constitue le second argument
de la fonction execute() (valeurs litérales).

La syntaxe est systématiquement détaillée dans l'en-tête
des fonctions.

Dépendances : psycopg2 (https://www.psycopg.org).
"""


from psycopg2 import sql


def query_is_relation_owner():
    """Crée une requête qui vérifie que le rôle courant est membre du propriétaire d'une table.
    
    ARGUMENTS
    ---------
    Néant.
    
    RESULTAT
    --------
    Une requête prête à l'emploi, à utiliser comme suit :
    >>> cur.execute(query_is_relation_owner(), (schema_name, table_name))
    
    Avec (arguments positionnels) :
    - schema_name (str) : nom du schéma de la table ;
    - table_name (str) : nom de la table (ou toute autre relation).
    """
    return """
        SELECT pg_has_role(relowner, 'USAGE')
            FROM pg_catalog.pg_class
            WHERE relnamespace = quote_ident(%s)::regnamespace
                AND relname = %s
        """
    

def query_exists_extension():
    """Crée une requête qui vérifie qu'une extension est installée sur la base PostgreSQL cible.
    
    ARGUMENTS
    ---------
    Néant.
    
    RESULTAT
    --------
    Une requête prête à l'emploi, à utiliser comme suit :
    >>> cur.execute(query_exists_extension(), (extension_name,))
    
    Avec (arguments positionnels) :
    - extension_name (str) : le nom de l'extension.
    
    Cette requête renverra :
    - True si l'extension est installée ;
    - False si elle est disponible dans le répertoire des
    extension du serveur mais non installée ;
    - NULL si elle n'est pas disponible sur le serveur.
    """
    return """
        SELECT count(*) = 1
            FROM pg_available_extensions
            WHERE name = %s
                AND installed_version IS NOT NULL
        """


def query_update_table_comment(schema_name, table_name):
    """Crée une requête de mise à jour du descriptif d'une table ou vue.
    
    ARGUMENTS
    ---------
    - schema_name (str) : nom du schéma de la table ;
    - table_name (str) : nom de la table.
    
    RESULTAT
    --------
    Une requête prête à l'emploi, à utiliser comme suit :
    >>> query = query_update_table_comment(schema_name, table_name)
    >>> cur.execute(query, (new_pg_description,))
    
    Avec (arguments positionnels) :
    - new_pg_description (str) : valeur actualisée du descriptif de
    la table.
    """
    return sql.SQL(
        "COMMENT ON TABLE {} IS %s"
        ).format(
            sql.Identifier(schema_name, table_name)
            )


def query_get_table_comment(schema_name, table_name):
    """Crée une requête de récupération du descriptif d'une table ou vue.
    
    ARGUMENTS
    ---------
    - schema_name (str) : nom du schéma de la table ;
    - table_name (str) : nom de la table.
    
    RESULTAT
    --------
    Une requête prête à l'emploi, à utiliser comme suit :
    >>> query = query_get_table_comment(schema_name, table_name)
    >>> cur.execute(query)
    >>> old_description = cur.fetchone()[0]
    
    """
    return sql.SQL(
        "SELECT obj_description('{}'::regclass, 'pg_class')"
        ).format(
            sql.Identifier(schema_name, table_name)
            )


def query_list_templates():
    """Crée une requête d'import de la liste des modèles disponibles.
    
    ARGUMENTS
    ---------
    Néant.
    
    RESULTAT
    --------
    Une requête prête à l'emploi, à utiliser comme suit :
    >>> cur.execute(query_list_templates(), (schema_name, table_name))
    
    Avec (arguments positionnels) :
    - schema_name (str) : nom du schéma de la table ;
    - table_name (str) : nom de la table.
    
    On notera qu'au lieu d'importer le filtre sql_filter, la
    commande l'exécute et renvoie un booléen indiquant s'il est
    vérifié.
    """
    return """
        SELECT
            tpl_label,
            z_metadata.meta_execute_sql_filter(sql_filter, %s, %s) AS check_sql_filter,
            md_conditions,
            priority
            FROM z_metadata.meta_template
            ORDER BY tpl_label
        """


def query_get_categories():
    """Crée une requête d'import des catégories à afficher dans un modèle donné.
    
    ARGUMENTS
    ---------
    Néant.
    
    RESULTAT
    --------
    Une requête prête à l'emploi, à utiliser comme suit :
    >>> cur.execute(query_get_categories(), (tpl_label,))
    
    Avec :
    - tpl_label (str) : nom du modèle à utiliser.
    """
    return """
        SELECT 
            origin,
            path,
            cat_label,
            widget_type::text,
            row_span,
            help_text,
            default_value,
            placeholder_text,
            input_mask,
            multiple_values,
            is_mandatory,
            order_key,
            read_only,
            is_node,
            data_type::text,
            tab_name
            FROM z_metadata.meta_template_categories_full
            WHERE tpl_label = %s
        """


def query_template_tabs():
    """Crée une requête d'import des onglets utilisés par un modèle.
    
    ARGUMENTS
    ---------
    Néant.
    
    RESULTAT
    --------
    Une requête prête à l'emploi, à utiliser comme suit :
    >>> cur.execute(query_template_tabs(), (tpl_label,))
    
    Avec :
    - tpl_label (str) : nom du modèle.
    """
    return """
        SELECT
            meta_tab.tab_name
            FROM z_metadata.meta_tab
                LEFT JOIN z_metadata.meta_template_categories
                    ON meta_tab.tab_name = meta_template_categories.tab_name
            WHERE meta_template_categories.tpl_label = %s
                AND (
                    meta_template_categories.shrcat_path IS NOT NULL
                        AND meta_template_categories.shrcat_path ~ '^[a-z]{1,10}[:][a-z0-9-]{1,25}$'
                    OR meta_template_categories.shrcat_path IS NULL
                        AND meta_template_categories.loccat_path ~ '^[<][^<>"[:space:]{}|\\^`]+[:][^<>"[:space:]{}|\\^`]+[>]$'
                    )
            GROUP BY meta_tab.tab_name, meta_tab.tab_num
            ORDER BY meta_tab.tab_num NULLS LAST, meta_tab.tab_name
        """

