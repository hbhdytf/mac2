# __author__ = 'sandy'
# -*- coding=utf-8 -*-
import sys
import MySQLdb
import datetime
from time import time
from swift.common.utils import cache_from_env, get_logger, \
    split_path, config_true_value, register_swift_info
from swift.common.swob import Response, Request
from swift.common.swob import HTTPBadRequest, HTTPForbidden, HTTPNotFound, \
    HTTPUnauthorized


class UserInfo:
    def denied_response(self, req):
        self.response = '[Deny] : %s\n' % req
        return None

    def get_user_info_from_token(self, env=None, token=None):
        """
        Get user information for the given token.
        :param env: The current WSGI environment dictionary.
        :param token: Token to validate and return a info string for.
        :returns: None if the token is invalid or a string containing a comma
                  separated list of groups the authenticated user is a member
                  of. The first group in the list is also considered a unique
                  identifier for that user.

        """
        info = None
        if not token:
            return None
        memcached_client = cache_from_env(env)
        if not memcached_client:
            raise Exception('Memcache required')
        memcached_token_key = '%s/token/%s' % (self.reseller_prefix, token)
        cached_auth_data = memcached_client.get(memcached_token_key)
        if cached_auth_data:
            expires, info = cached_auth_data
            if expires < time():
                self.denied_response('No User %s.' % info)
        return info

    def get_user_info_from_db(self, user_name=None):
        """
        Get user information for the given username.
        :param username: Username to validate and return a info string for. in
                  this function it means login_name
        :returns: None if the token is invalid or a string containing a comma
                  separated list of groups the authenticated user is a member
                  of. The first group in the list is also considered a unique
                  identifier for that user.

        """
        # Choose columns from database
        item = ('tu_id', 'login_name', 'username', 'password', 'seclevel', 'mobile', 'email')
        try:
            info_select = self.cur.execute("SELECT %s FROM TUser WHERE login_name = \'%s\'" % (str(item).replace('\'', '')[1:-1], user_name))
            # print "info_select : %d" % info_select
            # login_name is a unique value, so the select result is only 1
            if info_select != 1:
                if info_select == 0:
                    self.denied_response('No User %s.' % user_name)
                else:
                    self.denied_response('duplicated user %s.' % user_name)
            info = self.cur.fetchone()
            if info is None:
                self.denied_response('Error SQL execute.')
            info = dict(zip(item, info))
        except Exception as e:
            self.denied_response(e)
        return info

    def get_userid(self):
        return self.tu_id

    def get_secfield(self):
        """
        Return a list of user's security fields
        :returns: None if the token or username is invalid. or a list containing
                  separated secfield of the authenticated user.

        """
        if self.login_name:
            secfield = self.get_secfield_from_uid(self.tu_id)
            return secfield
        if self.token:
            secfield = self.get_secfield_from_token(self.token)
            return secfield
        else:
            self.denied_response('Error in get_secfield.')
        return None

    def get_secfield_from_uid(self, uid):
        """
        Return a list of user's security fields
        :params:  the unique uid is used to specify the user
        :returns: None if the user has no secfield. else return a list of secfield
                  by searching database.
        """
        secfield = None
        try:
            info_select = self.cur.execute("SELECT %s FROM TUserSecfieldRelation WHERE tu_id = %s" % ('secfield_id', uid))
            # print "info_select : %d" % info_select
            # login_name is a unique value, so the select result is only 1
            if info_select != 1:
                if info_select == 0:
                    return self.denied_response('The uid %s has no secfield related.' % uid)
                else:
                    return self.denied_response('duplicated secfield %s.' % uid)
            info = self.cur.fetchone()
            if info is None:
                self.denied_response('Error SQL execute.')
            secfield = (info[0].encode("utf8")).split(",")
        except Exception as e:
            self.denied_response(e)
        return secfield

    def get_secfield_info_from_secid(self, secid):
        """
        Return a concrete information of security fields
        :params:  the unique secfield id is used to specify the secfield
        :returns: None if the secid point to no secfield. else return a list of
                  secfield information by searching database.
        """
        # Choose columns from database
        item = ('secfield_id', 'parent_secfd_id', 'secfield_name', 'gen_time')
        try:
            info_select = self.cur.execute("SELECT %s FROM TSecfield WHERE secfield_id = \'%s\'" %
                                           (str(item).replace('\'', '')[1:-1], secid))
            # print "info_select : %d" % info_select
            # login_name is a unique value, so the select result is only 1
            if info_select != 1:
                if info_select == 0:
                    return self.denied_response('No Secfield id %s.' % secid)
                else:
                    self.denied_response('duplicated secfield id %s.' % secid)
            info = self.cur.fetchone()
            if info is None:
                self.denied_response('Error SQL execute.')
            secfield_info = dict(zip(item, info))
        except Exception as e:
            self.denied_response(e)
        return secfield_info

    def get_parentid_secfd_from_secid(self, secid):
        secfield_info = self.get_secfield_info_from_secid(secid)
        return secfield_info['parent_secfd_id']

    def get_seclevel_from_token(self, token):
        info = self.get_user_info_from_token(token)
        return info['sec_level']

    def get_seclevel(self):
        """
        Get security level from user
        """
        if self.seclevel:
            return self.seclevel
        else:
            if self.username:
                stat = 'User : %s has no security level, please contact system \
                    admin' % self.username
            else:
                stat = 'No User.'
            self.denied_response(stat)
        # return 0 # maybe default seclevel

    def __init__(self, token=None, username=None, request=None):
        # Database defination
        self.conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd='root', db="auth", charset="utf8")
        self.cur = self.conn.cursor()
        self.mc_user = cache_from_env(request.environ)
        # Initialze user information by token or usernames
        if token is None and username is None:
            self.denied_response('token')
        # TO DO: get user from db (web update user, not read from cache , temparily )
        if self.mc_user.get(username) and False:
            self.tu_id, self.username, self.seclevel, self.login_name, self.response = self.mc_user.get(username).split(',')
        else:
            if token:
                info = self.get_user_info_from_token(token=token)
            elif username:
                info = self.get_user_info_from_db(user_name=username)
            if info:
                # set each info
                self.tu_id = info['tu_id']
                self.username = info['username']
                self.login_name = info['login_name']
                self.seclevel = info['seclevel']
                self.email = info['email']
                self.password = info['password']
                self.mobile = info['mobile']
                self.response = 'True'
                self.mc_user.set(self.username, (('%s,%s,%s,%s,%s')%(self.tu_id, self.username, self.seclevel,self.login_name,self.response)))
            elif not self.response:
                self.response = ['Forbidden']

    def __call__(self):
        print "__call__ is running"


