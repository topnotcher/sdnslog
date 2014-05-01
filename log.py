import socket,os, pwd, grp, datetime, argparse, select

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
    query['time'] = datetime.datetime.strptime(log_fields[0], '%m/%d/%Y-%H:%M:%S.%f')
    query['name'] = log_fields[2]
    query['type'] = log_fields[3]
    src,dst = [x.strip() for x in log_fields[4].split('->', 1)]
    query['src'], src_port = src.split(':',2)
    query['dst'], dst_port = dst.split(':',2)

    return query

def read_socket(sock):
    dgm = sock.recv(1024)

    if not dgm:
        return;

    log = [x.strip() for x in dgm.strip().split('[**]')]
    
    if not log[1].startswith('Query TX'): 
        return
    
    query = parse_query_log(log)

    print '%s %s %s %s -> %s' % (str(query['time']), query['type'], query['name'], query['src'], query['dst'])

def monitor_sockets(socks):

    while True:
        rd,wr,err = select.select(socks, [], [])
        
        for sock in rd:
            read_socket(sock)

def main():
    parser = argparse.ArgumentParser(description='Parse suricata DNS logs from \
            a unix socket and log queries to a MySQL database.')
    parser.add_argument('-s','--socket', nargs='+', help='a unix dgram socket to monitor', required=True)
    parser.add_argument('-u', '--user', help='user to drop to after creating the socket', required=True)
    parser.add_argument('-g', '--group', help='group to drop to after creating the socket', required=True)

    args = parser.parse_args()

    socks = init_sockets(args.socket, args.user, args.group)
    drop_privileges(args.user, args.group)
   
    monitor_sockets(socks)

if __name__ == '__main__':
    main()


