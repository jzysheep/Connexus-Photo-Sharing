import webapp2

class UpdateCookiesHandler(webapp2.RequestHandler):
    def get(self):
        self.handleAndRedirect()

    def handleAndRedirect(self):
        self.resetCookies('index')
        self.resetCookies('refresh')

        url = "/view_single?stream_key=" + self.request.get("stream_key")
        self.redirect(url)

    def resetCookies(self, name):
        self.response.headers.add_header('Set-Cookie', '%s=%s' % (name, 0))
