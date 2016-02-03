import re
import urllib2
import json

import webapp2
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.api import search

from domain import common

class SearchStreamHandler(webapp2.RequestHandler):
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        else:
            self.render()

    def render(self):
        logout_url = users.create_logout_url(common.raw_logout_url)
        current_user = users.get_current_user().email()
        stream_list = self.getSearchMatchedStreamInfoList()
        num_of_cols = 4
        is_admin = self.getIsAdmin()

        template_values = {
            'logout_url': logout_url,
            'current_user': current_user,
            'stream_list': stream_list,
            'num_of_cols': num_of_cols,
            'is_admin': is_admin
        }

        template = common.JINJA_ENVIRONMENT.get_template('search.html')
        self.response.write(template.render(template_values))

    def getSearchMatchedStreamInfoList(self):
        stream_keys = self.getSearchMatchedStreams()
        stream_list = [self.getSingleStreamInfo(key) for key in stream_keys]
        return stream_list

    def getSearchMatchedStreams(self):
        search_str = self.getSearchString()
        if not self.getIsValidString(search_str):
            return []

        query = self.createQuery(search_str)
        index = search.Index(name="stream_index")
        try:
            results = index.search(query)
            stream_keys = []
            for doc in results:
                stream_keys.append(ndb.Key(urlsafe=doc.doc_id))
            return stream_keys
        except search.Error:
            self.redirect('/error?error_param=fatal_search')

    def createQuery(self, search_str):
        query_str = self.getQueryString(search_str)
        sort = search.SortExpression(expression='name', direction=search.SortExpression.ASCENDING)
        sort_opts = search.SortOptions(expressions=[sort])
        query_options = search.QueryOptions(
            limit=20,
            sort_options=sort_opts
        )
        query = search.Query(query_string=query_str, options=query_options)
        return query

    def getQueryString(self, search_str):
        name_query = 'name=' + search_str
        tag_query = 'tags=' + search_str
        combined_query = ' OR '.join([name_query, tag_query])
        return combined_query

    def getIsValidString(self, str):
        r = re.compile(r"\b(\w+)\b")
        return r.findall(str) != []

    def getSearchString(self):
        raw_str = self.request.get("search_str")
        r = re.compile('([^\s\w])+')
        search_str = r.sub('', raw_str)
        return search_str

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

class SearchSuggestionHandler(webapp2.RequestHandler):
    def post(self):
        search_str = self.getSearchString()
        resp = self.getSuggestion(search_str)
        self.response.out.write(resp)

    def getSearchString(self):
        return self.request.get("search_str")

    def getSuggestion(self, search_str):
        resp = {}
        resp['search_str'] = search_str
        resp['streams'] = self.getSuggestedStreams(search_str)
        # Convert unicode to javascript string
        return json.dumps(resp)

    def getSuggestedStreams(self, search_str):
        search_str = self.getValidString(search_str)
        if not self.getIsValidString(search_str):
            return []

        query = self.createQuery(search_str)
        index = search.Index(name="stream_index")
        try:
            results = index.search(query)
            stream_names = []
            for doc in results:
                stream_names.append(doc.fields[0].value)
            return stream_names
        except search.Error:
            self.redirect('/error?error_param=fatal_search')

    def getValidString(self, str):
        r = re.compile('([^\s\w])+')
        str = r.sub('', str)
        return str

    def getIsValidString(self, str):
        r = re.compile(r"\b(\w+)\b")
        return r.findall(str) != []

    def createQuery(self, search_str):
        query_string = self.getQueryString(search_str)
        sort = search.SortExpression(expression='name', direction=search.SortExpression.ASCENDING)
        sort_opts = search.SortOptions(expressions=[sort])
        query_options=search.QueryOptions(
            limit=20,
            sort_options=sort_opts,
        )
        query = search.Query(query_string=query_string, options=query_options)
        return query

    def getQueryString(self, search_str):
        query = 'suggestion=' + search_str
        return query