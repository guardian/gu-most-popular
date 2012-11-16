import webapp2
import handlers

app = webapp2.WSGIApplication([('/', handlers.MainPage),
								('/api/most-viewed', handlers.MostViewed),
								],
                              debug=True)