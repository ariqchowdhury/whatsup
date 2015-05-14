# Live group discussion using websockets
# Installation #

## Python ##
add a .sh to /etc/profile PYTHONPATH=$HOME/whatsup/site
```
$ apt-get install python-pip
$ apt-get install build-essential python-dev
```

## Tornado ##

```
$ pip install tornado
```

## Cassandra ##
Get latest tarball from http://cassandra.apache.org/download/

Follow instructions in README.txt

Get latest whatsup*.keyspace from Downloads to create the cassandra schema
```
$ cqlsh -f whatsup.keyspace
```

### Cassandra driver ###
https://github.com/datastax/python-driver

## Passlib ##
[Library](http://pythonhosted.org/passlib/index.html) for password hashing

```
$ pip install passlib
```

## Celery ##
```
$ pip install celery
$ sudo apt-get install rabbitmq-server
$ pip install librabbitmq
$ pip install tornado-celery
```
To start celery:
```
$ celery worker -A whatsup.task_queue --loglevel=info
```

## Redis ##
```
$ wget http://download.redis.io/redis-stable.tar.gz
$ tar xvzf redis-stable.tar.gz
$ cd redis-stable
$ make
$ sudo cp redis-server /usr/local/bin
$ sudo cp redis-cli /usr/local/bin
```
### redis-py ###
```
$ sudo pip install redis
```
Also install Hiredis:
```
$ sudo pip install hiredis
```

### html laundry ###
```
sudo apt-get install libxml2-dev libxslt1-dev
sudo pip install htmllaundry
```

### Webbit - java websockets ###
```
git clone git://github.com/webbit/webbit.git
https://code.google.com/p/json-simple/
```

### Jsoup ###
sanitize html in java

# Testing #
## Install Selenium ##
```
$ pip install selenium
```
