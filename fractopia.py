
from datetime import datetime
import time
from py2neo import Graph, Node, Relationship, NodeSelector
import uuid
import inspect


graph = Graph()
selector = NodeSelector(graph)



class Fracti(object):
    """ Representation of a node in the database. Everything is stored in fractis"""
    def __init__(self, creator_id, content="", name="No name", other_labels=None, id_=None, acess_keys="public-rw", timestamp=time.time()):
        self.id_ = str(uuid.uuid4()) if id_ is None else id_
        self.name = name  #gives error because of empty string name property
        self.other_labels = []
        self.content = content
        self.acess_keys = acess_keys
        self.timestamp = timestamp
        self.creator_id = creator_id


    @staticmethod
    def find_db(id_, label="Fracti"):
        """ returns a node in database based on id"""
        fracti = selector.select(label, id=id_)
        fracti = fracti.first()
        if fracti:
            return fracti
        else:
            return None


    @classmethod
    def get_instance(cls, ob):
        """given a node object or an ID, returns equivalent class instance """

        class_ = cls

        if isinstance(ob, Node):
            fracti = ob
        else:
            if cls.find_db(ob) is None:
                raise Exception("Wrong id format or not existent node")
            else:
                fracti = cls.find_db(ob)

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
        """ search for nodes based on label and property""" #not in use
        sel = selector.select(label, property=value)
        return list(sel)


    def new_label(self, label):
        self.other_labels.append(label)

    def fetch_db(self,label="Fracti"):
        """ Searches for the node in the database, or returns none"""

        return Fracti.find_db(label=label, id_=self.id_)

    def insert_db(self,label="Fracti"):
        """ inserts fracti oject as node in database, Returns True for sucess, False for failure"""
        if self.fetch_db() is None:
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
        return True

    def delete_db(self):
        """Delete node from database, if not actor and no relationships"""
        try:
            fracti = self.fetch_db()
            graph.delete(fracti)
            return True
        except:
            return False


class Actor(Fracti):
    """Actor class, wich uses mediators (extensions) to interact with the database, and its also represented by a fracti on the database"""

    def __init__(self, creator_id, content="", name="", other_labels=None):
        super(Actor, self).__init__(creator_id, content, name, other_labels)

    @classmethod
    def create_actor(cls, creator_id, content="", name=""):
        actor = cls(creator_id, content, name)
        actor.other_labels.append("Actor")
        actor.insert_db()
        return actor

    def connect_extension(self,extension_id):

        ex_class = Extension.extensions_index[extension_id]
        if not Extension.find_db(self.id_ + "-" + str(extension_id)):
            actor = self.fetch_db()
            ext_main_node = Fracti.find_db(extension_id)

            ex_inst = ex_class.initialize_instance_node(self.id_)
            actor_extension = Relationship(ex_inst,"OF",actor)
            graph.create(actor_extension)
            return Fracti.get_instance(ex_inst)
        else:

            ex_nd = Extension.find_db(self.id_ + "-" + str(extension_id))
            instance = ex_class.get_instance(ex_nd)
            return instance


class Extension(Fracti):

    extensions_index = {}
    extension_id = 0

    def __init__(self, creator_id, name="", content="Extension"):
        super(Extension, self).__init__(creator_id , name, content, id_=None)

    @classmethod
    def initialize_main_node(cls, creator_id="Fractopia", content="Extension",acess_keys="public-rw"):
        """ Creates extension main node on database an ads to the index, returns node"""
        if Fracti.find_db(cls.extension_id) is None:
            extension = Extension(creator_id)
            extension.id_ = cls.extension_id
            extension.name = cls.__name__
            extension.other_labels
            extension.other_labels.append("Extension")
            extension.other_labels.append(cls.__name__)
            extension.insert_db()
            Extension.extensions_index[cls.extension_id] = cls
            return extension.fetch_db()
        else:
            Extension.extensions_index[cls.extension_id] = cls
            return Fracti.find_db(cls.extension_id)


    @classmethod
    def initialize_instance_node(cls,actor_id, content="Extension",acess_keys="public-rw"):
        """Initilizes instance node with default configs and inboxes, returns node"""
        id_ext = actor_id + "-" + str(cls.extension_id)
        main_node = cls.initialize_main_node()
        extension = cls(actor_id)
        extension.id_ = id_ext
        extension.other_labels.append("Extension")
        extension.other_labels.append(cls.__name__)
        extension.name = cls.__name__
        extension.insert_db()
        inst_node = extension.fetch_db()
        extension.initial_config()
        rel = Relationship(inst_node,"OF",main_node)
        graph.create(rel)
        return inst_node




