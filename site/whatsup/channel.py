from whatsup.db import session
from whatsup.db import get_title_from_chid
from whatsup.db import create_channel

from whatsup.task_queue import write_to_clients
from whatsup.core import channel_client_hash
from whatsup.task_queue import test_task

import whatsup.core
import tornado.web
import tornado.websocket

import uuid
import json
import datetime

PATH_TO_SITE = "../"
CHANNEL_PAGE = "channel.html"

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
			rows = get_title_from_chid(ch_id)

		if not rows:
			self.write("Channel does not exist")
		else:
			channel_title = rows[0].title
			self.render(PATH_TO_SITE+CHANNEL_PAGE, channel_title=channel_title, logged_in=logged_in, ch_id=ch_id)

class ChannelWebSocketHandler(tornado.websocket.WebSocketHandler):
	""" Handler for a channel room. 
	"""

	ch_id = None

	def open(self):
		print "Connection Opened"
		self.write_message({'sender': "server", 'msg': "New Connection Opened"})

	def on_message(self, message):
		# TODO: write message to buffer

		received_obj = json.loads(message)

		if received_obj['type'] == 'init':
			 
			ch_key = received_obj['msg']
			self.ch_id = ch_key

			if ch_key in channel_client_hash:
				channel_client_hash[ch_key].append(self)
			else:
				channel_client_hash[ch_key] = [self]
		elif received_obj['type'] == 'msg':
			# Get a timestamp
			now = datetime.datetime.now()
			date = now.date()
			time = now.time()
			ts = datetime.datetime.combine(date, time) # Need this for the db entry

			msg = received_obj['msg']
			user = received_obj['user']
			src = received_obj['src']

			# write_to_clients(user, msg, src, time)
			# write_to_clients.delay(user, msg, src, time)
			# retval = test_task.delay()
			# print retval.ready()

			# if retval.ready():
				# print retval.get()

			# for client in channel_client_hash[received_obj['src']]:
			# 	client.write_message({'msg': "%s" % received_obj['msg'], 'user': "%s" % received_obj['user'], 'ts': "%s" % time})
		elif received_obj['type'] == 'close':
			print "CLOSE MESSAGE RECEIVED"
			ch_key = received_obj['msg']
			channel_client_hash[ch_key].remove(self)
		else:
			raise Exception("received type from websocket is invalid")

	def on_close(self):
		print "Connection Closed"
		channel_client_hash[self.ch_id].remove(self)


# Create channels:
class CreateChannelHandler(whatsup.core.BaseHandler):
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

		create_channel(title, tag, length, dmy, hour, user, ch_id, url)

		self.redirect("/")