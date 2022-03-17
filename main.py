import json
import socket
import time
import yaml


def get_one_ip():
    list_services = []
    for service in services:
        serv_ip = {}
        serv_ip[service] = socket.gethostbyname(service)
        list_services.append(serv_ip)
    # print(list_services)
    return list_services


def get_all_ip():
    serv_ip = {}
    for service in services:
        serv_ip[service] = socket.gethostbyname_ex(service)[2]
    return serv_ip


def save_ip(list_ip):
    with open("1.json", "w") as js:
        json.dump(list_ip, js)
    with open("1.yaml", "w") as ym:
        yaml.dump(list_ip, ym, indent=2, explicit_start=True, explicit_end=True)
    return


def print_log(l_ip):
    for dict_s in l_ip:
        for service, ip in dict_s.items():
            ip_new = socket.gethostbyname(service)
            if ip != ip_new:
                print(f'[ERROR] {service} IP mismatch: {ip} {ip_new}')
                dict_s[service] = ip_new
                save_ip(l_ip)
                # print(list_ip)
            print(f'{service} - {ip_new}')
        time.sleep(1)


if __name__ == '__main__':
    services = ['drive.google.com', 'mail.google.com', 'google.com']
    # list_ips = get_all_ip()
    # print(list_ips)
    list_ip = get_one_ip()
    save_ip(list_ip)
    while True:
        print_log(list_ip)
