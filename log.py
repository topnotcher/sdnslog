import socket,os, pwd, grp, datetime

sock_path = '/var/run/suricata-megatron-dns.log'


def get_uid():
    return pwd.getpwnam('suricata').pw_uid

def get_gid():
    return grp.getgrnam('suricata').gr_gid

def drop_root():
    uid = get_uid()
    gid = get_gid()

    os.setgroups([])
    os.setgid(gid)
    os.setuid(uid)
    

def main():
    if os.path.exists(sock_path):
        os.remove(sock_path)


    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    sock.bind(sock_path)

    os.chown(sock_path,get_uid(),get_gid())
    os.chmod(sock_path, 0700)


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


