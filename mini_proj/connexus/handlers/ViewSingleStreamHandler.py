__author__ = 'Fuzhou Zou'

import datetime

import webapp2
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.api import images

from domain import common

class ViewSingleStreamHandler(webapp2.RequestHandler):
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        else:
            self.setCookies('refresh')
            self.render()

    def render(self):
        stream_key = self.getStreamKey()
        if not stream_key:
            self.redirect('/error?error_param=fatal_invalid_url')
            return

        if self.getIsSubscriber(stream_key) and self.getIsAnotherView():
            self.updateStreamViewCount(stream_key)
            self.updateRecentView(stream_key)

        stream_name = self.getStreamName(stream_key)
        upload_url = blobstore.create_upload_url(self.getUploadURL(stream_key))
        logout_url = users.create_logout_url(common.raw_logout_url)
        current_user = users.get_current_user().email()
        image_urls = self.getImageURLs(stream_key)
        num_of_cols = 3
        image_window_urls = self.getImageWindowURLs(image_urls, num_of_cols)
        view_more_url = self.getViewMoreURL(stream_key)
        view_more_button_visible = self.getIsViewMoreButtonVisible(len(image_urls), num_of_cols)
        geo_view_visible = (len(image_urls) > 0)
        geo_view_url = self.getGeoViewURL(stream_key)
        subscribe_url = self.getSubscribeHandlerURL(stream_key)
        is_stream_owner = self.getIsStreamOwner(stream_key)
        is_subscribed = self.getIsSubscriber(stream_key)
        is_admin = self.getIsAdmin()

        template_values = {
            'stream_name': stream_name,
            'upload_url': upload_url,
            'logout_url': logout_url,
            'current_user': current_user,
            'image_window_urls': image_window_urls,
            'view_more_url': view_more_url,
            'view_more_button_visible': view_more_button_visible,
            'geo_view_visible': geo_view_visible,
            'geo_view_url': geo_view_url,
            'subscribe_url': subscribe_url,
            'is_stream_owner': is_stream_owner,
            'is_subscribed': is_subscribed,
            'num_of_cols': num_of_cols,
            'is_admin': is_admin
        }

        template = common.JINJA_ENVIRONMENT.get_template('view_single.html')
        self.response.write(template.render(template_values))

    def updateRecentView(self, stream_key):
        view_key = self.getViewKey(stream_key)
        if not view_key:
            new_view = self.createNewView(stream_key)
            self.addNewView(new_view)
        else:
            self.appendDateToExistingView(view_key)

    def createNewView(self, stream_key):
        new_view = common.View(parent=ndb.Key("ViewRepo", users.get_current_user().user_id()))
        new_view.populate(stream_key=stream_key,
                          recent_view_dates=[datetime.datetime.now()])
        return new_view

    def addNewView(self, new_view):
        try:
            new_view.put()
        except:
            self.redirect('/error?error_param=fatal_add_view')

    def appendDateToExistingView(self, view_key):
        try:
            view = view_key.get()
            view.recent_view_dates.append(datetime.datetime.now())
            view.put()
        except:
            self.redirect('/error?error_param=fatal_update_view')

    def getViewKey(self, stream_key):
        view_list = common.View.query(common.View.stream_key == stream_key).fetch()
        for view in view_list:
            return view.key
        return None

    def updateStreamViewCount(self, stream_key):
        self.setStreamNumOfViewCount(stream_key)

    def setStreamNumOfViewCount(self, stream_key):
        try:
            stream = stream_key.get()
            stream.number_of_views += 1
            stream.put()
        except:
            self.redirect('/error?error_param=fatal_update_view')

    def getIsViewMoreButtonVisible(self, num_of_images, num_of_cols):
        return (num_of_images > num_of_cols)

    def getIsSubscriber(self, stream_key):
        return (users.get_current_user().email() in stream_key.get().subscriber_list)

    def getStreamNumOfViewCount(self, stream_key):
        return stream_key.get().number_of_views

    def getStreamOwner(self, stream_key):
        return stream_key.get().owner

    def getIsStreamOwner(self, stream_key):
        return (stream_key.get().owner == users.get_current_user().email())

    def getStreamName(self, stream_key):
        return stream_key.get().name

    def getUploadURL(self, stream_key):
        url = "/upload?stream_key=" + stream_key.urlsafe()
        return url

    def getViewMoreURL(self, stream_key):
        url = "/view_more?stream_key=" + stream_key.urlsafe()
        return url

    def getGeoViewURL(self, stream_key):
        url = "/geo_view?stream_key=" + stream_key.urlsafe()
        return url

    def getSubscribeHandlerURL(self, stream_key):
        handler_url = '/subscribe?stream_key=' + stream_key.urlsafe()
        return handler_url

    def getImageURLs(self, stream_key):
        image_query = common.Image.query(common.Image.stream_key == stream_key).order(-common.Image.upload_date)
        image_list = image_query.fetch()
        image_urls = [images.get_serving_url(image.blob_key) for image in image_list]
        return image_urls

    def getImageWindowURLs(self, image_urls, window_size):
        num_of_images = len(image_urls)
        if (num_of_images <= window_size):
            return image_urls
        else:
            index = self.getCookies('index')
            urls = []
            for i in xrange(index, index + window_size):
                urls.append(image_urls[i % num_of_images])
            return urls

    def getStreamKey(self):
        try:
            return ndb.Key(urlsafe=self.request.get("stream_key"))
        except:
            return None

    def getIsAnotherView(self):
        return (self.getCookies('index') == 0) and (self.getCookies('refresh') == 0)

    def setCookies(self, name):
        index = self.getCookies(name) + 1
        self.response.headers.add_header('Set-Cookie', '%s=%s' % (name, index))

    def getCookies(self, name):
        return int(self.request.cookies.get(name, 0))

    def getIsAdmin(self):
        return (users.get_current_user().email() == common.admin_email)