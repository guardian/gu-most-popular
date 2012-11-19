import webapp2
import handlers

app = webapp2.WSGIApplication([
	('/', handlers.MainPage),
		webapp2.Route(r'/api/most-viewed/<section_id>', handler = handlers.MostViewed),
		webapp2.Route(r'/api/most-viewed', handler = handlers.MostViewed),
		],
		debug=True)