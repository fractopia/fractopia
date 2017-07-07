from fractopia import *


class Tests():


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
        actor0 = Actor("Fractopia","Fractopia-Actor")
        actor = Actor("Fractopia-test","1")
        actor2 = Actor("Fractopia-test","2")
        actor3 = Actor("Fractopia-test","3")
        actor4 = Actor("Fractopia-test","4")
        actors_list = [actor0, actor, actor2, actor3,actor4]
        actexs = []
        BasicFractopus.initialize_main_node()
        for actor in actors_list:
            actor.insert_db()
            actexs.append(actor.connect_extension(1))

        forum = actexs[0].create_fracti("Directory", "a forum", "Forum")
        post = actexs[1].create_fracti("Content","lorem ipsum","title")
        post = Fracti.get_instance(post)
        print post
        actexs[1].post_fracti(post, actexs[2].inbox("Public inbox"))
        forum_batatas = actexs[1].create_fracti("Directory","a forum", "Forum das batata")
        actexs[1].post_fracti(forum_batatas,forum)
        post2 = actexs[1].create_fracti("Content", "batata")
        actexs[2].post_fracti(post2, forum_batatas)
        actexs[1].tag_fracti(post2, word="comida")
        actexs[2].see_inside(actexs[2].inbox("Public inbox"))
        actexs[1].get_fracti(post2)
        actexs[1].see_inside(forum_batatas)
        #actexs[1].share(post2.id_, actexs[3].inbox("Public Inbox"))
        #actexs[3].see_directory(actexs[3].inbox("Public Inbox"))


        return actexs

    @staticmethod
    def test_edit():
        all_batatas = actexs[1].search_fracti(content="Batata")
        first = all_batatas[0]
        return actexs[1].edit_fracti(first.id_, content="Batata mudada")


    def test_delete():
        all_batatas = actexs.search_fracti(content="Batata mudada")
        first = all_batatas[0]
        actexs[1].delete_fracti(first.id_)


    def test():
        pass





Tests.test_all()
