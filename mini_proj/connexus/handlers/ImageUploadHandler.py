__author__ = 'Fuzhou Zou'

import json

import webapp2
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb

from domain import common

class ImageUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        if not users.get_current_user():
            self.handleAndRelogin()
        else:
            self.handleAndRedirect()

    def handleAndRelogin(self):
        if self.getUploadIsValid():
            blob_key = self.get_uploads()[0].key()
            blobstore.delete(blob_key)

        url = "/view_single?stream_key=" + self.request.get("stream_key")
        self.redirect(users.create_login_url(url))

    def handleAndRedirect(self):
        if self.getUploadIsValid():
            new_image = self.createNewImage()
            self.addNewImage(new_image)

        url = "/update_cookies?stream_key=" + self.request.get("stream_key")
        self.redirect(url)

    def createNewImage(self):
        stream_key = self.getStreamKey()
        blob_key = self.get_uploads()[0].key()
        comments = self.request.get("comments")

        new_image = common.Image(parent=ndb.Key("ImageRepo", users.get_current_user().user_id()))
        new_image.populate(stream_key=stream_key,
                           blob_key=blob_key,
                           comments=comments
                           )
        return new_image

    def getUploadIsValid(self):
        return self.get_uploads()

    def addNewImage(self, image):
        try:
            image.put()
        except:
            self.redirect('/error?error_param=fatal_add_image')

    def getImageCount(self):
        query = common.Image.query(common.Image.stream_key == self.getStreamKey())
        return query.count()

    def getStreamKey(self):
        try:
            return ndb.Key(urlsafe=self.request.get("stream_key"))
        except:
            self.redirect('/error?error_param=fatal_invalid_url')

class ImageUploadURLGenerationHandler(webapp2.RequestHandler):
    def post(self):
        upload_url = blobstore.create_upload_url(self.getUploadURL())
        resp = self.getResponse(upload_url)
        self.response.out.write(resp)

    def getUploadURL(self):
        url = "/upload?stream_key=" + self.request.get('stream_key')
        return url

    def getResponse(self, upload_url):
        resp = {}
        resp['upload_url'] = upload_url
        return json.dumps(resp)