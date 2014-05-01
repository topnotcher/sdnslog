import socket,os, pwd, grp, datetime, argparse, select, MySQLdb


def ip2n(ip):
    octets = ip.split('.')
    return sum([(int(octets[x]))<<(24-(8*x)) for x in range(0,4)])

class MySQLQueryLogger(object):
    def __init__(self, db, host, user, passwd):
        self.tbl = 'queries'
        self.db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
    
    def log_query(self,query):
        values = {
                'src': ip2n(query['src']),
                'dst': ip2n(query['dst']),
                'name': query['name'],
                'type': query['type'],
                'last_time': query['time'],
                'hits' : 1
        }

        fields_str = ','.join(["`%s`" % (key) for key in values.keys()])
        values_str = ','.join(["'%s'" % (self.db.escape_string(str(value))) for value in values.values()])
        query = "INSERT INTO `%s` (%s) VALUES (%s) ON DUPLICATE KEY UPDATE \
                `last_time` = VALUES(`last_time`), \
                `hits` = `hits` + 1;" % (self.tbl, fields_str, values_str)
        self.db.cursor().execute(query)
        self.db.commit()

def get_uid(user):
    return pwd.getpwnam(user).pw_uid

def get_gid(group):
    return grp.getgrnam(group).gr_gid

def drop_privileges(user,group):
    uid = get_uid(user)
    gid = get_gid(group)

    os.setgroups([])
    os.setgid(gid)
    os.setuid(uid)

def init_sockets(sock_paths, user, group):
    socks = []

    for path in sock_paths:
        if os.path.exists(path):
            os.remove(path)

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        sock.bind(path)

        os.chown(path,get_uid(user),get_gid(group))
        os.chmod(path, 0700)

        socks.append(sock)

    return socks

def parse_query_log(log_fields):
    query = {}
    query['time'] = datetime.datetime.strptime(log_fields[0], '%m/%d/%Y-%H:%M:%S.%f').strftime('%Y-%m-%d %H:%M:%S')
    query['name'] = log_fields[2]
    query['type'] = log_fields[3]
    src,dst = [x.strip() for x in log_fields[4].split('->', 1)]
    query['src'], src_port = src.split(':',2)
    query['dst'], dst_port = dst.split(':',2)

    return query

def read_socket(sock, logger):
    dgm = sock.recv(1024)

    if not dgm:
        return;

    log = [x.strip() for x in dgm.strip().split('[**]')]
    
    if not log[1].startswith('Query TX'): 
        return
    
    query = parse_query_log(log)

    logger.log_query(query)

def monitor_sockets(socks, logger):

    while True:
        rd,wr,err = select.select(socks, [], [])
        
        for sock in rd:
            read_socket(sock, logger)

def main():
    parser = argparse.ArgumentParser(description='Parse suricata DNS logs from \
            a unix socket and log queries to a MySQL database.')
    parser.add_argument('-s','--socket', nargs='+', help='a unix dgram socket to monitor', required=True)
    parser.add_argument('-u', '--user', help='user to drop to after creating the socket', required=True)
    parser.add_argument('-g', '--group', help='group to drop to after creating the socket', required=True)

    args = parser.parse_args()

    socks = init_sockets(args.socket, args.user, args.group)
    drop_privileges(args.user, args.group)

    logger = MySQLQueryLogger('dnslog','shockwave','test','test')

    monitor_sockets(socks, logger)

if __name__ == '__main__':
    main()


