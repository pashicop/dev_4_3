import json
import platform
import socket
import subprocess
import time
from datetime import datetime

import mysql.connector
import yaml

# from getpass import getpass
create_db = """
    CREATE TABLE ip(
        id INT AUTO_INCREMENT PRIMARY KEY,
        ip VARCHAR(100)
    );
    CREATE TABLE dns(
        id INT AUTO_INCREMENT PRIMARY KEY,
        dns VARCHAR(100)
    );
    CREATE TABLE dns(
        id INT AUTO_INCREMENT PRIMARY KEY,
        dns_id INT,
        cur_ip_id INT,
        old_ip_id INT,
        FOREIGN KEY (dns_id) REFERENCES dns(id),
        FOREIGN KEY (cur_ip_id) REFERENCES ip(id),
        FOREIGN KEY (old_ip_id) REFERENCES ip(id)
    )    
    INSERT INTO ip(ip)
        VALUES
            ("8.8.8.8"),
            ("195.19.97.117")
    INSERT INTO dns(dns)
        VALUES
            ("bioreformed.ru"),
            ("google.com")
    INSERT INTO ip_track(dns_id, cur_ip_id, old_ip_id)
        VALUES
            (NULL, 1, 1),
            (1, 2, 2)
"""


def connect_db():
    connection = None
    with open("credentials.json", encoding="UTF-8") as f:
        cred = json.load(f)
    test_db = "test"
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user=cred["user"],
            password=cred["password"],
            database="test"
        )
        print(connection)
        print(f'Database {test_db} Connected!')
    except mysql.connector.Error as e:
        print(e)
    # time.sleep(120)
    if connection:
        return connection
    else:
        print("Нет соединения с БД")


def close_db(con_db):
    # time.sleep(20)
    con_db.close()
    print("Database connection closed")


def get_one_ip(in_services):
    l_serv_ip = []
    for service in in_services:
        serv_ip = {service: socket.gethostbyname(service)}
        l_serv_ip.append(serv_ip)
    # print(list_services)
    return l_serv_ip


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
    with open("credentials.json", encoding="UTF-8") as f:
        dict = json.load(f)
    try:
        with mysql.connector.connect(
                host="localhost",
                user=dict["user"],
                password=dict["password"],
                database="test"
        ) as connection:
            print(connection)
            known_dns = []
            db_query = """
                SELECT 
                    ipt.id, 
                    dns.dns,
                    ipt.cur_ip_id, 
                    ip1.ip AS current_ip, 
                    ipt.old_ip_id, 
                    ip2.ip AS old_ip 
                FROM ip_track ipt 
                LEFT JOIN dns
                    ON dns.id = ipt.dns_id
                LEFT JOIN ip ip1
                    ON ip1.id = ipt.cur_ip_id 
                LEFT JOIN ip ip2
                    ON ip2.id = ipt.old_ip_id
                """
            with connection.cursor() as cursor:
                cursor.execute(db_query)
                result = cursor.fetchall()
                for row in result:
                    print(row)
                    if row[1]:
                        known_dns.append(row[1])
            for service in list_ip:
                for service_name, service_ip in service.items():
                    if service_name in known_dns:
                        db_query_select_id_from_dns = "SELECT id FROM test.dns WHERE dns = '" + service_name + "'"
                        print(db_query_select_id_from_dns)
                        with connection.cursor() as cursor2:
                            cursor2.execute(db_query_select_id_from_dns)
                            id_from_dns = int(cursor2.fetchone()[0])
                            print(id_from_dns)
                    with connection.cursor() as cursor3:
                        db_query_select_ip_id_from_ip = "SELECT id FROM test.ip WHERE ip = '" + service_ip + "'"
                        print(db_query_select_ip_id_from_ip)
                        cursor3.execute(db_query_select_ip_id_from_ip)
                        result3 = cursor3.fetchone()
                        if result3:
                            id_ip_from_ip = int(result3[0])
                        else:
                            id_ip_from_ip = 0
                    if id_ip_from_ip == 0:
                        with connection.cursor() as cursor4:
                            db_query_insert = "INSERT INTO ip(ip) VALUES ('" + service_ip + "')"
                            print(db_query_insert)
                            cursor4.execute(db_query_insert)
                            connection.commit()
                            db_query_ips = "SELECT id FROM ip WHERE ip = '" + service_ip + "'"
                            print(db_query_ips)
                            cursor4.execute(db_query_ips)
                            id_ip_from_ip = int(cursor4.fetchone()[0])
                    print(id_ip_from_ip)
                    # id_ip_from_ip = "NULL"
                    print()

                    print()
                    # with connection.cursor() as cursor4:

                    # known_ip.append(row[1])
                # if ip not in known_ip:
                #     cursor.execute(db_query)
                #     connection.commit()
            # for serv_ip_dict in list_ip:
            #     for serv, ip in serv_ip_dict.items():
            #         db_query = "INSERT INTO ip_track(dns_id, cur_ip_id, old_ip_id) VALUES ('" + serv_id + "', '" + cur_ip_id + "'" + old_ip_id + "')"
            #         db_query2 = "SELECT * FROM ip"
            # for ip in list_ip2:
            #     known_ip = []
            #     db_query = "INSERT INTO ip(ip) VALUES ('" + ip + "')"
            #     db_query2 = "SELECT * FROM ip"
            #     print(db_query)
            #     print(db_query2)
            #
    except mysql.connector.Error as e:
        print(e)
    # time.sleep(100)
    return


