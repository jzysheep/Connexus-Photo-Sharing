#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import webapp2
from google.appengine.api import users

from domain import common
from handlers.ManagePageHandler import ManagePageHandler
from handlers.CreateNewStreamHandler import CreateNewStreamHandler
from handlers.ViewSingleStreamHandler import ViewSingleStreamHandler
from handlers.ViewAllStreamsHandler import ViewAllStreamsHandler
from handlers.ImageUploadHandler import ImageUploadHandler
from handlers.ImageUploadHandler import ImageUploadURLGenerationHandler
from handlers.SubscribeStreamHandler import SubscribeStreamHandler
from handlers.DeleteStreamHandler import DeleteOwnedStreamHandler
from handlers.UnsubscribedStreamHandler import UnsubscribedStreamHandler
from handlers.SearchStreamHandler import SearchStreamHandler
from handlers.SearchStreamHandler import SearchSuggestionHandler
from handlers.ViewTrendingStreamHandler import ViewTrendingStreamHandler
from handlers.UpdateTrendingStreamHandler import UpdateTrendingStreamHandler
from handlers.SetDigestRateHandler import SetDigestRateHandler
from handlers.SendDigestEmailHandler import SendDigestEmailPerFiveMinute
from handlers.SendDigestEmailHandler import SendDigestEmailPerHour
from handlers.SendDigestEmailHandler import SendDigestEmailPerDay
from handlers.ViewMorePicturesHandler import ViewMorePicturesHandler
from handlers.GeoViewHandler import GeoViewHandler
from handlers.UpdateCookiesHandler import UpdateCookiesHandler
from handlers.ErrorHandler import ErrorHandler
from handlers.AdminManagePageHandler import AdminManagePageHandler
from handlers.DeleteStreamHandler import DeleteAllStreamsHandler

class MainHandler(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            login_url = '/manage'
            self.redirect(login_url)
        else:
            login_url = users.create_login_url('/manage')

        template_values = {
            'login_url': login_url,
        }

        template = common.JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/manage', ManagePageHandler),
    ('/create', CreateNewStreamHandler),
    ('/view_single', ViewSingleStreamHandler),
    ('/view_all', ViewAllStreamsHandler),
    ('/upload', ImageUploadHandler),
    ('/upload_url_gen', ImageUploadURLGenerationHandler),
    ('/subscribe', SubscribeStreamHandler),
    ('/delete_owned_stream', DeleteOwnedStreamHandler),
    ('/unsubscribe_stream', UnsubscribedStreamHandler),
    ('/search', SearchStreamHandler),
    ('/search_suggest', SearchSuggestionHandler),
    ('/view_trending', ViewTrendingStreamHandler),
    ('/update_trending', UpdateTrendingStreamHandler),
    ('/set_digest_rate', SetDigestRateHandler),
    ('/send_digest_per_5min', SendDigestEmailPerFiveMinute),
    ('/send_digest_per_hour', SendDigestEmailPerHour),
    ('/send_digest_per_day', SendDigestEmailPerDay),
    ('/view_more', ViewMorePicturesHandler),
    ('/geo_view', GeoViewHandler),
    ('/update_cookies', UpdateCookiesHandler),
    ('/error', ErrorHandler),
    ('/admin', AdminManagePageHandler),
    ('/delete_all_streams', DeleteAllStreamsHandler)
], debug=True)
