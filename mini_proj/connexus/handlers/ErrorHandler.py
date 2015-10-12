__author__ = 'Fuzhou Zou'

import webapp2
from google.appengine.api import users

from domain import common

class ErrorHandler(webapp2.RequestHandler):
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        else:
            self.render()

    def render(self):
        logout_url = users.create_logout_url(common.raw_logout_url)
        current_user = users.get_current_user().email()
        error_message = self.parseErrorMessage(self.request.get("error_param"))
        is_admin = self.getIsAdmin()

        template_values = {
            'logout_url': logout_url,
            'current_user': current_user,
            'error_message': error_message,
            'is_admin': is_admin
        }

        template = common.JINJA_ENVIRONMENT.get_template('error.html')
        self.response.write(template.render(template_values))

    def parseErrorMessage(self, error_param):
        message = "Error: "
        if error_param == "duplicate_stream_name":
            message += "You tried to create a new stream whose name is the same as one existing stream!\n"
        elif error_param == "empty_stream_name":
            message += "You tried to create a new stream whose name is empty!\n"
        elif error_param == "fatal_add_stream":
            message += "Exception @adding a new stream. Please contact Connexus support."
        elif error_param == "fatal_del_image":
            message += "Exception @deleting a stream image. Please contact Connexus support."
        elif error_param == "fatal_del_view":
            message += "Exception @deleting a stream view. Please contact Connexus support."
        elif error_param == "fatal_del_stream":
            message += "Exception @deleting a stream. Please contact Connexus support."
        elif error_param == "fatal_add_image":
            message += "Exception @adding a stream image. Please contact Connexus support."
        elif error_param == "fatal_invalid_url":
            message += "Exception @Invalid URL specified. Please double check your URL or contact Connexus support."
        elif error_param == "fatal_unsubscribe":
            message += "Exception @unsubscribing a stream. Please contact Connexus support."
        elif error_param == "fatal_add_view":
            message += "Exception @adding a stream view. Please contact Connexus support."
        elif error_param == "fatal_update_view":
            message += "Exception @updating a stream view. Please contact Connexus support."
        elif error_param == "fatal_search":
            message += "Exception @search. Please contact Connexus support."
        else:
            message += "Unexpected service failure! Please contact Connexus support."

        return message

    def getIsAdmin(self):
        return (users.get_current_user().email() == common.admin_email)