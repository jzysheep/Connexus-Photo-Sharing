__author__ = 'Fuzhou Zou'

import re
import time

import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import mail
from google.appengine.api import search

from domain import common

class CreateNewStreamHandler(webapp2.RequestHandler):
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        else:
            self.render()

    def post(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        else:
            self.handleAndRedirect()

    def render(self):
        logout_url = users.create_logout_url(common.raw_logout_url)
        current_user = users.get_current_user().email()
        is_admin = self.getIsAdmin()

        template_values = {
            'logout_url': logout_url,
            'current_user': current_user,
            'is_admin': is_admin
        }

        template = common.JINJA_ENVIRONMENT.get_template('create.html')
        self.response.write(template.render(template_values))

    def handleAndRedirect(self):
        new_stream = self.createNewStream()
        if self.getIsUsedStreamName(new_stream.name):
            self.redirect('/error?error_param=duplicate_stream_name')
        elif self.getIsEmptyStreamName(new_stream.name):
            self.redirect('/error?error_param=empty_stream_name')
        else:
            self.addNewStream(new_stream)
            self.sendInviteEmails(new_stream.key)
            self.updateSearchIndex(self.createSearchDocument(new_stream.key))

            time.sleep(0.1)
            self.redirect('/manage')

    def createNewStream(self):
        owner = self.getStreamOwner()
        name = self.getStreamName()
        tag_list = self.getStreamTagList()
        url = self.getStreamCoverURL()

        new_stream = common.Stream(parent=ndb.Key("StreamRepo", users.get_current_user().user_id()))
        new_stream.populate(owner=owner,
                            name=name,
                            tag_list=tag_list,
                            cover_photo_url=url
                            )
        return new_stream

    def addNewStream(self, new_stream):
        try:
            new_stream.put()
        except:
            self.redirect('/error?error_param=fatal_add_stream')

    def updateSearchIndex(self, document):
        try:
            index = search.Index(name="stream_index")
            index.put(document)
        except search.Error:
            self.redirect('/error?error_param=fatal_add_stream')

    def createSearchDocument(self, stream_key):
        doc = search.Document(
            doc_id=stream_key.urlsafe(),
            fields=[search.TextField(name='name', value=self.getStreamName()),
                    search.TextField(name='tags', value=" ".join(self.getStreamTagList())),
                    search.TextField(name='suggestion', value=self.getSubStrings())],
            language='en')
        return doc

    def getSubStrings(self):
        string_list = []
        str = self.getStreamName()
        length = len(str)
        string_list.extend([str[i:j+1] for i in xrange(length) for j in xrange(i, length)])
        return " ".join(string_list)

    def sendInviteEmails(self, stream_key):
        email_list = self.getStreamEmailList()
        view_stream_url = common.connexus_home + "/view_single?stream_key=" + stream_key.urlsafe()
        for to_email in email_list:
            if not self.getIsStreamOwner(to_email):
                email_message = self.createEmailMessage(to_email, view_stream_url)
                self.sendEmail(email_message)

    def sendEmail(self, message):
        try:
            message.send()
        except:
            # TODO: Add error handling code here
            pass

    def createEmailMessage(self, to_email_addr, view_stream_url):
        stream_name = self.getStreamName()
        optional_message = self.getOptionalMessage()

        message = mail.EmailMessage()
        sender_email = users.get_current_user().email()
        message.sender = "Connexus Support <%s>" % sender_email
        message.to = to_email_addr
        message.subject = "You're Invited to Subscribe Connexus Stream"
        message.body = common.invite_email_body % (stream_name, sender_email, optional_message, view_stream_url)
        return message

    def getIsStreamOwner(self, email):
        return (users.get_current_user().email() == email)

    def getIsUsedStreamName(self, name):
        stream_query = common.Stream.query(ndb.AND(common.Stream.owner == users.get_current_user().email(),
                                                   common.Stream.name == name))
        stream_list = stream_query.fetch()
        return (len(stream_list) > 0)

    def getIsEmptyStreamName(self, name):
        return not name

    def getStreamOwner(self):
        return users.get_current_user().email()

    def getStreamName(self):
        return self.request.get("stream_name")

    def getStreamTagList(self):
        raw_text = self.request.get("tag_list")
        return self.parseTagList(raw_text)

    def getStreamEmailList(self):
        raw_text = self.request.get("email_list")
        return self.parseEmailList(raw_text)

    def getOptionalMessage(self):
        raw_text = self.request.get("optional_message")
        message = "Please discover more about it on Connexus! "
        if raw_text:
            message += "Stream owner has left a message to you: %s" % raw_text
        return message

    def getStreamCoverURL(self):
        return self.request.get("image_url")

    def getStreamCount(self):
        query = common.Stream.query(common.Stream.owner == users.get_current_user().email())
        return query.count()

    def parseEmailList(self, emails):
        r = re.compile(r"[\w\.-]+@[\w\.-]+")
        email_list = r.findall(emails)
        return email_list

    def parseTagList(self, tags):
        r = re.compile(r"[#]\s*(\w+)")
        tag_list = r.findall(tags)
        return tag_list

    def getIsAdmin(self):
        return (users.get_current_user().email() == common.admin_email)