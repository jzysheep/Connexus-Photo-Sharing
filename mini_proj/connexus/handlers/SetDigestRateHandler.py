import time

import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb

from domain import common

class SetDigestRateHandler(webapp2.RequestHandler):
    def post(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url('/view_trending'))
        else:
            self.handleAndRedirect()

    def handleAndRedirect(self):
        self.setDigestRate()
        time.sleep(0.1)

        self.redirect('/view_trending')

    def setDigestRate(self):
        request_rate = self.getDigestRateRequest()

        key = self.getDigestRateKey()
        if key:
            self.updateDigestRate(key, request_rate)
        else:
            new_digest_rate = self.createDigestRate(request_rate)
            self.addDigestRate(new_digest_rate)

    def updateDigestRate(self, rate_key, rate_text):
        digest_rate = rate_key.get()
        digest_rate.rate = rate_text
        digest_rate.put()

    def createDigestRate(self, rate_text):
        new_digest_rate = common.DigestRate(parent=ndb.Key('DigestRateRepo', users.get_current_user().user_id()))
        new_digest_rate.populate(user=users.get_current_user().email(),
                                 rate=rate_text)
        return new_digest_rate

    def addDigestRate(self, rate):
        rate.put()

    def getDigestRateRequest(self):
        return self.request.get('digest_rate')

    def getDigestRate(self):
        digest_rate = common.DigestRate.query(common.DigestRate.user == users.get_current_user().email()).fetch()
        rate = 'no'
        for d in digest_rate:
            rate = d.rate
        return rate

    def getDigestRateKey(self):
        query = common.DigestRate.query(common.DigestRate.user == users.get_current_user().email())
        digest_rate = query.fetch()
        for rate in digest_rate:
            return rate.key
        return None