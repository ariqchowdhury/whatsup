import tornado.web
import tornado.websocket

from celery import Celery
from celery import Task

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster 
from cassandra.query import SimpleStatement

# Enums for the order of objects in rows
class DecodeGenerateFrontpage:
	title, tag, start, url, dmy = range(5)

# Cassandra settings
KEYSPACE = "whatsup_dev"
CASS_IP = '127.0.0.1'
cluster = Cluster([CASS_IP])

app = Celery('whatsup', backend='amqp://guest@localhost', broker='amqp://guest@localhost//')

CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = ['pickle']

class DatabaseTask(Task):
	abstract = True
	_db = None

	@property
	def db(self):
		if self._db is None:
			self._db = cluster.connect()
			self._db.set_keyspace(KEYSPACE)
		return self._db


@app.task(base=DatabaseTask)
def write_to_db(user, msg, src, comment_id):
	
	write_to_db.db.execute("""
		INSERT INTO comment (id, user, data, score, ts)
		VALUES (%s, '%s', '%s', 0, dateof(now()));
		""" % (comment_id, user, msg))

	write_to_db.db.execute("""
		INSERT INTO comment_channel_index (cmnt_id, ch_id)
		VALUES (%s, %s);
		""" % (comment_id, src))

@app.task(base=DatabaseTask)
def generate_frontpage(date):
	rows = generate_frontpage.db.execute("SELECT title, tag, start, url, dmy FROM channels WHERE dmy='%s' ORDER BY start;" % date)
	
	myrows = []

	for row in rows:
	  mylist=[]
	  myrows.append(mylist)
	  for datum in row:
	    mylist.append(datum)

	return myrows