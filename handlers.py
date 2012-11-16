import webapp2
import jinja2
import os
import json
import logging

from urllib import quote, urlencode
from google.appengine.api import urlfetch

import headers
import ophan

jinja_environment = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

class MainPage(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template('index.html')
		
		template_values = {}

		self.response.out.write(template.render(template_values))

class MostViewed(webapp2.RequestHandler):
	def get(self):
		headers.json(self.response)

		ophan_json = ophan.popular()
		self.response.out.write(ophan_json)
