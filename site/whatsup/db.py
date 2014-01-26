from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster 
from cassandra.query import SimpleStatement

# Cassandra settings
KEYSPACE = "whatsup_dev"
CASS_IP = '127.0.0.1'

cluster = Cluster([CASS_IP])
session = cluster.connect()
session.set_keyspace(KEYSPACE)

#DEPRECATED -- replaced by task_queue.generate_frontpage
def read_events_for_frontpage(date):
	return session.execute("SELECT title, tag, start, url, dmy FROM channels WHERE dmy='%s' ORDER BY start;" % date);

def user_password_check(username):
	return session.execute("SELECT salt, pswd FROM users where user='%s'" % username)

def is_user_in_db(username):
	return session.execute("SELECT * FROM users where user='%s'" % username)

def insert_user_into_db(username, salt, hash):
	session.execute("INSERT INTO users (user, salt, pswd) VALUES ('%s', '%s', '%s');" % (username, salt, hash))

def get_title_from_chid(ch_id):
	return session.execute("SELECT title from channels_by_id WHERE id=%s" % ch_id)

def create_channel(title, tag, length, dmy, hour, user, ch_id, url):
	session.execute("""
			INSERT INTO channels (id, dmy, start, ts, len, user, title, tag, url)
			VALUES (%s, '%s', '%s', dateof(now()), %s, '%s', '%s', '%s', '%s');
			""" % (ch_id, dmy, dmy+" "+hour, length, user, title, tag, url))

	session.execute("""
		INSERT INTO channels_by_id (id, dmy, start, ts, len, user, title, tag, url)
		VALUES (%s, '%s', '%s', dateof(now()), %s, '%s', '%s', '%s', '%s');
		""" % (ch_id, dmy, dmy+" "+hour, length, user, title, tag, url))

	session.execute("INSERT INTO user_channel_index (user, ch_id) VALUES ('%s', %s);" % (user, ch_id))