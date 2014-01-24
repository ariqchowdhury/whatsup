import tornado.web
import tornado.websocket

from celery import Celery
from celery import Task

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster 
from cassandra.query import SimpleStatement

# Cassandra settings
KEYSPACE = "whatsup_dev"
CASS_IP = '127.0.0.1'
cluster = Cluster([CASS_IP])

app = Celery('whatsup', backend='amqp://guest@localhost', broker='amqp://guest@localhost//')

CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = ['pickle']

# class MsgBufferTask(Task):
# 	abstract = True
# 	_channel_client_hash = None

# 	@property 
# 	def cch(self):
# 		if self._channel_client_hash is None:
# 			self._channel_client_hash = channel_client_hash
# 		return self._channel_client_hash

class DatabaseTask(Task):
	abstract = True
	_db = None

	@property
	def db(self):
		if self._db is None:
			self._db = cluster.connect()
			self._db.set_keyspace(KEYSPACE)
		return self._db

@app.task
def write_to_clients(ts, user, msg, src, time):
	print user

@app.task(base=DatabaseTask)
def write_to_db(ts, user, msg, src, time, comment_id):
	
	write_to_db.db.execute("""
		INSERT INTO comment (id, user, data, score, ts)
		VALUES (%s, '%s', '%s', 0, dateof(now()));
		""" % (comment_id, user, msg))

	write_to_db.db.execute("""
		INSERT INTO comment_channel_index (cmnt_id, ch_id)
		VALUES (%s, %s);
		""" % (comment_id, src))



# for client in channel_client_hash[src]:
		# client.write_message({'msg': "%s" % msg, 'user': "%s" % user, 'ts': "%s" % time})