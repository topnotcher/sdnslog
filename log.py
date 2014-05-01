import socket,os, pwd, grp, datetime, argparse

sock_path = '/var/run/suricata-megatron-dns.log'


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
        if os.path.exists(sock_path):
            os.remove(sock_path)

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        sock.bind(path)

        os.chown(path,get_uid(user),get_gid(group))
        os.chmod(path, 0700)

        socks.append(sock)

    return socks

def main():
    parser = argparse.ArgumentParser(description='Parse suricata DNS logs from \
            a unix socket and log queries to a MySQL database.')
    parser.add_argument('-s','--socket', nargs='+', help='a unix dgram socket to monitor', required=True)
    parser.add_argument('-u', '--user', help='user to drop to after creating the socket', required=True)
    parser.add_argument('-g', '--group', help='group to drop to after creating the socket', required=True)

    args = parser.parse_args()

    sock = init_sockets(args.socket, args.user, args.group)[0]
    drop_privileges(args.user, args.group)
   
    while True:
        dgm = sock.recv(1024)
        if not dgm:
            break;

        log = [x.strip() for x in dgm.strip().split('[**]')]
        
        if not log[1].startswith('Query TX'): 
            continue

        time = datetime.datetime.strptime(log[0], '%m/%d/%Y-%H:%M:%S.%f')
        name = log[2]
        type = log[3]
        src,dst = [x.strip() for x in log[4].split('->', 1)]
        src_ip, src_port = src.split(':',2)
        dst_ip, dst_port = dst.split(':',2)
        

        print '%s %s %s %s -> %s' % (str(time), type, name, src_ip, dst_ip)




if __name__ == '__main__':
    main()


