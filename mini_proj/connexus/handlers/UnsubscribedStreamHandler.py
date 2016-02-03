import time

import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb

from domain import common

class UnsubscribedStreamHandler(webapp2.RequestHandler):
    def post(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url('/manage'))
        else:
            self.handleAndRedirect()

    def handleAndRedirect(self):
        self.unsubscribeStreams()

        time.sleep(0.1)
        self.redirect('/manage')

    def unsubscribeStreams(self):
        stream_keys = self.getToUnsubscribeStreamKeys()
        for key in stream_keys:
            self.unsubscribeSingleStream(key)

    def unsubscribeSingleStream(self, stream_key):
        try:
            stream = stream_key.get()
            stream_key.get().subscriber_list.remove(users.get_current_user().email())
            stream.put()
        except:
            self.redirect('/error?error_param=fatal_unsubscribe')

    def getToUnsubscribeStreamKeys(self):
        stream_key_urls = self.request.get_all("unsubscribe")
        unsubscribe_stream_keys = [ndb.Key(urlsafe=url) for url in stream_key_urls]
        return unsubscribe_stream_keys

    def getSubscribedStreamCount(self):
        query = common.Stream.query(common.Stream.subscriber_list.IN([users.get_current_user().email(),]))
        return query.count()