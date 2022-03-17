import socket

def get_one_ip():
    serv_ip = {}
    for service in services:
        serv_ip[service] = socket.gethostbyname(service)
    # print(serv_ip)
    return serv_ip

def get_all_ip():
    serv_ip = {}
    for service in services:
        serv_ip[service] = socket.gethostbyname_ex(service)[2]
    # print(serv_ip)
    return serv_ip
if __name__ == '__main__':
    services = ['drive.google.com', 'mail.google.com', 'google.com']
    list_ip = get_one_ip()
    list_ips = get_all_ip()
    print(list_ip)
    print(list_ips)
    test
