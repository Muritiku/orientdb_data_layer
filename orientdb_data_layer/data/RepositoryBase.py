from ..data_connection import get_graph, is_connected as is_data_connected


class RepositoryBase(object):

    __model_type = None
    __graph = None
    __broker = None

    def is_connected(self):
        if is_data_connected():
            if self.__graph is None or self.__broker is None:
                self.__graph = get_graph()
                if hasattr(self.__model_type, 'element_plural'):
                    self.__broker = getattr(self.__graph, self.__model_type.element_plural)
                elif hasattr(self.__model_type, 'label'):
                    self.__broker = getattr(self.__graph, self.__model_type.label)
            return self.__graph is not None and self.__broker is not None
        return False

    def __init__(self, model_type):
        self.__model_type = model_type

    def add(self, prop_dict, result_JSON= False):
        """
        add record by properties dict
        :param prop_dict: dictionary of values for properties updating (OUT OF TYPE will be ignored)
        :param result_JSON: return result as JSON text (default = False)
        :return: created MODEL OBJECT or JSON
        """
        if self.is_connected():
            if result_JSON:
                return self.sql_command("SELECT * FROM V WHERE @rid = {}"
                                        .format(self.__broker.create(**prop_dict)), result_JSON=True)[0].oRecordData['data']
            else:
                return self.__broker.create(**prop_dict)

    def get(self, query_dict, result_JSON= False):
        """
        get records by query dict
        :param query_dict: dictionary of values for records searching
        :return: list of MODEL OBJECTS
        """
        if self.is_connected():
            if result_JSON:
                json_list = [val.oRecordData['data'] for val in self.sql_command(self.__broker.query(**query_dict), result_JSON=True)]
                return "{[" + ",".join(json_list) + "]}"
            else:
                return [obj for obj in self.__broker.query(**query_dict)]

    def update(self, query_dict, prop_dict):
        """
        update records in database
        Example:
        update(dict(name='test2', id=1), dict(name= 'test3')
        will update all records with name = 'test2' and id =1, and set value of name = 'test3'

        :param query_dict: dictionary of values for records searching
        :param prop_dict: dictionary of values for properties updating (OUT OF TYPE will be ignored)
        :return: list of updated MODEL OBJECTS
        """
        if self.is_connected():
            result = []
            for rec in self.__broker.query(**query_dict):
                for key in prop_dict:
                    setattr(rec, key, prop_dict[key])
                cluster, id = (int(val) for val in rec._id.replace('#', '').split(':'))
                self.__graph.client.record_update(cluster, id, rec._props)
                result.append(rec)
            return result

    def delete(self, query_dict):
        """
        delete records in database
        :param query_dict: dictionary of values for records searching
        :return: Count of deleted records
        """
        if self.is_connected():
            result = []
            for rec in self.__broker.query(**query_dict):
                cluster, id = (int(val) for val in rec._id.replace('#', '').split(':'))
                result.append(self.__graph.client.record_delete(cluster, id))
            return result.count(True)

    def sql_command(self, sqlcommand, result_as_dict=False, result_JSON= False):
        """
        Call direct SQL query
        :param sqlcommand: query string
        :param result_JSON: return result as JSON text (default = False)
        :param result_as_dict: return result as 'list of dict' but NOT orientRecord (default = False)
        :return: list of orient records [oRecordData] or list of Json
        """
        if self.is_connected():
            if result_JSON:
                return self.__graph.client.command(
                    "SELECT @this.toJson('rid,version,fetchPlan:*:-1') AS data FROM ({})".format(sqlcommand)
                )
            elif result_as_dict:
                return [rec.oRecordData for rec in self.__graph.client.command(sqlcommand)]
            else:
                return self.__graph.client.command(sqlcommand)

