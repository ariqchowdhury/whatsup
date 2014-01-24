import tornado.web
import tornado.websocket
from whatsup.core import channel_client_hash

from celery import Celery



app = Celery('whatsup', backend='amqp://guest@localhost', broker='amqp://guest@localhost//')

@app.task(name='whatsup.task_queue.write_to_clients')
def write_to_clients(user, msg, src, time):
	print channel_client_hash
	print user
	print msg
	print src

@app.task(name='whatsup.task_queue.test_task')
def test_task():
	return 5




# for client in channel_client_hash[src]:
		# client.write_message({'msg': "%s" % msg, 'user': "%s" % user, 'ts': "%s" % time})