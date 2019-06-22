#-*- coding:utf-8 -*-
import requests
import json


class Sess():
    def __init__(self):
        self.session=requests.Session()
        # post_data={
        #   "password_change_required" : False,
        #   "password_change" : "http://localhost:7474/user/neo4j/password",
        #   "username" : "neo4j"
        # }
        url='http://localhost:7474/user/neo4j'
        headers={
            'Accept':'application/json; charset=UTF-8',
            'Authorization':'Basic bmVvNGo6MQ=='
        }
        login=self.session.get(url=url,headers=headers)
        # print(login)

    #用户最短路径
    def get_shortpath(self,userA_id,userB_id):
        cypher = "MATCH (a:Person {id:'%s'}),(b:Person {id:'%s'}),p=allshortestpaths((a)-[:师生|好友 *..5]-(b)) RETURN p LIMIT 5" % (userA_id, userB_id)
        post_data = {
            "statements": [{
                "statement": cypher,
                "resultDataContents":["graph"],
            }]
        }
        url = 'http://localhost:7474/db/data/transaction/commit'
        try:
            data = sess.session.post(url=url, headers={"Accept": "application/json; charset=UTF-8","Content-Type": "application/json",'Authorization': 'Basic bmVvNGo6MQ=='},data=json.dumps(post_data), timeout=4)
            a = data.json()
        except:
            a = {'detail': '未找到关系'}
            a = json.dumps(a)
        print(a)
        return a

    #用户总页码
    def user_pagenation(self,userA_node_id):
        cypher=""" MATCH data=(n:Person {id:'%s'})-[*..1]-(m:Person) RETURN count(data) """%(userA_node_id)
        post_data={
            "statements": [{
                "statement": cypher,
                # "resultDataContents":["graph"],
            }]
        }
        url = 'http://localhost:7474/db/data/transaction/commit'
        try:
            data = sess.session.post(url=url, headers={"Accept": "application/json; charset=UTF-8",
                                                       "Content-Type": "application/json",
                                                       'Authorization': 'Basic bmVvNGo6MQ=='},
                                     data=json.dumps(post_data), timeout=4)
            a = data.json()
            return a
        except:
            a = {'detail': '未找到关系'}
            # a = json.dumps(a)
            return a

    #用户分页显示
    def get_user_page(self,userA_node_id,page_size=5,page_num=1,if_all=False):
        if not if_all:
            counter=self.user_pagenation(userA_node_id)
            counter=counter['results'][0]['data'][0]['row'][0]
            print(counter)
            if page_size<=50:
                skip=page_size*(page_num-1)
                # co=skip+page_size
                if skip<=counter:
                    if skip+page_size < counter:
                        next_post={'page_num':page_num+1,'page_size':page_size,'user_id':userA_node_id,'if_all':False}
                    else:
                        next_post=None
                    if skip>0:
                        previous_post={'page_num':page_num-1,'page_size':page_size,'user_id':userA_node_id,'if_all':False}
                    else:
                        previous_post=None
                    # if page_num
                    cypher = """ MATCH data=(n:Person {id:'%s'})-[*..1]-(m:Person) RETURN data ORDER BY m.id SKIP %s LIMIT %s """%(userA_node_id,skip,page_size)
                    post_data = {
                        "statements": [{
                            "statement": cypher,
                            "resultDataContents":["graph"],
                        }]
                    }
                    url = 'http://localhost:7474/db/data/transaction/commit'
                    try:
                        data = sess.session.post(url=url, headers={"Accept": "application/json; charset=UTF-8","Content-Type": "application/json",'Authorization': 'Basic bmVvNGo6MQ=='},data=json.dumps(post_data), timeout=4)
                        data = data.json()
                        a={'count':counter,'next_post':next_post,'previous_post':previous_post,'results':data}
                    except:
                        a = {'detail': '未找到关系'}
                    print(a)
                    return a
                else:
                    data = {'detail': None}
                    data = json.dumps(data)
                    print(data)
                    return data
            else:
                data={'detail':'每页数量过大,请重新设置！'}
                # data=json.dumps(data)
                # print(data)
                return data
        else:
            cypher = """ MATCH data=(n:Person {id:'%s'})-[*..1]-(m:Person) RETURN data ORDER BY m.id""" % (userA_node_id)
            post_data = {
                "statements": [{
                    "statement": cypher,
                    "resultDataContents": ["graph"],
                }]
            }
            url = 'http://localhost:7474/db/data/transaction/commit'
            try:
                data = sess.session.post(url=url, headers={"Accept": "application/json; charset=UTF-8",
                                                           "Content-Type": "application/json",
                                                           'Authorization': 'Basic bmVvNGo6MQ=='},
                                         data=json.dumps(post_data), timeout=4)
                data = data.json()
            except:
                data = {'detail': '未找到关系'}
            print(data)
            return data

    #获取课程总页数
    def lesson_pagenation(self,user_id):
        cypher = """ MATCH data=(n:Person {id:'%s'})-[*..1]-(m:Lesson) RETURN count(data) """ % (user_id)
        post_data = {
            "statements": [{
                "statement": cypher,
                # "resultDataContents":["graph"],
            }]
        }
        url = 'http://localhost:7474/db/data/transaction/commit'
        try:
            data = sess.session.post(url=url, headers={"Accept": "application/json; charset=UTF-8",
                                                       "Content-Type": "application/json",
                                                       'Authorization': 'Basic bmVvNGo6MQ=='},
                                     data=json.dumps(post_data), timeout=4)
            a = data.json()
            return a
        except:
            a = {'detail': '未找到关系'}
            # a = json.dumps(a)
            return a

    #分页获取我的课程
    def get_my_lesson(self,user_id,page_size=5,page_num=1,if_all=False):
        if not if_all:
            counter = self.user_pagenation(user_id)
            counter = counter['results'][0]['data'][0]['row'][0]
            print(counter)
            if page_size <= 50:
                skip = page_size * (page_num - 1)
                # co=skip+page_size
                if skip <= counter:
                    if skip + page_size < counter:
                        next_post = {'page_num': page_num + 1, 'page_size': page_size, 'user_id': user_id,'if_all': False}
                    else:
                        next_post = None
                    if skip > 0:
                        previous_post = {'page_num': page_num - 1, 'page_size': page_size, 'user_id': user_id,'if_all': False}
                    else:
                        previous_post = None
                    # if page_num
                    cypher = """ MATCH data=(n:Person {id:'%s'})-[*..1]-(m:Lesson) RETURN data ORDER BY m.id SKIP %s LIMIT %s """ % (user_id, skip, page_size)
                    post_data = {
                        "statements": [{
                            "statement": cypher,
                            "resultDataContents": ["graph"],
                        }]
                    }
                    url = 'http://localhost:7474/db/data/transaction/commit'
                    try:
                        data = sess.session.post(url=url, headers={"Accept": "application/json; charset=UTF-8","Content-Type": "application/json",'Authorization': 'Basic bmVvNGo6MQ=='},data=json.dumps(post_data), timeout=4)
                        data = data.json()
                        a = {'count': counter, 'next_post': next_post, 'previous_post': previous_post, 'results': data}
                    except:
                        a = {'detail': '未找到关系'}
                    print(a)
                    return a
                else:
                    data = {'detail': None}
                    data = json.dumps(data)
                    print(data)
                    return data
            else:
                data = {'detail': '每页数量过大,请重新设置！'}
                data = json.dumps(data)
                print(data)
                return data
        else:
            cypher=""" MATCH data=(n:Person {id:"%s"}) -[*..1]-(m:Lesson) RETURN data ORDER BY m.id """ %(user_id)
            post_data = {
                "statements": [{
                    "statement": cypher,
                    "resultDataContents": ["graph"],
                }]
            }
            url = 'http://localhost:7474/db/data/transaction/commit'
            try:
                data = sess.session.post(url=url, headers={"Accept": "application/json; charset=UTF-8",
                                                           "Content-Type": "application/json",
                                                           'Authorization': 'Basic bmVvNGo6MQ=='},
                                         data=json.dumps(post_data), timeout=4)
                data = data.json()
            except:
                data = {'detail': '未找到关系'}
            print(data)
            return data

    #获取我的专业
    def get_my_major(self,user_id):
        cypher=""" MATCH data=(n:Person {id:"%s"}) -[o]-(m:Major) RETURN data """ % (user_id)
        post_data = {
            "statements": [{
                "statement": cypher,
                "resultDataContents": ["graph"],
            }]
        }
        url = 'http://localhost:7474/db/data/transaction/commit'
        try:
            data = sess.session.post(url=url, headers={"Accept": "application/json; charset=UTF-8",
                                                       "Content-Type": "application/json",
                                                       'Authorization': 'Basic bmVvNGo6MQ=='},
                                     data=json.dumps(post_data), timeout=4)
            data = data.json()
        except:
            data = {'detail': '未找到关系'}
        print(data)
        return data

    #获取相似专业
    def get_the_similar_major(self,major_node_id):
        cypher=""" MATCH data=(n)-[o:相似专业]-(m:Major) WHERE id(n)=%d  RETURN data """ % (major_node_id)
        post_data = {
            "statements": [{
                "statement": cypher,
                "resultDataContents": ["graph"],
            }]
        }
        url = 'http://localhost:7474/db/data/transaction/commit'
        try:
            data = sess.session.post(url=url, headers={"Accept": "application/json; charset=UTF-8",
                                                       "Content-Type": "application/json",
                                                       'Authorization': 'Basic bmVvNGo6MQ=='},
                                     data=json.dumps(post_data), timeout=4)
            data = data.json()
        except:
            data = {'detail': '未找到关系'}
        print(data)
        return data

    #获取专业的课程
    def get_major_lesson(self,major_node_id,lesson_type="专业限选",if_all_major_lesson=False):
        if not if_all_major_lesson:
            cypher=""" MATCH data=(n:Major)-[o:培养方案]-(m:Lesson) WHERE id(n)=%d AND o.type="%s" RETURN data """ % (major_node_id,lesson_type)
            post_data = {
                "statements": [{
                    "statement": cypher,
                    "resultDataContents": ["graph"],
                }]
            }
            url = 'http://localhost:7474/db/data/transaction/commit'
            try:
                data = sess.session.post(url=url, headers={"Accept": "application/json; charset=UTF-8",
                                                           "Content-Type": "application/json",
                                                           'Authorization': 'Basic bmVvNGo6MQ=='},
                                         data=json.dumps(post_data), timeout=4)
                data = data.json()
            except:
                data = {'detail': '未找到关系'}
            print(data)
            return data
        else:
            cypher = """ MATCH data=(n:Major)-[o:培养方案]-(m:Lesson) WHERE id(n)=%d AND o.type<>"公共必修" RETURN data """ % (major_node_id)
            post_data = {
                "statements": [{
                    "statement": cypher,
                    "resultDataContents": ["graph"],
                }]
            }
            url = 'http://localhost:7474/db/data/transaction/commit'
            try:
                data = sess.session.post(url=url, headers={"Accept": "application/json; charset=UTF-8",
                                                           "Content-Type": "application/json",
                                                           'Authorization': 'Basic bmVvNGo6MQ=='},
                                         data=json.dumps(post_data), timeout=4)
                data = data.json()
            except:
                data = {'detail': '未找到关系'}
            print(data)
            return data




sess=Sess()

if __name__ == '__main__':
    # sess.get_shortpath('201626703079','201625201031')
    # sess.pagenation('201626703079')
    # sess.get_user_page(page_num=1,userA_node_id='201626703079')
    sess.get_my_lesson(user_id='201626703079',if_all=True)
    # sess.get_user_page(if_all=True,userA_node_id='201626703079')
