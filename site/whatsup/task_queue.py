import tornado.web
import tornado.websocket

from celery import Celery
from celery import Task

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster 
from cassandra.query import SimpleStatement

from whatsup.password import pwd_context

# Enums for the order of objects in rows
class DecodeGenerateFrontpage:
	title, tag, start, url, dmy = range(5)

class DecodeGetHashedPswd:
	salt, pswd = range(2)

class DecodeGetChannelTitleFromId:
	title = 0

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

def SanitizeCassRows(cass_rows):
	myrows = []

	for row in cass_rows:
	  mylist=[]
	  myrows.append(mylist)
	  for datum in row:
	    mylist.append(datum)

	return myrows

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
def CreateChannel(title, tag, length, dmy, hour, user, ch_id, url):
	CreateChannel.db.execute("""
			INSERT INTO channels (id, dmy, start, ts, len, user, title, tag, url)
			VALUES (%s, '%s', '%s', dateof(now()), %s, '%s', '%s', '%s', '%s');
			""" % (ch_id, dmy, dmy+" "+hour, length, user, title, tag, url))

	CreateChannel.db.execute("""
		INSERT INTO channels_by_id (id, dmy, start, ts, len, user, title, tag, url)
		VALUES (%s, '%s', '%s', dateof(now()), %s, '%s', '%s', '%s', '%s');
		""" % (ch_id, dmy, dmy+" "+hour, length, user, title, tag, url))

	CreateChannel.db.execute("INSERT INTO user_channel_index (user, ch_id) VALUES ('%s', %s);" % (user, ch_id))

@app.task(base=DatabaseTask)
def generate_frontpage(date):
	rows = generate_frontpage.db.execute("SELECT title, tag, start, url, dmy FROM channels WHERE dmy='%s' ORDER BY start;" % date)
	return SanitizeCassRows(rows)

@app.task(base=DatabaseTask)
def get_hashed_pswd(username):
	rows = get_hashed_pswd.db.execute("SELECT salt, pswd FROM users where user='%s'" % username)
	return SanitizeCassRows(rows)

@app.task
def verify_password(salted_pswd, hashed_pswd):
	return pwd_context.verify(salted_pswd, hashed_pswd)

@app.task
def EncryptPassword(salted_pswd):
	return pwd_context.encrypt(salted_pswd)

@app.task(base=DatabaseTask)
def DoesUserExist(username):
	rows = DoesUserExist.db.execute("SELECT * FROM users where user='%s'" % username)
	return SanitizeCassRows(rows)

@app.task(base=DatabaseTask)
def AddUser(username, salt, hash, email):
	AddUser.db.execute("INSERT INTO users (user, salt, pswd, email) VALUES ('%s', '%s', '%s', '%s');" % (username, salt, hash, email))

@app.task(base=DatabaseTask)
def GetChannelTitleFromId(ch_id):
	rows = GetChannelTitleFromId.db.execute("SELECT title from channels_by_id WHERE id=%s" % ch_id)
	return SanitizeCassRows(rows)
