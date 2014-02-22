import datetime
from os import system

import redis

from whatsup.task_queue import generate_frontpage
from whatsup.task_queue import DecodeGenerateFrontpage

if __name__ == "__main__":
	decode = DecodeGenerateFrontpage

	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	r.set("key", "Redis Working")

	result = r.get("key")
	print result

	today = datetime.datetime.now()
	# today.strftime("%Y-%m-%d")

	rows = generate_frontpage.delay(datetime.datetime(2014, 1, 17, 8))
	flist = rows.get()

	system("redis-cli KEYS 'featured:*' | xargs redis-cli DEL")

	for i, item in enumerate(flist):
		r.set("featured:%s:title" % i, "%s" % item[decode.title])
		r.set("featured:%s:tag" % i, "%s" % item[decode.tag])
		r.set("featured:%s:start" % i, "%s" % item[decode.start].time())
		r.set("featured:%s:url" % i, "%s" % item[decode.url])
		r.set("featured:%s:dmy" % i, "%s" % item[decode.dmy])