class Secfield:
    def denied_response(self, req):
        self.response = '[Deny] : %s\n' % req

    def get_secfield_info_from_secid(self, secid):
        """
        Return a concrete information of security fields
        :params:  the unique secfield id is used to specify the secfield
        :returns: None if the secid point to no secfield. else return a list of
                  secfield information by searching database.
        """
        # Choose columns from database
        item = ('secfield_id', 'parent_secfd_id', 'secfield_name', 'gen_time')
        try:
            info_select = self.cur.execute("SELECT %s FROM TSecfield WHERE \
                secfield_id=%s" % (str(item).replace('\'', '')[1:-1], int(secid)))
            # print "info_select : %d" % info_select
            # login_name is a unique value, so the select result is only 1
            if info_select != 1:
                if info_select == 0:
                    self.denied_response('No Secfield %s.' % secid)
                else:
                    self.denied_response('duplicated secfield id %s.' % secid)
            info = self.cur.fetchone()
            if info is None:
                self.denied_response('Error SQL execute.')
            secfield_info = dict(zip(item, info))
        except Exception as e:
            self.denied_response(e)
        return secfield_info

    def get_parent_id(self):
        parent_id = None
        if self.parent_secfd_id:
            parent_id = self.parent_secfd_id
        return parent_id

    def test(self):
        uid = self.secfield_id.encode('utf-8')
        info = self.cur.execute("select %s from TPolicy where secfield_id=%s" % ('seclass_id', uid))
        if info == 1:
            infos = self.cur.fetchone()
            dd = infos[0].encode('utf-8').split(',')
            return dd
        else:
            self.response = "%s" % 'Error'
            return self.denied_response(self.response)

    def get_seclass(self):
        if not self.secfield_id:
            self.denied_response("No secfield_id %s" % self.secfield_id)
            return "None"
        #uid = self.secfield_id.encode('utf-8')
	uid=self.secfield_id
        info_select = self.cur.execute("SELECT %s FROM TPolicy WHERE secfield_id = %s" % ('seclass_id', uid))
        # login_name is a unique value, so the select result is only 1
        if info_select == 1:
            info = self.cur.fetchone()
            seclass = (info[0].encode('utf-8')).split(',')
            return seclass
        else:
            return ''

    def __init__(self, secid, req):
        # Database defination
        # self.mc = memcache.Client(['192.168.119.89:11211'])
        self.mc = cache_from_env(req.environ)
        self.conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd='root', db="auth", charset="utf8")
        self.cur = self.conn.cursor()
	print "----------------",self.mc.get(str(secid))
        if self.mc.get(str(secid)):
            self.secfield_id, self.parent_secfd_id, self.secfield_name = self.mc.get(str(secid)).split(',')
        else:
            info = self.get_secfield_info_from_secid(secid)
            if info:
                self.secfield_id = info['secfield_id']
                self.parent_secfd_id = info['parent_secfd_id']
                self.secfield_name = info['secfield_name'].encode('utf-8')
                self.response = 'True'
                # add into memcached
                self.mc.set(str(self.secfield_id), (('%s,%s,%s') % (self.secfield_id, self.parent_secfd_id, self.secfield_name)))


