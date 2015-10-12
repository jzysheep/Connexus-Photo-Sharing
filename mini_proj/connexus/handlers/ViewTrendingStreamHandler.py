__author__ = 'Fuzhou Zou'

import urllib2

import webapp2
from google.appengine.api import users
from google.appengine.api import images

from domain import common

class ViewTrendingStreamHandler(webapp2.RequestHandler):
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        else:
            self.render()

    def render(self):
        logout_url = users.create_logout_url(common.raw_logout_url)
        current_user = users.get_current_user().email()
        trending_streams = self.getStreamInfoList()
        num_of_streams = len(trending_streams)
        digest_rate = self.getDigestRate()
        is_admin = self.getIsAdmin()

        template_values = {
            'logout_url': logout_url,
            'current_user': current_user,
            'trending_streams': trending_streams,
            'num_of_streams': num_of_streams,
            'digest_rate': digest_rate,
            'is_admin': is_admin
        }

        template = common.JINJA_ENVIRONMENT.get_template('view_trending.html')
        self.response.write(template.render(template_values))

    def getStreamInfoList(self):
        key_list = self.getViewKeyList()
        key_list.sort(key=lambda key: self.getRecentNumOfViews(key), reverse=True)
        stream_info_list = [self.getStreamInfo(key) for key in key_list[0:3]]
        return stream_info_list

    def getViewKeyList(self):
        recent_views = common.View.query(common.View.num_of_views > 0).fetch()
        key_list = [v.key for v in recent_views]
        return key_list

    def getStreamKey(self, view_key):
        return view_key.get().stream_key

    def getRecentNumOfViews(self, view_key):
        return view_key.get().num_of_views

    def getStreamName(self, stream_key):
        return stream_key.get().name

    def getStreamInfo(self, view_key):
        stream_info = {}
        stream_key = self.getStreamKey(view_key)
        stream_info["key"] = stream_key
        stream_info["name"] = self.getStreamName(stream_key)
        stream_info["cover_photo_url"] = self.getCoverPhotoURL(stream_key)
        stream_info["num_of_views"] = self.getRecentNumOfViews(view_key)
        return stream_info

    def getCoverPhotoURL(self, stream_key):
        cover_url = stream_key.get().cover_photo_url
        try:
            urllib2.urlopen(urllib2.Request(cover_url), timeout=1)
            return cover_url
        except:
            cover_url = self.getMostRecentImageURL(stream_key)
            if cover_url:
                return cover_url[0]
            else:
                cover_url = "http://placehold.it/300x200&text=[No Cover Photo]"
                return cover_url

    def getMostRecentImageURL(self, stream_key):
        image_query = common.Image.query(common.Image.stream_key == stream_key).order(-common.Image.upload_date)
        image = image_query.fetch(1)
        image_url = [images.get_serving_url(img.blob_key) for img in image]
        return image_url

    def getDigestRate(self):
        digest_rate = common.DigestRate.query(common.DigestRate.user == users.get_current_user().email()).fetch()
        rate = 'no'
        for d in digest_rate:
            rate = d.rate
        return rate

    def getIsAdmin(self):
        return (users.get_current_user().email() == common.admin_email)