class BasicFractopus(Extension):
    """ Alows the most basic interaction with database, creating new fractis or editing, relationships, and managing acess_keys"""

    extension_id = 1

    def actor_node(self):
        return Fracti.find_db(self.id_[:36])

    def normalize_input(self, fracti):
        """Cheks type for fracti input (node, id or class instance) and returns class instance if possible"""
        if not isinstance(fracti, (Fracti, Node, str, int)):
            raise TypeError("Not a suported fracti input type")
        elif isinstance(fracti, Node):
            return Fracti.get_instance(fracti)
        elif isinstance(fracti,(int,str)):
            if Fracti.find_db(fracti) is None:
                    raise Exception("Wrong id format or not existent node in db")
            else:
                fracti = Fracti.get_instance(fracti)

        return fracti




    def initial_config(self):
        """Create default inboxes and other configurations"""
        inbox = self.create_fracti("Directory","Public inbox for receiving other user`s posts","Public inbox")
        inbox_inst = Fracti.get_instance(inbox)
        inbox_inst.insert_db()
        rel = Relationship(inbox, "OF", self.fetch_db())
        rel2 = Relationship(inbox, "IN", self.fetch_db())
        graph.create(rel)
        graph.create(rel2)

    def check_permissions(self, fracti):
        """Checks if acess_keys matches with fracti"""
        #fracti = self.normalize_input(fracti)
        #if fracti.acess_keys is self.key_ring:
        #    return True
        #else:
        #    return False
        # need to create keyring
        return fracti

    def get_fracti(self, fracti):
        if self.check_permissions(fracti):
            return self.normalize_input(fracti)
        else:
            return False


    def inbox(self,key="Public inbox"):
        inbox = None
        for rel in graph.match(end_node=self.fetch_db(),rel_type="OF"):
            if rel.start_node().properties["name"] == key:
                inbox = rel.start_node()

        return inbox



    def create_fracti(self, type_, content, name="No name", permissions="public-rw"):
        """creates a fracti associated to the actor (with CREATED relationship), returns
        fracti node object"""

        fracti = Fracti(self.id_, content=content, name=name, acess_keys=permissions)
        fracti.other_labels.append(type_) #always append labels
        fracti.insert_db()
        fracti = fracti.fetch_db()
        rel = Relationship(self.fetch_db(), "CREATED", fracti)
        graph.create(rel)
        return fracti

    def edit_fracti(self, fracti, content=None,name=None,acess_keys=None):
        """Get a fracti and edit it. Returns True/False for Sucess/Failure"""
        fracti = self.get_fracti(fracti)
        if fracti:
            if content:
                fracti.content = content
            if name:
                fracti.name = name
            if acess_keys:
                fracti.acess_keys = acess_keys
            fracti.update_db()
            return True
        else:
            return false

    def delete_fracti(self, fracti):
        fracti = self.get_fracti(fracti)
        if fracti:
            try:
                fracti.delete_db()
                return True
            except:
                return False
        else:
            return False


    def post_fracti(self, fracti, destination):

        actor = self.fetch_db()
        fracti = self.normalize_input(fracti)
        fracti = fracti.fetch_db()
        destination = self.normalize_input(destination)
        destination = destination.fetch_db()
        post = Relationship(actor,"POSTED", fracti)
        to = Relationship(fracti,"TO",destination)
        is_in = Relationship(fracti,"IS_IN",destination)
        context = graph.begin()
        context.create(post)
        context.create(to)
        context.create(is_in)
        context.commit()

    def tag_fracti(self,fracti, word,other_tag=None):
        """creates tag if not exist and create Relationship, initially just words, later other fractis"""
        tagged = self.get_fracti(fracti)
        tagged_node = tagged.fetch_db()
        tag = word
        sel = selector.select("Tag",content=word, name="Tag (Word)")
        if sel.first():
            tag = sel.first()
        else:
            tag = Fracti(self.id_, content=word, name="Tag (Word)", )
            tag.other_labels.append("Tag")
            tag.insert_db()
            tag = tag.fetch_db()

        rel = Relationship(tag, "TAG_OF", tagged_node)
        graph.create(rel)

    def see_inside(self, fracti):
        """Returns all fractis in a fracti(usually a directory), None if none is found"""
        fracti = self.get_fracti(fracti)
        fracti_node = fracti.fetch_db()
        found_nodes = []
        for rel in graph.match(end_node=fracti_node, rel_type="IS_IN"):
            found_nodes.append(rel.start_node())


        if len(found_nodes) > 0:
            return found_nodes
        else:
            return None

    def share_fracti(self, fracti, destination):
        """ Creates a 'Share link' and post it to destination"""
        fracti = self.get_fracti(fracti)
        destination = self.get_fracti(destination)
        print destination
        sl = Fracti(self.id_, content=fracti.id_, name="Shared Fracti")
        sl.other_labels.append("ShareLink")
        sl.insert_db()
        rel = Relationship(sl.fetch_db(), "SHARE_OF", fracti.fetch_db())
        rel2 = Relationship(self.fetch_db(),"SHARED",sl.fetch_db())
        rel3 = Relationship(self.fetch_db(),"POSTED",sl.fetch_db())
        rel4 = Relationship(sl.fetch_db(),"TO",destination.fetch_db())
        rel5 = Relationship(sl.fetch_db(), "IS_IN", destination.fetch_db())
        graph.create(rel)
        graph.create(rel2)
        graph.create(rel3)
        graph.create(rel4)
        graph.create(rel5)



    def create_relation(self, fracti1, relation, fracti2):
        """ Creates custom relation defined by user (not in use still)"""
        pass


    def delete_relation(self, relation):
        """ delete relations, still in doubt of using"""
        pass
