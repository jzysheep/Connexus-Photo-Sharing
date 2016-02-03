import time

import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import search

from domain import common

class DeleteStreamHandler(webapp2.RequestHandler):
    def deleteStreams(self):
        stream_keys = self.getToDeleteStreamKeys()
        for key in stream_keys:
            self.deleteSingleStream(key)

    def deleteSingleStream(self, stream_key):
        self.deleteStreamImages(stream_key)
        self.deleteRecentViewStream(stream_key)
        self.deleteSearchIndex(stream_key)
        try:
            stream_key.delete()
        except:
            self.redirect('/error?error_param=fatal_del_stream')

    def deleteSearchIndex(self, stream_key):
        index = search.Index(name="stream_index")
        index.delete(stream_key.urlsafe())

    def deleteRecentViewStream(self, stream_key):
        try:
            view_key = self.getRecentViewStreamKey(stream_key)
            view_key.delete()
        except:
            self.redirect('/error?error_param=fatal_del_view')

    def deleteStreamImages(self, stream_key):
        image_query = common.Image.query(common.Image.stream_key == stream_key)
        image_list = image_query.fetch()
        for img in image_list:
            self.deleteSingleImage(img.key)

    def deleteSingleImage(self, image_key):
        try:
            blobstore.delete(image_key.get().blob_key)
            image_key.delete()
        except:
            self.redirect('/error?error_param=fatal_del_image')

    def getRecentViewStreamKey(self, stream_key):
        view_query = common.View.query(common.View.stream_key == stream_key)
        view_list = view_query.fetch()
        for view in view_list:
            return view.key

    def getStreamCount(self):
        return 0

    def getToDeleteStreamKeys(self):
        return []

class DeleteOwnedStreamHandler(DeleteStreamHandler):
    def post(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url('/manage'))
        else:
            self.handleAndRedirect()

    def handleAndRedirect(self):
        self.deleteStreams()

        time.sleep(0.1)
        url = '/manage'
        self.redirect(url)

    def getToDeleteStreamKeys(self):
        stream_key_urls = self.request.get_all("delete_owned")
        to_delete_stream_keys = [ndb.Key(urlsafe=url) for url in stream_key_urls]
        return to_delete_stream_keys

    def getStreamCount(self):
        query = common.Stream.query(common.Stream.owner == users.get_current_user().email())
        return query.count()

class DeleteAllStreamsHandler(DeleteStreamHandler):
    def post(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url('/admin'))
        else:
            self.handleAndRedirect()

    def handleAndRedirect(self):
        self.deleteStreams()

        time.sleep(0.1)
        self.redirect('/admin')

    def getToDeleteStreamKeys(self):
        stream_key_urls = self.request.get_all("delete_admin")
        to_delete_stream_keys = [ndb.Key(urlsafe=url) for url in stream_key_urls]
        return to_delete_stream_keys

    def getStreamCount(self):
        query = common.Stream.query()
        return query.count()

