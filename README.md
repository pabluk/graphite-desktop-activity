Graphite Desktop Activity
=========================

Feeds Graphite with your desktop activity


Installation
------------

On Debian systems you need to install python-xlib

```bash
sudo apt-get install python-xlib
```

Usage
-----

For example
```bash
$ ./desktop-activity --daemon --server graphite.example.com
```

You can see more options with `--help`

```bash
$ ./desktop-activity --help
usage: desktop-activity [-h] [-s SERVER] [-p PORT] [-l LOG_FILE] [-d] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        Carbon server name or IP address. Default: 127.0.0.1
  -p PORT, --port PORT  Carbon server port. Default: 2003
  -l LOG_FILE, --log-file LOG_FILE
                        Log messages to file
  -d, --daemon          Run as a daemon in background
  -v, --verbose         Show debug messages
```


Screenshot
----------

![Screenshot](http://seminar.io/media/screenshots/desktop-activity.png)