def print_log(l_ip):
    for dict_s in l_ip:
        for service, ip in dict_s.items():
            ip_new = socket.gethostbyname(service)
            if ip != ip_new:
                with open("output/error", "a") as file_err:
                    err_string = str(
                        datetime.now()) + " [ERROR] " + service + " IP mismatch: " + ip + " " + ip_new + "\n"
                    file_err.write(err_string)
                print(f'[ERROR] {service} IP mismatch: {ip} {ip_new}')
                dict_s[service] = ip_new
                save_ip(l_ip)
            print(f'{service} - {ip_new}')
        time.sleep(1)
    print(datetime.now())


def ping_ok(sHost):
    try:
        output = subprocess.check_output(
            "ping -{} 1 {}".format('n' if platform.system().lower() == "windows" else 'c', sHost), shell=True)
    except Exception as e:
        print(e)
        return False
    return True


def check_ip(l_ip):
    dict = {}
    for ip in l_ip:
        if ping_ok(ip):
            dict[ip] = "OK"
            print(f'{ip} - {dict[ip]}')
        else:
            dict[ip] = "ALARM!"
            print(f'{ip} - {dict[ip]}')
    with open("output/ip.yaml", "w+") as f:
        yaml.dump(dict, f, indent=2, explicit_start=True, explicit_end=True)
        yaml.dump(str(datetime.now()), f, explicit_start=True, explicit_end=True)
    return


def add_ip_row(list_ip2, con_db):
    try:
        known_ip = []
        db_query_select = "SELECT * FROM ip"
        with con_db.cursor() as c_select:
            print(db_query_select)
            c_select.execute(db_query_select)
            result = c_select.fetchall()
            for row in result:
                known_ip.append(row[1])
        for ip in list_ip2:
            if ip not in known_ip:
                db_query_insert = "INSERT INTO ip(ip) VALUES ('" + ip + "')"
                print(db_query_insert)
                with con_db.cursor() as c_insert:
                    c_insert.execute(db_query_insert)
                    con_db.commit()
    except mysql.connector.Error as e:
        print(e)


def add_dns_row(in_services, con_db):
    try:
        known_dns = []
        db_query_select = "SELECT * FROM dns"
        with con_db.cursor() as c_select:
            print(db_query_select)
            c_select.execute(db_query_select)
            result = c_select.fetchall()
            for row in result:
                known_dns.append(row[1])
        for dns in in_services:
            if dns not in known_dns:
                db_query_insert = "INSERT INTO dns(dns) VALUES ('" + dns + "')"
                print(db_query_insert)
                with con_db.cursor() as c_insert:
                    c_insert.execute(db_query_insert)
                    con_db.commit()
    except mysql.connector.Error as e:
        print(e)


if __name__ == '__main__':
    with open("input/services") as serv_files:
        services = serv_files.read().splitlines()
    with open("input/ip") as ip_file:
        list_input_ip = ip_file.read().splitlines()
    list_serv_ip = get_one_ip(services)
    conn = connect_db()
    if conn:
        add_ip_row(list_input_ip, conn)
        add_dns_row(services, conn)
        save_ip(list_serv_ip)
        # while True:
        #     print_log(list_ip)
        #     check_ip(list_ip2)
        close_db(conn)
