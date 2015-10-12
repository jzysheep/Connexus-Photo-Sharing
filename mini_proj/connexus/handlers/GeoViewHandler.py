__author__ = 'Ziyang Jiang'

from datetime import timedelta, datetime
import random

import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import images

from domain import common

class GeoViewHandler(webapp2.RequestHandler):
    def post(self):
        if not users.get_current_user():
            url = "/geo_view?stream_key=" + self.request.get("stream_key")
            self.redirect(users.create_login_url(url))
        else:
            self.render()

    def render(self):
        logout_url = users.create_logout_url(common.raw_logout_url)
        current_user = users.get_current_user().email()
        image_info = self.getGeoViewImageInfo()
        is_admin = self.getIsAdmin()

        template_values = {
            'logout_url': logout_url,
            'current_user': current_user,
            'image_info': image_info,
            'is_admin': is_admin
        }

        template = common.JINJA_ENVIRONMENT.get_template('geo_view.html')
        self.response.write(template.render(template_values))

    def getGeoViewImageInfo(self):
        stream_key = self.getStreamKey()

        images_info = []
        currentTime = datetime.now()
        aYearAgo = currentTime - timedelta(days=365)

        image_query = common.Image.query(common.Image.stream_key == stream_key).order(-common.Image.upload_date)
        image_list = image_query.fetch()

        for image in image_list:
            createTime = str(image.upload_date)
            # date_object = datetime.strptime(createTime, '%Y-%m-%d')

            lat = - 57.32652122521709 + 114.65304245043419 * random.random()
            lon = - 123.046875 + 246.09375 * random.random()

            # if aYearAgo <= date_object:
            images_info.append({
                "url": images.get_serving_url(image.blob_key),
                "lon": lon,
                "lat": lat,
                "createTime": createTime
            })

        return images_info

    def getStreamKey(self):
        try:
            return ndb.Key(urlsafe=self.request.get("stream_key"))
        except:
            self.redirect('/error?error_param=fatal_invalid_url')

    def getIsAdmin(self):
        return (users.get_current_user().email() == common.admin_email)