
from datetime import datetime
import time
from py2neo import Graph, Node, Relationship, NodeSelector
import uuid
import inspect
#import neo4j.v1
#from neo4j.v1 import basic_auth




#fractalia = py2neo.Graph(password="plaintextpwd")
"""

class Fractalia():
    graph = py2neo.Graph(password="plaintextpwd")
    node = py2neo.Node()
    relationship = py2neo.Relationship()



fractalia = Fractalia()
fg = fractalia.graph
# timestamp ->time.mktime(datetime.now().timetuple()))
"""



graph = Graph(password="plaintextpwd")
selector = NodeSelector(graph)


class Tests():


    @staticmethod
    def cru():
        fracti = Fracti("Tester","content",other_labels=["Test","Label2"])
        fracti.insert_db()
        print fracti.fetch_db()
        fracti.content = "other content"
        print fracti.update_db()
        Fracti.find_db(fracti.id_)


    @staticmethod
    def actor_con():
        actor = Actor(1,"Primeiro actor")
        actor.insert_db()
        BasicFractopus.initialize_main_node()
        actor_bf = actor.connect_extension(1)
        actor_bf.create_content(content="conteudo legal", name="nomezin")
        actor_bf.create_directory("pasta legal", "nomezera")









class Fracti(object):
    """ Representation of a node in the database. Everything is stored in fractis"""
    def __init__(self, creator_id, content="", name="", other_labels=[], id_= str(uuid.uuid4()), acess_keys="public-rw", timestamp=time.time()):
        self.id_ = id_
        self.name = name
        self.other_labels = other_labels
        self.content = content
        self.acess_keys = acess_keys
        self.timestamp = timestamp
        self.creator_id = creator_id




    @staticmethod
    def find_db(id_, label="Fracti"):
        """ find a node in de database based on id"""
        fracti = selector.select(label, id=id_)
        fracti = fracti.first()
        return fracti

    @classmethod
    def get_instance(cls,ids=None, node=None):
        """given a node object or an ID, creates a instance of the class to manage methods"""

        class_ = cls

        if node:
            fracti = node
        else:
            fracti = Fracti.find_db(ids)

        if fracti.has_label("Extension"):

            for label in fracti.labels():
                for key in Extension.extensions_index:
                    if label == Extension.extensions_index[key].__name__:
                        class_ = Extension.extensions_index[key]


        instance = class_(creator_id= fracti["creator_id"] )
        instance.id_ = fracti["id"]
        instance.acess_keys = fracti["acess_keys"]
        instance.timestamp = fracti["timestamp"]
        instance.content= fracti["content"]
        instance.name= fracti["name"]
        instance.other_labels= [label for label in fracti.labels()]

        return instance




    def search_db(label, property, value):
        """ search for a node based on label and property""" #not in use
        sel = selector.select(label, property=value)
        return list(sel)


    def content(self,content):
        """ Method to change content and commit to database directly, still deciding if needed"""
        pass

    def acess_keys(self):
        pass

    def new_label(self, label):
        self.other_labels.append(label)

    def fetch_db(self,label="Fracti"):
        """ Searches for the node in the database, or returns none"""

        return Fracti.find_db(label=label, id_=self.id_)

    def insert_db(self,label="Fracti"):
        if not self.fetch_db():
            fracti = Node(label, id=self.id_, content=self.content, name=self.name, acess_keys=self.acess_keys,timestamp=self.timestamp,creator_id=self.creator_id)
            for label in self.other_labels:
                fracti.add_label(label)
            graph.create(fracti)
        else:
            return self.fetch_db()


    def update_db(self):
        fracti = self.fetch_db()
        fracti["content"] = self.content
        fracti["acess_keys"] = self.acess_keys
        for label in self.other_labels:
            if not fracti.has_label(label):
                fracti.add_label(label)
        graph.begin(autocommit=True)
        graph.push(fracti)
        return fracti

    def delete_db(self):
        """Delete node from database, if not actor and no relationships"""
        fracti = self.fetch_db()
        graph.delete(fracti)




