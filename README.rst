===================
orientdb_data_layer
===================

Current state: Alpha, in development (everything works - but I will be adding new features)

*by Anton Dziavitsyn 2017*
::
    a.dziavitsyn@gmail.com
    devitsin@gmail.com

Introduction
------------

    orientdb_data_layer is the easy to use framework for data layer organisation for working with OrientDB
        It uses `PyOrient module <http://orientdb.com/docs/last/PyOrient.html>`_

        And provides some additional functionality (look at next section)

New features history by version
-------------------------------
        [0.32]
        
        + The ability to organize code more structurally in an architectural sense
        
        + Repository pattern realisation for encapsulation of the data layer logic
        
        + The ability to expand data-logic by adding custom methods to repositories. (in addition to base 'add', 'get', 'update', 'delete') - which will give flexibility and will keep all data logic at one place
        
        + The abitlity to work with model objects or abstract dictionaries (to get fully hashable results)
        
        + JSON results output with including linked objects

        [0.4.0]

        + get_by_tree(query_dict) method to filter objects by Link

Installation
------------
::

    pip install orientdb_data_layer

Usage example:
--------------
.. code-block:: python

    from orientdb_data_layer import data_connection
    from orientdb_data_layer.data import RepositoryBase

    # using pyorient.ogm (ORM realisation - part of pyorient module )
    # look at last version description here https://orientdb.com/docs/last/PyOrient.html
    from pyorient.ogm import property

    # Connecting OrientDB database
    initial_drop = True  # initial_drop used to DROP DATABASE when connected (to rebuild data schema)
    data_connection.connect_database('plocal://<ip_address>:2424/<database_name>', '<username>', '<password>', initial_drop)


    # Describe your database schema (in database will be created correspondent object types)

    # Base class for Graph vertices (V) (Nodes or Documents)
    NodeBase = data_connection.NodeBase

    # Base class for Graph edges (E) (Relations)
    RelationshipBase = data_connection.RelationshipBase


    class CustomNode(NodeBase):
        element_plural = 'nodes_collection'  # plural name for collection of nodes is required for repository
        id = property.Integer(default=0)
        name = property.String()


    class CustomSubNode(NodeBase):
        element_plural = 'subnodes_collection'

        id = property.Integer(default=0)
        parent_node = property.Link(mandatory=True, nullable=False, linked_to=CustomNode)
        name = property.String()

    #  create-update/register database schema
    #  refresh_models - will refresh/update database schema
    #  attach_models - will attach current model to existing database schema
    data_connection.refresh_models()

    # Now database was refreshed and it contains 2 Nodes (by our declaration)

    # Working with custom repositories
    # Every repository works with one node type, and supports (add, get, update, delete operations & direct sql_command)
    # in additional Repository may return results in JSON with including all linked objects (by documental links)


    class CustomNodeRepository(RepositoryBase):

        def __init__(self):
            super().__init__(CustomNode)  # here should be passed Node type for repository


    class CustomSubNodeRepository(RepositoryBase):

        def __init__(self):
            super().__init__(CustomSubNode)

    # And now we may use our repositories (Or add some additional functionality in them - if needed)

    _nodeRep = CustomNodeRepository()
    _subNodeRep = CustomSubNodeRepository()

    parent_record = _nodeRep.add({
        'id': 1,
        'name': 'our first parent record'
    })

    sub_record = _subNodeRep.add({
        'id': 21,
        'parent_node': parent_record,
        'name': 'child'
    })

    # and now we may obtain the records by filtering:
    # this will get all records of type CustomSubNode with 'id' = 1
    rec = _subNodeRep.get({
        'id': 21
    })

    # From ver[0.4.0] you may use get_by_tree(query_dict) method to filter objects by Link
    # This works with unlimited count of levels
    rec = _subNodeRep.get_by_tree({
        'parent_node': {
            'id': 1
        }
    })
    # rec = list of CustomSubNode when parent_node.id == 1

    # rec is list of CustomSubNode objects (look at OGM description in pyorient for details)
    # or we may return result as JSON (with linked parent record by our schema)
    rec = _subNodeRep.get({
        'id': 21
    }, result_JSON = True)

    '''
    rec:

    {
      [
        {
          "@rid": "#45:0",
          "@version": 1,
          "id": 21,
          "parent_node": {
            "@rid": "#33:0",
            "@version": 1,
            "id": 1,
            "name": "our first parent record"
          },
          "name": "child"
        }
      ]
    }
    '''
    # Also, you may use direct calls to current graph object's methods. Graph can be accessed by:
    _graph = data_connection.get_graph()

Repository base methods description:
------------------------------------
.. code-block:: python

    add(prop_dict, result_JSON= False):
        """
        add record by properties dict
        :param prop_dict: dictionary of values for properties updating (OUT OF TYPE will be ignored)
        :param result_JSON: return result as JSON text (default = False)
        :return: created MODEL OBJECT or JSON
        """

    get(query_dict, result_JSON= False):
        """
        get records by query dict
        :param query_dict: dictionary of values for records searching
        :return: list of MODEL OBJECTS
        """

    update(query_dict, prop_dict):
        """
        update records in database
        Example:
        update(dict(name='test2', id=1), dict(name= 'test3')
        will update all records with name = 'test2' and id =1, and set value of name = 'test3'

        :param query_dict: dictionary of values for records searching
        :param prop_dict: dictionary of values for properties updating (OUT OF TYPE will be ignored)
        :return: list of updated MODEL OBJECTS
        """

    delete(query_dict):
        """
        delete records in database
        :param query_dict: dictionary of values for records searching
        :return: Count of deleted records
        """

    sql_command(sqlcommand, result_as_dict=False, result_JSON= False):
        """
        Call direct SQL query
        :param sqlcommand: query string
        :param result_JSON: return result as JSON text (default = False)
        :param result_as_dict: return result as 'list of dict' but NOT orientRecord (default = False)
        :return: list of orient records [oRecordData] or list of Json
        """
