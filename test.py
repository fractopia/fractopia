from fractopia import *
from py2neo import *


actor = Actor("A")
BasicFractopus.initialize_main_node()
actor.insert_db()
basic = actor.connect_extension(1)

aa = basic.create_fracti("Content","conteudo")
print basic.inbox("Public inbox")
