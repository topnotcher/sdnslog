```
usage: sdnslog [-h] -c CONFIG [-s SOCKET [SOCKET ...]] [-d] [-u USER]
               [-g GROUP]

Parse suricata DNS logs from a unix socket and log queries to a MySQL
database.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        path to configuration file
  -s SOCKET [SOCKET ...], --socket SOCKET [SOCKET ...]
                        a unix dgram socket to monitor
  -d, --daemon          daemonize
  -u USER, --user USER  user to drop to after creating the socket
  -g GROUP, --group GROUP
                     group to drop to after creating the socket
```
