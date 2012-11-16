import webapp2
import jinja2
import os
import json
import logging
import time

from urllib import quote, urlencode
from google.appengine.api import urlfetch
from google.appengine.api import memcache
from google.appengine.ext import deferred


import headers
import ophan

jinja_environment = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

def read_ophan(section = None):
	if section:
		pass

	ophan_json = ophan.popular()

	if ophan_json:
		client = memcache.Client()
		client.set('all', ophan_json)
		client.set('all.epoch_seconds', time.time())	


class MainPage(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template('index.html')
		
		template_values = {}

		self.response.out.write(template.render(template_values))

class MostViewed(webapp2.RequestHandler):
	def get(self):
		section_name = 'all'

		client = memcache.Client()

		ophan_json = client.get(section_name)
		
		if not ophan_json:
			deferred.defer(read_ophan)
			ophan_json = "{}"

		last_read = client.get(section_name + ".epoch_seconds")

		if last_read and (time.time() - last_read) > 5 * 60:
			deferred.defer(read_ophan)

		headers.json(self.response)
		self.response.out.write(ophan_json)