class Subject:
    """
    Parser User as Subject
    """
    def denied_response(self, req):
        self.response = '[Deny] : %s\n' % req
        return None

    def __init__(self, User):
        try:
            self.seclevel = User.get_seclevel()
            self.secfield = User.get_secfield()
        except:
            self.seclevel = -1
            self.secfield = None
        if not self.seclevel:
            # set defualt Subject
            self.seclevel = -1
        if not self.seclevel:
            self.secfield = None


class Meta(object):
    """
    Each container has a separate meta tables, path is an unique string to get
    concrete information of object
    """
    def denied_response(self, req):
        self.response = '[Deny] : %s\n' % req
        return None

    def __init__(self, path, req):
        # Database defination
        self.conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd='root', db="auth", charset="utf8")
        self.cur = self.conn.cursor()
        self.mc_meta = cache_from_env(req.environ)
        obj = self.get_conobj_from_path(path)
        #obj = self.get_objname_from_path(path)
        if self.mc_meta.get(path):
            self.object_id, self.object_name, self.parent_secl_id, self.seclevel, self.path, self.response = self.mc_meta.get(path).split(',')
        else:
            meta = self.get_metadata_from_objname(obj)
            if meta:
                self.object_id = meta['object_id']
                self.object_name = meta['object_name'].encode("utf8")
                self.parent_secl_id = meta['parent_secl_id']
                self.seclevel = meta['obj_seclevel']
                self.author = meta['author'].encode("utf8") if meta['author'] else None
                self.path = meta['path'].encode("utf8")
                self.subject = meta['subject'].encode("utf8") if meta['subject'] else None
                self.description = meta['description'].encode("utf8") if meta['description'] else None
                self.source = meta['source'].encode("utf8") if meta['source'] else None
                self.response = 'True'
                self.mc_meta.set(self.path, (('%s,%s,%s,%s,%s,%s') % (self.object_id, self.object_name, self.parent_secl_id, self.seclevel, self.path, self.response)))
            elif not self.response:
                self.response = ['Forbidden']

    def get_seclevel(self):
        """
        Get security level from metadata
        """
        if self.seclevel:
            return self.seclevel
        else:
            if self.object_name:
                stat = 'Object : %s has no security level, please contact system \
                    admin' % self.object_name
            else:
                stat = 'No Object metadata.'
            self.denied_response(stat)

    def get_seclass(self):
        """
        Get security classification from metadata
        """
        if self.parent_secl_id:
            return self.parent_secl_id
        else:
            if self.object_name:
                stat = 'Object : %s has no security classification, please contact system \
                    admin' % self.object_name
            else:
                stat = 'No Object metadata.'
            self.denied_response(stat)

    def get_metadata_from_objname(self, obj):
        item = ('object_id', 'object_name', 'parent_secl_id', 'obj_seclevel', 'author', 'path',
                'subject', 'description', 'language', 'source')
        try:
            info_select = self.cur.execute("select %s from TMeta where path = \'%s\'" %
                                           (str(item).replace('\'', '')[1:-1], obj))
            # login_name is a unique value, so the select result is only 1
            if info_select != 1:
                if info_select == 0:
                    return self.denied_response('No files %s.' % obj)
                else:
                    return self.denied_response('duplicated files id %s.' % obj)
            info = self.cur.fetchone()
            if info is None:
                return self.denied_response('Error SQL execute.')
            Meta_info = dict(zip(item, info))
        except Exception as e:
            return self.denied_response(e)
        return Meta_info

    def get_objname_from_path(self, path):
        # get object name from path
        _junk, account, container, obj = split_path(path, 1, 4, True)
        return obj
    def get_conobj_from_path(self,path):
        # get object name from path
        _junk, account, container, obj = split_path(path, 1, 4, True)
        if obj!=None:
            obj="%s/%s" % (container,obj)
        else:
            obj=None
        return obj
    def check_path(self, path):
        # path string replace or check
        if not path:
            return False
        if '..' in path:
            return False
        return True


