import redis

from whatsup.task_queue import generate_frontpage
from whatsup.task_queue import DecodeGenerateFrontpage

if __name__ == "__main__":
	decode = DecodeGenerateFrontpage

	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	r.set("key", "Redis Working")

	result = r.get("key")
	print result

	rows = generate_frontpage.delay('2014-01-17')
	flist = rows.result

	for i in range(0, len(flist[:10])):
		r.set("featured:%s:title" % i, "%s" % flist[i][decode.title])
		r.set("featured:%s:tag" % i, "%s" % flist[i][decode.tag])
		r.set("featured:%s:start" % i, "%s" % flist[i][decode.start].time())
		r.set("featured:%s:url" % i, "%s" % flist[i][decode.url])
		r.set("featured:%s:dmy" % i, "%s" % flist[i][decode.dmy])



