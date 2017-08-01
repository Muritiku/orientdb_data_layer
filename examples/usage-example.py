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
    'id': 1,
    'parent_node': parent_record,
    'name': 'child'
})

# and now we may obtain the records by filtering:
# this will get all records of type CustomSubNode with 'id' = 1
rec = _subNodeRep.get({
    'id': 1
})
# rec is list of CustomSubNode objects (look at OGM description in pyorient for details)
# or we may return result as JSON (with linked parent record by our schema)
rec = _subNodeRep.get({
    'id': 1
}, result_JSON = True)

'''
rec:

{
  [
    {
      "@rid": "#45:0",
      "@version": 1,
      "id": 1,
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
