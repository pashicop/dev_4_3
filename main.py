import json
import socket
import time
from datetime import datetime
import subprocess, platform
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


def save_ip(list_ip: list):
    with open("output/1.json", "w") as js:
        json.dump(list_ip, js)
        json.dump(str(datetime.now()), js)
    with open("output/1.yaml", "w") as ym:
        yaml.dump(list_ip, ym, indent=2, explicit_start=True, explicit_end=True)
        yaml.dump(str(datetime.now()), ym, explicit_start=True, explicit_end=True)
    return


def print_log(l_ip):
    for dict_s in l_ip:
        for service, ip in dict_s.items():
            ip_new = socket.gethostbyname(service)
            if ip != ip_new:
                with open("output/error", "a") as file_err:
                    err_string = str(datetime.now()) + " [ERROR] " + service + " IP mismatch: " + ip + " " + ip_new + "\n"
                    file_err.write(err_string)
                print(f'[ERROR] {service} IP mismatch: {ip} {ip_new}')
                dict_s[service] = ip_new
                save_ip(l_ip)
            print(f'{service} - {ip_new}')
        time.sleep(1)
    print(datetime.now())


def pingOk(sHost):
    try:
        output = subprocess.check_output("ping -{} 1 {}".format('n' if platform.system().lower()=="windows" else 'c', sHost), shell=True)
    except Exception as e:
        return False
    return True

def check_ip(l_ip):
    dict = {}
    for ip in l_ip:
        if pingOk(ip):
            dict[ip] = "OK"
            print(f'{ip} - {dict[ip]}')
        else:
            dict[ip] = "ALARM!"
            print(f'{ip} - {dict[ip]}')
    with open("output/ip.yaml", "w+") as f:
        yaml.dump(dict, f, indent=2, explicit_start=True, explicit_end=True)
        yaml.dump(str(datetime.now()), f, explicit_start=True, explicit_end=True)
    return

if __name__ == '__main__':
    with open("input/services") as serv_files:
        services = serv_files.read().splitlines()
    with open("input/ip") as ip_file:
        list_ip2 = ip_file.read().splitlines()
    list_ip = get_one_ip()
    save_ip(list_ip)
    while True:
        print_log(list_ip)
        check_ip(list_ip2)
