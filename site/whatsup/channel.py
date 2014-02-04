import uuid
import json

import tornado.web
import tornado.websocket
from tornado import gen

from whatsup.task_queue import write_to_db, GetChannelTitleFromId, DecodeGetChannelTitleFromId, CreateChannel
import whatsup.core

PATH_TO_SITE = "../"
CHANNEL_PAGE = "channel.html"

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
		if self.current_user:
			logged_in = True
		else:
			logged_in = False

		try:
			ch_id = url_to_uuid(url)
		except ValueError:
			# This exception is raised if the url length is incorrect for the url decode
			# This likely means user entered their own url, so just go to does not exist
			ch_id = url
			rows = None
		else:
			response = yield gen.Task(GetChannelTitleFromId.apply_async, args=[ch_id])
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
		title = self.get_argument("title")
		tag = self.get_argument("tag")
		length = self.get_argument("length")
		dmy = self.get_argument("start_date")
		hour = self.get_argument("hour")
		user = self.current_user
		ch_id = uuid.uuid4()
		url = uuid_to_url(ch_id)
		
		#timestamp will just use cassandra getdate(now())
		# Need to insert into all channel column families, see: db_sechma for columns

		yield gen.Task(CreateChannel.apply_async, args=[title, tag, length, dmy, hour, user, ch_id, url])

		self.redirect("/ch/%s" % url)