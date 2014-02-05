from whatsup.task_queue import write_to_db
import sys
import uuid

if __name__ == "__main__":
	username = sys.argv[1]
	message = sys.argv[2]
	_src = sys.argv[3]

	#TODO: message needs to be sanitized here for db entry. Entering qutoes messes things up right now '', ""

	src = uuid.UUID(_src)
	comment_id = uuid.uuid4()

	write_to_db.delay(username, message, src, comment_id)