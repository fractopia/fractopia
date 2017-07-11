from fractopia import *



graph = Graph(password="plaintextpwd")
selector = NodeSelector(graph)



class Tests():
    actexs = []


    @staticmethod
    def cru():
        fracti = Fracti("Tester","content",other_labels=["Test","Label2"])
        fracti.insert_db()
        print fracti.fetch_db()
        fracti.content = "other content"
        fracti.update_db()
        return Fracti.find_db(fracti.id_)

    @staticmethod
    def actor_con():
        actor = Actor(1,"Primeiro actor")
        actor.insert_db()
        BasicFractopus.initialize_main_node()
        actor_bf = actor.connect_extension(1)
        actor_bf.create_content(content="conteudo legal", name="nomezin")
        actor_bf.create_directory("pasta legal", "nomezera")

    @staticmethod
    def test_all():

        forum = Tests.actexs[0].create_fracti("Directory", "a forum", "Forum")
        post = Tests.actexs[1].create_fracti("Content","lorem ipsum","title")
        post = Fracti.get_instance(post)
        print post
        Tests.actexs[1].post_fracti(post, Tests.actexs[2].inbox("Public inbox"))
        forum_batatas = Tests.actexs[1].create_fracti("Directory","a forum", "Forum das batata")
        Tests.actexs[1].post_fracti(forum_batatas,forum)
        post2 = Tests.actexs[1].create_fracti("Content", "batata")
        Tests.actexs[1].post_fracti(post2, forum_batatas)
        Tests.actexs[1].tag_fracti(post2, "comida")
        Tests.actexs[2].see_inside(Tests.actexs[2].inbox("Public inbox"))
        Tests.actexs[1].get_fracti(post2)
        print Tests.actexs[1].see_inside(forum_batatas)
        Tests.actexs[4].share_fracti(post2, Tests.actexs[3].inbox("Public inbox"))
        Tests.actexs[3].see_inside(Tests.actexs[3].inbox("Public inbox"))


        return Tests.actexs


    @staticmethod
    def create_actors():
        BasicFractopus.initialize_main_node()
        for numero in range(1,6):
            actor =  Actor("Fractopia0-test", name="Actor")
            actor.other_labels.append("Actor")
            actor.insert_db()
            Tests.actexs.append(actor.connect_extension(1))
        print Tests.actexs


    @staticmethod
    def test_edit():
        all_batatas = Tests.actexs[1].search_fracti(content="Batata")
        first = all_batatas[0]
        return Tests.actexs[1].edit_fracti(first.id_, content="Batata mudada")


    def test_delete():
        all_batatas = Tests.actexs.search_fracti(content="Batata mudada")
        first = all_batatas[0]
        Tests.actexs[1].delete_fracti(first.id_)

    @staticmethod
    def delete():
        graph.delete_all()




Tests.delete()
Tests.create_actors()
Tests.test_all()
