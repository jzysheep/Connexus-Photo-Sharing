__author__ = 'Fuzhou Zou'

import datetime

import webapp2

from domain import common

class UpdateTrendingStreamHandler(webapp2.RequestHandler):
    def get(self):
        self.updateViews()

    def updateViews(self):
        view_key_list = self.getViewKeyList()
        for view_key in view_key_list:
            self.updateSingleView(view_key)

    def updateSingleView(self, view_key):
        recent_view = view_key.get()
        view_dates = recent_view.recent_view_dates
        index = self.getFirstNonObsoleteDateIndex(view_dates)
        recent_view.recent_view_dates = view_dates[index:]
        recent_view.put()

    def getFirstNonObsoleteDateIndex(self, date_list):
        cutoff_date = datetime.datetime.now() - datetime.timedelta(hours=1)
        index = next((index for index in xrange(len(date_list)) if date_list[index] >= cutoff_date), len(date_list))
        return index

    def getViewKeyList(self):
        recent_views = common.View.query(common.View.num_of_views > 0).fetch()
        view_keys = [view.key for view in recent_views]
        return view_keys
