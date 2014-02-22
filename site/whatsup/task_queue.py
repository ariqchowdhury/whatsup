import uuid

from celery import Celery
from celery import Task

from cassandra.cluster import Cluster 

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

def sanitize_cass_rows(cass_rows):
	myrows = []

	for row in cass_rows:
	  mylist=[]
	  myrows.append(mylist)
	  for datum in row:
	    mylist.append(datum)

	return myrows

@app.task(base=DatabaseTask)
def write_to_db(user, msg, src, comment_id):	
	p1 = write_reply_to_db.db.prepare("""
        INSERT INTO comment (id, user, data, score, ts)
        VALUES (?, ?, ?, 0, dateof(now()))
		""")

	p2 = write_reply_to_db.db.prepare("""
        INSERT INTO comment_channel_index (cmnt_id, ch_id)
        VALUES (?, ?)
		""")

	comment_id_as_uuid = uuid.UUID(comment_id)
	src_as_uuid = uuid.UUID(src)

	create_channel.db.execute(p1.bind((comment_id_as_uuid, user, msg)))
	create_channel.db.execute(p2.bind((comment_id_as_uuid, src_as_uuid)))

@app.task(base=DatabaseTask)
def write_reply_to_db(user, msg, src, comment_id, parent_id):

	p1 = write_reply_to_db.db.prepare("""
        INSERT INTO comment (id, user, data, score, ts)
        VALUES (?, ?, ?, 0, dateof(now()))
		""")

	p2 = write_reply_to_db.db.prepare("""
        INSERT INTO comment_channel_index (cmnt_id, ch_id)
        VALUES (?, ?)
		""")

	p3 = write_reply_to_db.db.prepare("""
        INSERT INTO comment_reply_index (cmnt_id, rep_id)
        VALUES (?, ?)
		""")

	comment_id_as_uuid = uuid.UUID(comment_id)
	src_as_uuid = uuid.UUID(src)
	parent_id_as_uuid = uuid.UUID(parent_id)

	create_channel.db.execute(p1.bind((comment_id_as_uuid, user, msg)))
	create_channel.db.execute(p2.bind((comment_id_as_uuid, src_as_uuid)))
	create_channel.db.execute(p3.bind((parent_id_as_uuid, comment_id_as_uuid)))

@app.task(base=DatabaseTask)
def create_channel(title, tag, length, dmy, hour, user, ch_id, url):

	p1 = create_channel.db.prepare("""
        INSERT INTO channels (id, dmy, start, ts, len, user, title, tag, url)
        VALUES (?, ?, ?, dateof(now()), ?, ?, ?, ?, ?)
		""")

	p2 = create_channel.db.prepare("""
        INSERT INTO channels_by_id (id, dmy, start, ts, len, user, title, tag, url)
        VALUES (?, ?, ?, dateof(now()), ?, ?, ?, ?, ?)
		""")

	p3 = create_channel.db.prepare("""
        INSERT INTO user_channel_index (user, ch_id) VALUES (?, ?)
		""")

	create_channel.db.execute(p1.bind((ch_id, dmy, hour, length, user, title, tag, url)))
	create_channel.db.execute(p2.bind((ch_id, dmy, hour, length, user, title, tag, url)))
	create_channel.db.execute(p3.bind((user, ch_id)))


@app.task(base=DatabaseTask)
def generate_frontpage(date):
	p = generate_frontpage.db.prepare("SELECT title, tag, start, url, dmy FROM channels WHERE dmy=? ORDER BY start;")
	rows = generate_frontpage.db.execute(p.bind((date,)))
	return sanitize_cass_rows(rows)

@app.task(base=DatabaseTask)
def get_hashed_pswd(username):
	p = get_hashed_pswd.db.prepare("SELECT salt, pswd FROM users where user=?")
	rows = get_hashed_pswd.db.execute(p.bind((username,)))
	return sanitize_cass_rows(rows)

@app.task
def verify_password(salted_pswd, hashed_pswd):
	return pwd_context.verify(salted_pswd, hashed_pswd)

@app.task
def encrypt_password(salted_pswd):
	return pwd_context.encrypt(salted_pswd)

@app.task(base=DatabaseTask)
def does_user_exist(username):
	p = does_user_exist.db.prepare("SELECT * FROM users where user=?")
	rows = does_user_exist.db.execute(p.bind((username,)))
	return sanitize_cass_rows(rows)

@app.task(base=DatabaseTask)
def add_user(username, salt, hash, email):
	p = add_user.db.prepare("INSERT INTO users (user, salt, pswd, email) VALUES (?, ?, ?, ?);")
	add_user.db.execute(p.bind((username, salt, hash, email)))

@app.task(base=DatabaseTask)
def get_channel_title_from_id(ch_id):
	p = get_channel_title_from_id.db.prepare("SELECT title from channels_by_id WHERE id=?")
	rows = get_channel_title_from_id.db.execute(p.bind((ch_id,)))
	return sanitize_cass_rows(rows)