class Object:
    """
    Parser audio files as Object
    """
    def denied_response(self, req):
        self.response = '[Deny] : %s' % req
        return None

    def get_parent_seclass(self, secid=None):
        # if not self.seclass:
        #      return None
        parent = {}
        if not secid:
            secid = self.seclass
        # in this way, suppose the max classification depth is 10
        for v in range(1, 10):
            seclass_info = self.get_parent_seclass_from_db(secid)
            if not seclass_info:
                break
            parent[str(secid)] = str(seclass_info['parent_secl_id'])
            if not seclass_info['parent_secl_id']:
                break
            else:
                secid = seclass_info['parent_secl_id']
        return parent

    def get_parent_seclass_from_db(self, secid):
        # Database defination
        self.conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd='root', db="auth", charset="utf8")
        self.cur = self.conn.cursor()
        item = ('seclass_id', 'parent_secl_id', 'seclass_name', 'gen_time')
        try:
            info_select = self.cur.execute("select %s from TSeclass where seclass_id = \'%s\'"
                                           % (str(item).replace('\'', '')[1:-1], secid))
            # seclass_id is a unique value, so the select result is only 1
            if info_select != 1:
                if info_select == 0:
                    self.denied_response('No Seclass %s.' % secid)
                    return None
                else:
                    self.denied_response('duplicated seclass id %s.' % secid)
            info = self.cur.fetchone()
            if info is None:
                self.denied_response('Error SQL execute.')
            seclass_info = dict(zip(item, info))
        except:
            self.denied_response('Error SQL execute.')
        return seclass_info if seclass_info else None

    def __init__(self, meta=None):
        if meta:
            self.seclevel = meta.get_seclevel()
            self.seclass = meta.get_seclass()
            if not (self.seclevel and self.seclass):
                self.seclevel = 1
                self.seclass = 0


