import webapp2
from google.appengine.api import users

class ViewMorePicturesHandler(webapp2.RequestHandler):
    def post(self):
        if not users.get_current_user():
            url = "/view_single?stream_key=" + self.request.get("stream_key")
            self.redirect(users.create_login_url(url))
        else:
            self.handleAndRedirect()

    def handleAndRedirect(self):
        self.setCookies('index')

        url = "/view_single?stream_key=" + self.request.get("stream_key")
        self.redirect(url)

    def setCookies(self, name):
        index = self.getCookies(name) + 1
        self.response.headers.add_header('Set-Cookie', '%s=%s' % (name, index))

    def getCookies(self, name):
        return int(self.request.cookies.get(name, 0))
