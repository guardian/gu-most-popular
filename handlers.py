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
import content_api

jinja_environment = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

def fresh(current_seconds):
	return (time.time() - current_seconds) < 5 * 60

def resolve_content(url):
	params = {'show-fields' : 'headline,thumbnail,trailText'}

	data = json.loads(content_api.read(content_api.content_id(url), params))
	return data.get('response', {}).get('content', {})

def read_ophan(section = None):
	if section:
		pass

	ophan_json = ophan.popular()

	if not ophan_json:
		raise deferred.PermanentTaskFailure()

	ophan_data = json.loads(ophan_json)

	client = memcache.Client()

	resolved_stories = [resolve_content(entry['url']) for entry in ophan_data]

	client = memcache.Client()
	client.set('all', json.dumps(resolved_stories))
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
			ophan_json = "[]"

		last_read = client.get(section_name + ".epoch_seconds")

		if last_read and not fresh(last_read):
			deferred.defer(read_ophan)

		headers.json(self.response)
		headers.set_cache_headers(self.response, 60)
		self.response.out.write(ophan_json)
