import socket
import time


def get_one_ip():
    serv_ip = {}
    for service in services:
        serv_ip[service] = socket.gethostbyname(service)
    return serv_ip


def get_all_ip():
    serv_ip = {}
    for service in services:
        serv_ip[service] = socket.gethostbyname_ex(service)[2]
    return serv_ip


def print_log(l_ip):
    for service, ip in l_ip.items():
        ip_new = socket.gethostbyname(service)
        if ip != ip_new:
            print(f'[ERROR] {service} IP mismatch: {ip} {ip_new}')
            l_ip[service] = ip_new
            # print(list_ip)
        print(f'{service} - {ip_new}')
    time.sleep(1)


if __name__ == '__main__':
    services = ['drive.google.com', 'mail.google.com', 'google.com']
    # list_ips = get_all_ip()
    # print(list_ips)
    list_ip = get_one_ip()
    while True:
        print_log(list_ip)
