from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster 
from cassandra.query import SimpleStatement

# Cassandra settings
KEYSPACE = "whatsup_dev"
CASS_IP = '127.0.0.1'

cluster = Cluster([CASS_IP])
session = cluster.connect()
session.set_keyspace(KEYSPACE)