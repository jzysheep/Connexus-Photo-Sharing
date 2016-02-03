import urllib2

import webapp2
from google.appengine.api import users
from google.appengine.api import images

from domain import common

class ViewAllStreamsHandler(webapp2.RequestHandler):
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        else:
            self.render()

    def render(self):
        logout_url = users.create_logout_url(common.raw_logout_url)
        current_user = users.get_current_user().email()
        stream_list = self.getAllStreamInfoList()
        num_of_cols = 4
        is_admin = self.getIsAdmin()

        template_values = {
            'logout_url': logout_url,
            'current_user': current_user,
            'stream_list': stream_list,
            'num_of_cols': num_of_cols,
            'is_admin': is_admin
        }

        template = common.JINJA_ENVIRONMENT.get_template('view_all.html')
        self.response.write(template.render(template_values))

    def getAllStreamInfoList(self):
        stream_query = common.Stream.query().order(common.Stream.creation_date)
        stream_list = stream_query.fetch()
        stream_info_list = []
        for stream in stream_list:
            stream_info_list.append(self.getSingleStreamInfo(stream.key))
        return stream_info_list

    def getSingleStreamInfo(self, stream_key):
        stream_info = {}
        stream_info["key"] = stream_key
        stream_info["name"] = self.getStreamName(stream_key)
        stream_info["cover_photo_url"] = self.getCoverPhotoURL(stream_key)
        return stream_info

    def getStreamName(self, stream_key):
        return stream_key.get().name

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

    def getIsAdmin(self):
        return (users.get_current_user().email() == common.admin_email)
