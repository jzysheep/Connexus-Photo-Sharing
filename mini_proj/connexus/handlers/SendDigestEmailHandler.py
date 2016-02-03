import webapp2
from google.appengine.api import mail

from domain import common

class SendDigestEmail(webapp2.RequestHandler):
    def get(self):
        email_list = self.getReceiverList()
        for to_addr in email_list:
            email_message = self.createEmail(to_addr)
            self.sendEmail(email_message)

    def createEmail(self, to_email_addr):
        message = mail.EmailMessage()
        sender_email = 'connexus@' + common.app_id + '.appspotmail.com'
        message.sender = 'Connexus Support <%s>' % sender_email
        message.to = to_email_addr
        message.subject = 'Connexus Trending Stream Digest'
        message.body = common.digest_email_body % (self.getDigestRateText(), self.getTrendingPageURL())
        return message

    def sendEmail(self, message):
        message.send()

    def getReceiverList(self):
        return []

    def getDigestRateText(self):
        return ""

    def getTrendingPageURL(self):
        url = common.connexus_home + '/view_trending'
        return url

class SendDigestEmailPerFiveMinute(SendDigestEmail):
    def getReceiverList(self):
        query = common.DigestRate.query(common.DigestRate.rate == 'per_5min')
        digest_rate_list = query.fetch()
        user_list = [rate.user for rate in digest_rate_list]
        return user_list

    def getDigestRateText(self):
        return 'every 5 minutes'

class SendDigestEmailPerHour(SendDigestEmail):
    def getReceiverList(self):
        query = common.DigestRate.query(common.DigestRate.rate == 'per_1hr')
        digest_rate_list = query.fetch()
        user_list = [rate.user for rate in digest_rate_list]
        return user_list

    def getDigestRateText(self):
        return 'every 1 hour'


class SendDigestEmailPerDay(SendDigestEmail):
    def getReceiverList(self):
        query = common.DigestRate.query(common.DigestRate.rate == 'per_1day')
        digest_rate_list = query.fetch()
        user_list = [rate.user for rate in digest_rate_list]
        return user_list

    def getDigestRateText(self):
        return 'every 1 day'