class Actor(Fracti):
    """Actor class, wich uses mediators (extensions) to interact with the database, and its also represented by a fracti on the database"""
    def __init__(self, creator_id, content="",other_labels=["Actor"]):
        super(Actor, self).__init__(creator_id, content, other_labels=["Actor"])


    def connect_extension(self,extension_id):
        actor = self.fetch_db()
        ext_main_node = Fracti.find_db(extension_id, label="Fracti")
        ex_class = Extension.extensions_index[extension_id]
        ex_inst = ex_class.initialize_instance_node(self.id_)

        actor_extension = Relationship(ex_inst,"OF",actor)
        graph.merge(actor_extension)
        return Fracti.get_instance(node=ex_inst)



class Extension(Fracti):

    extensions_index = {}
    extension_id = 0

    def __init__(self, creator_id, name="", content="Basic Extension",other_labels=["Extension"]):
        super(Extension, self).__init__(creator_id, name, content, other_labels)

    @classmethod
    def initialize_main_node(cls,label="Fracti", creator_id=1, content="Extension",acess_keys="public-rw"):
        extension = Node(label, id=cls.extension_id, content=content, acess_keys=acess_keys,timestamp=time.time(),creator_id=creator_id)
        extension.add_label(cls.__name__)
        extension.add_label("Extension")
        Extension.extensions_index[cls.extension_id] = cls
        graph.create(extension)
        return extension

    @classmethod
    def initialize_instance_node(cls,actor_id, label="Fracti", content="Extension",acess_keys="public-rw"):
        id_ = actor_id + "-" + str(cls.extension_id)
        extension = Node(label, id=id_, content=content, acess_keys=acess_keys,timestamp=time.time(),creator_id=actor_id)
        extension.add_label(cls.__name__)
        extension.add_label("Extension")
        main_node = Fracti.find_db(cls.extension_id)
        rel = Relationship(extension,"OF",main_node)
        graph.create(extension)
        graph.merge(rel)
        return extension

    @classmethod
    def get_instance(cls,id_=None, node=None):
        """given a node object or an ID, creates a instance of the class to manage methods"""
        if node:
            fracti = node
        else:
            fracti = Fracti.find_db(id_)



        instance = cls.__init__(creator_id=fracti["creator_id"],id_=fracti["id"],name= fracti["name"],
                            other_labels = fracti["other_labels"], content = fracti["content"],
                            acess_keys = fracti["acess_keys"], timestamp = fracti["timestamp"])

        return instance




class BasicFractopus(Extension):
    """ Alows the most basic interaction with database, creating new fractis or editing, relationships, and managing acess_keys"""


    extension_id = 1



    def actor_node(self):
        return Fracti.find_db(self.id_[:36])

    def create_fracti(self, type_, content, name="", permissions="public-rw"):
        fracti = Fracti(self.id_, content=content, name=name, acess_keys=permissions)
        fracti.other_labels.append(type_) #always append labels
        fracti.insert_db()
        fracti = fracti.fetch_db()
        rel = Relationship(self.actor_node(), "CREATED", fracti)
        graph.create(rel)
        return fracti

    def create_content(self, content, name="", permissions="public-rw"):
        self.create_fracti( "Content", content, name, permissions)

    def create_directory(self, content, name="", permissions="public-rw"):
        self.create_fracti("Directory", content, name, permissions)


    def create_relation(self):
        pass

    def delete_fracti(self):
        pass

    def delete_relation(self):
        pass


    def edit_fracti(self):
        pass

    def insert_acess_key(self):
        pass


class TagerFractopus():
    """ Mediator for creating tag relationships"""





class Content(Fracti):
    """ a fracti containing a piece of data"""
    pass

class Directory(Fracti):
    """ a fracti that links to other fractis as a way of organizing contents"""
    pass










"""
class Relationship():

    id_
    start_node
    end_node
    NAME:

    adicional_metadata
    timestamp
    creator
"""
