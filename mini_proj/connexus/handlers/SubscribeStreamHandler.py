__author__ = 'Fuzhou Zou'

import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb

class SubscribeStreamHandler(webapp2.RequestHandler):
    def post(self):
        if not users.get_current_user():
            self.handleAndRelogin()
        else:
            self.handleAndRedirect()

    def handleAndRelogin(self):
        url = "/view_single?stream_key=" + self.request.get("stream_key")
        self.redirect(users.create_login_url(url))

    def handleAndRedirect(self):
        stream_key = self.getStreamKey()
        if self.getIsSubscribed(stream_key):
            self.setUnsubscribed(stream_key)
        else:
            self.setSubscribed(stream_key)

        url = "/view_single?stream_key=" + self.request.get("stream_key")
        self.redirect(url)

    def getIsSubscribed(self, stream_key):
        subscriber_list = stream_key.get().subscriber_list
        return (users.get_current_user().email() in subscriber_list)

    def setUnsubscribed(self, stream_key):
        stream = stream_key.get()
        stream.subscriber_list.remove(users.get_current_user().email())
        stream.put()

    def setSubscribed(self, stream_key):
        stream = stream_key.get()
        stream.subscriber_list.append(users.get_current_user().email())
        stream.put()

    def getStreamKey(self):
        try:
            return ndb.Key(urlsafe=self.request.get("stream_key"))
        except:
            self.redirect('/error?error_param=fatal_invalid_url')