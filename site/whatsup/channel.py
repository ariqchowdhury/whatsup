import uuid
import datetime
import pytz

import tornado.web
import tornado.websocket
from tornado import gen
from htmllaundry import strip_markup

from whatsup.task_queue import get_channel_title_from_id, DecodeGetChannelTitleFromId, create_channel
import whatsup.core

PATH_TO_SITE = "../"
CHANNEL_PAGE = "channel.html"
CREATE_PAGE = "create.html"

channel_client_hash = {}
decode = DecodeGetChannelTitleFromId

def uuid_to_url(ch_id):
	return ch_id.bytes.encode('base_64').rstrip('=\n').replace('/', '_').replace('+', "-")

def url_to_uuid(url):
	missing_padding = 4 - len(url) % 4
	if missing_padding:
		url += b'=' * missing_padding

	return uuid.UUID(bytes=url.replace('_', '/').replace('-', '+').decode('base_64'))	 


class ChannelHandler(whatsup.core.BaseHandler):
	""" Renders the html page when a user enters a channel.
		Creates a WebSocket connection on entry.
	"""

	@tornado.web.removeslash
	@tornado.web.asynchronous
	@gen.coroutine
	def get(self, url):
		logged_in = True if self.current_user else False

		try:
			ch_id = url_to_uuid(url)
		except ValueError:
			# This exception is raised if the url length is incorrect for the url decode
			# This likely means user entered their own url, so just go to does not exist
			ch_id = url
			rows = None
		else:
			response = yield gen.Task(get_channel_title_from_id.apply_async, args=[ch_id])
			rows = response.result

		if not rows:
			self.write("Channel does not exist")
		else:
			channel_title = rows[0][decode.title]
			self.render(PATH_TO_SITE+CHANNEL_PAGE, channel_title=channel_title, logged_in=logged_in, ch_id=ch_id)


# Create channels:
class CreateChannelHandler(whatsup.core.BaseHandler):
	@tornado.web.asynchronous
	@gen.coroutine
	def post(self):
		title = strip_markup(self.get_argument("title"))
		tag = strip_markup(self.get_argument("tag"))
		length = strip_markup(self.get_argument("length"))
		dmy = strip_markup(self.get_argument("start_date"))
		hour = strip_markup(self.get_argument("hour"))
		user = self.current_user
		ch_id = uuid.uuid4()
		url = uuid_to_url(ch_id)

		length = int(length)
		hour = ''.join([dmy, " ", hour])
		dmy = ''.join([dmy, " ", "00:00"])
		datetime_dmy = datetime.datetime.strptime(dmy, '%Y-%m-%d %H:%M')
		datetime_start = datetime.datetime.strptime(hour, '%Y-%m-%d %H:%M')

		utc = pytz.timezone('UTC')
		datetime_dmy = utc.localize(datetime_dmy)
		datetime_start = utc.localize(datetime_start)

		print datetime_dmy
		print datetime_start

		#timestamp will just use cassandra getdate(now())
		# Need to insert into all channel column families, see: db_sechma for columns
		yield gen.Task(create_channel.apply_async, args=[title, tag, length, datetime_dmy, datetime_start, user, ch_id, url])

		self.redirect("/ch/%s" % url)

class Create(whatsup.core.BaseHandler):
	@tornado.web.asynchronous
	@gen.coroutine
	def get(self):
		logged_in = True if self.current_user else False
		self.render(PATH_TO_SITE+CREATE_PAGE, logged_in=logged_in)