import webapp2
from google.appengine.api import users

from domain import common

class ManagePageHandler(webapp2.RequestHandler):
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        else:
            self.render()

    def render(self):
        logout_url = users.create_logout_url(common.raw_logout_url)
        current_user = users.get_current_user().email()
        delete_owned_stream_handler_url = '/delete_owned_stream'
        unsubscribe_stream_handler_url = '/unsubscribe_stream'
        owned_stream_info_list = self.getOwnedStreamInfoList()
        subscribed_stream_info_list = self.getSubscribedStreamInfoList()
        is_admin = self.getIsAdmin()

        template_values = {
            'logout_url': logout_url,
            'current_user': current_user,
            'delete_owned_stream_handler_url': delete_owned_stream_handler_url,
            'unsubscribe_stream_handler_url': unsubscribe_stream_handler_url,
            'owned_stream_info_list': owned_stream_info_list,
            'subscribed_stream_info_list': subscribed_stream_info_list,
            'is_admin': is_admin
        }

        template = common.JINJA_ENVIRONMENT.get_template('manage.html')
        self.response.write(template.render(template_values))

    def getOwnedStreamInfoList(self):
        owned_streams = common.Stream.query(common.Stream.owner == users.get_current_user().email())
        owned_stream_info_list = []
        for stream in owned_streams:
            owned_stream_info_list.append(self.getStreamInfo(stream.key))
        return owned_stream_info_list

    def getSubscribedStreamInfoList(self):
        subscribed_streams = common.Stream.query(common.Stream.subscriber_list.IN([users.get_current_user().email(),]))
        subscribed_stream_info_list = []
        for stream in subscribed_streams:
            subscribed_stream_info_list.append(self.getStreamInfo(stream.key))
        return subscribed_stream_info_list

    def getStreamInfo(self, stream_key):
        stream_info = {}
        stream_info["key"] = stream_key
        stream_info["name"] = self.getStreamName(stream_key)
        stream_info["NumOfViews"] = self.getNumOfViews(stream_key)
        stream_info["LatestImageDate"] = self.getLatestImageDate(stream_key)
        stream_info["NumOfImages"] = self.getNumOfImages(stream_key)
        return stream_info

    def getStreamName(self, stream_key):
        return stream_key.get().name

    def getNumOfViews(self, stream_key):
        return stream_key.get().number_of_views

    def getImageList(self, stream_key):
        image_query = common.Image.query(common.Image.stream_key == stream_key).order(-common.Image.upload_date)
        image_list = image_query.fetch()
        return image_list

    def getLatestImageDate(self, stream_key):
        image_list = self.getImageList(stream_key)
        if image_list:
            return image_list[0].upload_date.date()
        else:
            return "N/A"

    def getNumOfImages(self, stream_key):
        image_list = self.getImageList(stream_key)
        return len(image_list)

    def getIsAdmin(self):
        return (users.get_current_user().email() == common.admin_email)