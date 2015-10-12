__author__ = 'Fuzhou Zou'

import os
import jinja2

from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), '../templates')),
                                       extensions=['jinja2.ext.autoescape'],
                                       autoescape=True)
app_id = 'skilled-orbit-108304'
connexus_home = 'http://' + app_id + '.appspot.com'
admin_email = 'zoufuzhouclipper@gmail.com'
raw_logout_url = '/'
raw_login_url = '/manage'

invite_email_body = """
Dear Sir or Madam,

You have been invited to subscribe Connexus stream("%s") from a registered Connexus user(%s).

%s

Please click the following link to confirm your subscription:
%s

Best,
Connexus Support Group
"""

digest_email_body = """
Dear Connexus user,

Based on our record, you have registered to receive Connexus Stream digest email %s.

Please click the following link to view the hottest Connexus Streams:
%s

You could always change your digest email settings on the same page.

Best,
Connexus Support Group
"""

class Image(ndb.Model):
    stream_key = ndb.KeyProperty()
    blob_key = ndb.BlobKeyProperty()
    upload_date = ndb.DateTimeProperty(auto_now_add=True)
    comments = ndb.TextProperty(required=False)

class Stream(ndb.Model):
    owner = ndb.StringProperty()
    name = ndb.StringProperty()
    subscriber_list = ndb.StringProperty(repeated=True)
    tag_list = ndb.StringProperty(repeated=True)
    cover_photo_url = ndb.StringProperty(required=False)
    creation_date = ndb.DateTimeProperty(auto_now_add=True)
    number_of_views = ndb.IntegerProperty(default=0)

class View(ndb.Model):
    stream_key = ndb.KeyProperty()
    recent_view_dates = ndb.DateTimeProperty(repeated=True)
    num_of_views = ndb.ComputedProperty(lambda e: len(e.recent_view_dates))

class DigestRate(ndb.Model):
    user = ndb.StringProperty()
    rate = ndb.StringProperty()