__author__ = 'Fuzhou Zou'

import webapp2
from google.appengine.api import users

from domain import common

class AdminManagePageHandler(webapp2.RequestHandler):
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        elif not self.getIsAdmin():
            self.redirect('/manage')
        else:
            self.render()

    def render(self):
        logout_url = users.create_logout_url(common.raw_logout_url)
        current_user = users.get_current_user().email()
        delete_owned_stream_handler_url = '/delete_all_streams'
        all_streams_info_list = self.getAllStreamsInfoList()
        is_admin = self.getIsAdmin()

        template_values = {
            'logout_url': logout_url,
            'current_user': current_user,
            'delete_all_streams_handler_url': delete_owned_stream_handler_url,
            'all_streams_info_list': all_streams_info_list,
            'is_admin': is_admin
        }

        template = common.JINJA_ENVIRONMENT.get_template('admin.html')
        self.response.write(template.render(template_values))

    def getAllStreamsInfoList(self):
        all_streams = common.Stream.query().fetch()
        all_streams_info_list = []
        for stream in all_streams:
            all_streams_info_list.append(self.getStreamInfo(stream.key))
        return all_streams_info_list

    def getStreamInfo(self, stream_key):
        stream_info = {}
        stream_info["key"] = stream_key
        stream_info["name"] = self.getStreamName(stream_key)
        stream_info["Owner"] = self.getStreamOwner(stream_key)
        stream_info["CreateDate"] = self.getStreamCreateDate(stream_key)
        stream_info["NumOfViews"] = self.getNumOfViews(stream_key)
        stream_info["NumOfImages"] = self.getNumOfImages(stream_key)
        return stream_info

    def getStreamName(self, stream_key):
        return stream_key.get().name

    def getStreamOwner(self, stream_key):
        return stream_key.get().owner

    def getStreamCreateDate(self, stream_key):
        return stream_key.get().creation_date.date()

    def getNumOfViews(self, stream_key):
        return stream_key.get().number_of_views

    def getNumOfImages(self, stream_key):
        image_list = self.getImageList(stream_key)
        return len(image_list)

    def getImageList(self, stream_key):
        image_query = common.Image.query(common.Image.stream_key == stream_key).order(-common.Image.upload_date)
        image_list = image_query.fetch()
        return image_list

    def getIsAdmin(self):
        return (users.get_current_user().email() == common.admin_email)