class mandatory_access_control(object):
    def __init__(self, app, conf):
        self.app = app
        self.conf = conf
        self.upload = 'True'
        self.logger = get_logger(conf, log_route='mac')
        self.reseller_prefix = "AUTH_"
        self.admins = {}
        conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="root", db="auth", charset="utf8")
        cur = conn.cursor()
        cur.execute('select * from TAdmin')
        for row1 in cur.fetchall():
            name = row1[1].encode('utf-8')
            password = row1[2].encode('utf-8')
            url = '$HOST/v1/%s%s' % (self.reseller_prefix, name)
            self.admins[name] = {'url': url, 'passwd': password}
        print "I am in mac middleware"

    def __call__(self, env, start_response):



        self.conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd='root', db="auth", charset="utf8")
        self.cur = self.conn.cursor()
        req = Request(env)
        token = env.get('HTTP_X_AUTH_TOKEN', env.get('HTTP_X_STORAGE_TOKEN'))
        memcache_client = cache_from_env(req.environ)
        if not memcache_client:
            raise Exception('Memcache required')
        memcache_token_key = '%s/token/%s' % (self.reseller_prefix, token)
        cached_auth_data = memcache_client.get(memcache_token_key)
        if not cached_auth_data:
            start_response("404 Forbidden", [("Content-type", "text/plain")])
            return ["Token denied test!!! I am here\n%s\n%s\n%s\n" % (cached_auth_data, memcache_token_key, env)]
        expires, self.account_name = cached_auth_data
        if expires < time():
            self.logger.increment('token_denied')
            return HTTPUnauthorized(request=req, headers={'Www-Authenticate': 'Swift realm="%s"' % self.account_name})
        path = req.environ['PATH_INFO']
        # self.account_name = 'mobile'
        _junk, account, container, obj = split_path(path, 1, 4, True)
        if obj!=None:
            obj="%s/%s" % (container,obj)
        else:
            obj=None
        user = UserInfo(username=self.account_name, request=req)
        print "#############",user.__dict__
        try:
            sub = Subject(user)
        except:
            start_response("404 Forbidden", [("Content-type", "text/plain")])
            return ["Token denied test!!! I am here\n%s\n%s\n%s\n" % (cached_auth_data, memcache_token_key, env)]
        if self.account_name in self.admins:
            if req.method == 'PUT' or req.method == 'POST':
                ss = self.app(env, start_response)
                '''
                check whether the container exists.the ss is the returned body.
                if the body not null,the container does not exist.
                else continue.then we check the sole path in the function save().
                '''
                try:
                    dd = str(ss.next())
                except Exception as e:
                    dd = str(e)
                if 'resource' not in dd:
                    self.save(env, sub_seclevel=0,obj_path=obj)
                    # start_response("404 Forbidden", [("Content-type", "text/plain"), ('upload', self.upload)])
                    # return ["%s" % self.upload]
                    if self.upload == 'True':
                        return self.app(env, start_response)
                    else:
                        start_response("404 Forbidden", [("Content-type", "text/plain")])
                        return str(self.upload)
                else:
                    start_response("404 Forbidden", [("Content-type", "text/plain")])
                    return ['The Container:%s is Not Found\n' % container]

        if req.method == 'GET' and obj:
            # user = UserInfo(username=self.account_name,request=req)
            audio = Meta(path, req)
            if audio.response != 'True':
                start_response("111 Forbidden", [("Content-type", "text/plain")])
                return audio.response
            # sub=Subject(user)
            if user.response != 'True':
                start_response("403 Forbidden", [("Content-type", "text/plain")])
                return user.response
            obj_info = Object(audio)
            if audio.response != 'True':
                start_response("404 Forbidden", [("Content-type", "text/plain")])
                return audio.response
            if int(sub.seclevel) < int(obj_info.seclevel):
                start_response("404 Forbidden", [("Content-type", "text/plain"), ("sub", sub.seclevel),
                                                 ("obj", obj_info.seclevel)])
                return ["Secure Level Forbidden,Please Check the Level!\n"]

            classes = obj_info.get_parent_seclass()
            x = str(obj_info.seclass)
            while x is not None:
                for secfd in sub.secfield:
                    secfield = Secfield(secfd, req)
                    if str(x) in secfield.get_seclass():
                        return self.app(env, start_response)
                try:
                    x = classes[x]
                except:
                    # not match secfield in the last search :KeyError: '0'
                    break
            start_response("403 Forbidden", [("Content-type", "text/plain"), ("sub", sub.seclevel),
                                             ("obj", obj_info.seclevel)])
            return ["Secure field Forbidden: secure-field not match\n"]
        elif req.method == 'PUT' and obj:
            sub_classes = []
            sub_secfield = sub.secfield
            for secfd in sub.secfield:
                clas = Secfield(secfd, req).get_seclass()
                sub_classes += clas
            object_info = Object()

            if user.response != 'True':
                start_response("403 Forbidden", [("Content-type", "text/plain")])
                return user.response
            obj_secl_id = env.get('HTTP_PARENT_SECL_ID')
            obj_seclevel = env.get('HTTP_OBJ_SECLEVEL')
            sub_seclevel = sub.seclevel

            if int(sub_seclevel) > int(obj_seclevel):
                start_response("403 Forbidden", [("Content-type", "text/plain"), ('sub', sub.seclevel),
                                                 ('obj', obj_seclevel)])
                return ["Secure Level Forbidden,Please Check the Levels!\n"]
            classes = object_info.get_parent_seclass(secid=obj_secl_id)  # the classes which the objects' all classes.
            for i in set(sub_classes):
                if i in classes.keys() or i in classes.values():
                    ss = self.app(env, start_response)
                    try:
                        dd = str(ss.next())
                    except Exception as e:
                        dd = str(e)
                    if 'resource' not in dd:
                        self.save(env, sub_seclevel, self.account_name,obj_path=obj)
                        if self.upload == 'True':
                            return self.app(env, start_response)
                        else:
                            start_response("404 Forbidden", [("Content-type", "text/plain")])
                            return str(self.upload)
                    else:
                        start_response("404 Forbidden", [("Content-type", "text/plain")])
                        return ['The Container:%s is Not Found\n' % container]
            start_response("404 Forbidden", [("Content-type", "text/plain")])
            return ["Secure field Forbidden: secure-field not match\n"]
        elif req.method == 'POST' and obj:
            # user = UserInfo(username=self.account_name, request=req)
            # sub = Subject(user)
            user = UserInfo(username=self.account_name, request=req)
            sub = Subject(user)
            sub_classes = []
            for secfd in sub.secfield:
                clas = Secfield(secfd, req).get_seclass()
                sub_classes += clas
            if user.response != 'True':
                start_response("404 Forbidden", [("Content-type", "text/plain")])
                return user.response
            obj_secl_id = env.get('HTTP_PARENT_SECL_ID', '')
            obj_seclevel = env.get('HTTP_OBJ_SECLEVEL', '')
            sub_seclevel = sub.seclevel
            if int(sub_seclevel) != int(obj_seclevel):
                start_response("404 Forbidden", [("Content-type", "text/plain"), ('sub', sub.seclevel), ('obj', obj_seclevel)])
                return ["The Level NOT Equal,Please Check Your Level!\n"]
            classes = obj.get_parent_seclass(secid=obj_secl_id)
            # new
            for i in set(sub_classes):
                if i in classes.keys() or i in classes.values():
                    self.save(env, start_response,obj_path=obj)
                    return self.app(env, start_response)
            # while x is not None:
            #     for secfd in sub.secfield:
            #         secfield = Secfield(secfd, req)
            #         if str(x) in secfield.get_seclass():
            #             self.save(env, start_response)
            #             return self.app(env, start_response)
            #     x = classes[x]
            start_response("404 Forbidden", [("Content-type", "text/plain")])
            return ["Secure field Forbidden: secure-field not match\n"]
        elif req.method == 'HEAD' and obj:
            print "HEAD",sub.__dict__
            print "conn",self.conn
            print "env",dir(env)
            print "obj",obj,"path",path
            print "---",env.get('PATH_INFO').split('/', 4)[-1]
            audio = Meta(path,req)
            if audio.response != 'True':
                start_response("111 Forbidden", [("Content-type", "text/plain")])
                return audio.response
            meta_info=audio.get_metadata_from_objname(obj)
            print "meta_info",meta_info.items()
            meta=[("Content-type", "text/plain"),('author',u'pad1')]
            for k in meta_info.keys():
                #meta.append((k,meta_info[k].encode('utf8')))
                item = meta_info[k].encode('utf8') if type(meta_info[k]) is unicode else meta_info[k]
                print type(item)
                meta.append((k,item))
            print "*********meta",meta
            #meta.append(meta_info.items())
            #self.cur = self.conn.cursor()
            #self.cur.execute("select ")
            #meta.append()
            #start_response("200 OK!", [("Content-type", "text/plain"),('author',u'pad1')])
            #start_response("200 OK!", [('parent_secl_id', 7L), ('object_name', u'\u5c0f\u9152\u7a9d'.encode('utf8'))])
            #self.getinfo
            start_response("200 OK!", meta)
            return self.app(env,start_response)
            #return ["Secure field Forbidden: secure-field not match\n"]

        elif req.method == 'DELETE' and obj:
            #user = UserInfo(username=self.account_name, request=req)
            #sub = Subject(user)
            print "del",user.__dict__
            print "del",sub.__dict__
            sub_classes = []
            if sub.secfield is None:
                start_response("404 Forbidden", [("Content-type", "text/plain")])
                return ["The Secfiled is None,Please Check Your secfield!\n"] 
            if sub.seclevel < 0 :
                start_response("404 Forbidden", [("Content-type", "text/plain")])
                return ["The Seclevel is Error,Please Check Your seclevel!\n"]
            for secfd in sub.secfield:
                clas = Secfield(secfd, req).get_seclass()
                sub_classes += clas
            n = self.cur.execute("select * from TMeta where path='%s'" % obj)
            if n == 0:
                start_response("404 Not Found", [([("Content-type", "text/plain")])])
                return ["Not Found this File,Please Check Your file's name\n"]
            secid = self.cur.fetchone()
            parent_id = secid[2]
            obj_level = secid[3]
            sub_seclevel = sub.seclevel
            print "===sub_seclevel===",sub_seclevel
            if int(sub_seclevel) != int(obj_level):
                start_response("404 Forbidden", [("Content-type", "text/plain"), ('sub', sub.seclevel), ('obj', obj_level)])
                return ["The Level NOT Equal,Please Check Your Level!\n"]
            classes = Object().get_parent_seclass(secid=parent_id)
            for i in set(sub_classes):
                if i in classes.keys() or i in classes.values():
                    cur1 = self.conn.cursor()
                    cur1.execute("delete from TMeta where path='%s'" % obj)
                    self.conn.commit()
                    cur1.close()
                    self.conn.close()
                    return self.app(env, start_response)
            start_response("404 Forbidden", [("Content-type", "text/plain"), ("par", classes)])
            return ["Secure field Forbidden: secure-field not match\n"]
        else:
            return self.app(env, start_response)

    def save(self, env, sub_seclevel=None, username=None,obj_path=None):
        self.conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd='root', db="auth", charset="utf8")
        self.cur = self.conn.cursor()
        method = env.get('REQUEST_METHOD', '')
        object_name = env.get('HTTP_OBJECT_NAME', '')
        parent_secl_id = env.get('HTTP_PARENT_SECL_ID', '')
        obj_seclevel = env.get('HTTP_OBJ_SECLEVEL', '')
        # author = account
        # author = env.get('PATH_INFO').split('/', 4)[2][5:]
        author = username
        #path = env.get('PATH_INFO').split('/', 4)[-1]
        if obj_path !=  None:
            path = obj_path
        else:
            path = env.get('PATH_INFO').split('/', 4)[-1]
        gen_time = datetime.datetime.now()
        types = env.get('CONTENT_TYPE', '')
        subject = env.get('HTTP_SUBJECT', '')
        description = env.get('HTTP_DESCRIPTION', '')
        language = env.get('HTTP_LANGUAGE', '')
        source = env.get('HTTP_SOURCE', '')
        values = (object_name, parent_secl_id, obj_seclevel, author, gen_time, path, types, subject, description, language, source)
        '''
        check whether the path exits.if exits,check the level
        is or not equal.if equal update.or return error
        '''
	print "=======================method:"
        if method == 'PUT':
            try:
                self.cur.execute('INSERT INTO TMeta(object_name, parent_secl_id, obj_seclevel, author, gen_time, path, type, subject, description, language, source) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', values)
            except Exception as e:
                if int(obj_seclevel) == int(sub_seclevel):
                    values1 = (object_name, parent_secl_id, obj_seclevel, author, gen_time, path, types, subject, description, language, source, path)
                    try:
                        self.cur.execute("UPDATE TMeta SET object_name=%s, parent_secl_id=%s, obj_seclevel=%s, author=%s, gen_time=%s, path=%s, type=%s, subject=%s, description=%s,language=%s, source=%s WHERE path=%s", values1)
                    except Exception as e:
                        self.upload = e
                else:
                    self.upload = str(e[1])+'and Secure Level not Equal!\n'
        elif method == 'POST':
            values1 = (object_name, parent_secl_id, obj_seclevel, author, gen_time, path, types, subject, description, language, source, path)
            self.cur.execute("UPDATE TMeta SET object_name=%s, parent_secl_id=%s, obj_seclevel=%s,author=%s, gen_time=%s, path=%s, type=%s, subject=%s, description=%s,language=%s, source=%s WHERE path=%s", values1)
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def denied_response(self, start_response, req):
        """
        Returns a standard WSGI response callable with the status of 403 or 401
        depending on whether the REMOTE_USER is set or not.
        """
        start_response("404 Forbidden", [("Content-type", "text/plain")])
        return req


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)
    register_swift_info('mac', account_acls=True)

    def acc_filter(app):
        return mandatory_access_control(app, conf)
    return acc_filter

