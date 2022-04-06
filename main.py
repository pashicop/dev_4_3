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
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user=cred["user"],
            password=cred["password"],
            database=cred["database"]
        )
        # print(connection)
        print(f'БД {cred["database"]} подключена!')
    except mysql.connector.Error as err:
        print(err)
    # time.sleep(120)
    if connection:
        return connection
    else:
        print("Нет соединения с БД")


def close_db(con_db):
    # time.sleep(20)
    con_db.close()
    print("БД отключена")


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


def save_init_ip(serv_ip: list, con_db):
    with open("output/1.json", "w") as js:
        list_out = serv_ip.copy()
        list_out.insert(0, {"date": str(datetime.now())})
        json.dump(list_out, js)
        # json.dump(str(datetime.now()), js)
    with open("output/1.yaml", "w") as ym:
        yaml.dump(list_out, ym, indent=2, explicit_start=True, explicit_end=True)
        # yaml.dump(str(datetime.now()), ym, explicit_start=True, explicit_end=True)
    try:
        print_result(con_db)
        for service in serv_ip:
            for service_name, service_ip in service.items():
                with con_db.cursor() as c_select_dns_id:
                    db_query_select_dns_id = "SELECT id FROM dns WHERE dns = '" + service_name + "'"
                    c_select_dns_id.execute(db_query_select_dns_id)
                    result_select_dns = c_select_dns_id.fetchone()
                    if result_select_dns is None:
                        # print("Не нашёл в базе dns")
                        add_dns(service_name, con_db)
                        c_select_dns_id.execute(db_query_select_dns_id)
                        result_select_dns = c_select_dns_id.fetchone()
                    dns_id = "'" + str(result_select_dns[0]) + "'"
                    # print(dns_id)
                with con_db.cursor() as c_select_ip_id:
                    db_query_select_ip_id = "SELECT id FROM ip WHERE ip = '" + service_ip + "'"
                    c_select_ip_id.execute(db_query_select_ip_id)
                    result_select_ip = c_select_ip_id.fetchone()
                    if result_select_ip is None:
                        # print("Не нашёл в базе ip")
                        add_ip(service_ip, con_db)
                        c_select_ip_id.execute(db_query_select_ip_id)
                        result_select_ip = c_select_ip_id.fetchone()
                    ip_id = "'" + str(result_select_ip[0]) + "'"
                    # print(ip_id)
                with con_db.cursor() as c_select_track:
                    db_query_select_track = "SELECT ipt.id FROM ip_track ipt LEFT JOIN dns ON ipt.dns_id = dns.id " \
                                            "WHERE dns = '" + service_name + "'"
                    # print(db_query_select_track)
                    c_select_track.execute(db_query_select_track)
                    result_select_id_ip_track = c_select_track.fetchone()
                    if result_select_id_ip_track:
                        track_id = "'" + str(result_select_id_ip_track[0]) + "'"
                        # print(track_id)
                        with con_db.cursor() as c_update_track:
                            db_query_update_track = "UPDATE ip_track SET cur_ip_id = " + ip_id + ", old_ip_id = " \
                                                    + ip_id + " WHERE ( id = " + track_id + ")"
                            # print(db_query_update_track)
                            c_update_track.execute(db_query_update_track)
                            con_db.commit()
                            # print(f'Обновил {track_id} {dns_id} {ip_id} {ip_id}')
                    else:
                        # print("Нет в Списке!")
                        # print("Добавляю!")
                        with con_db.cursor() as c_insert_new_track:
                            db_query_insert_new_track = "INSERT INTO ip_track (dns_id, cur_ip_id, old_ip_id) VALUES (" \
                                                        + dns_id + ", " + ip_id + ", " + ip_id + ")"
                            # print(db_query_insert_new_track)
                            c_insert_new_track.execute(db_query_insert_new_track)
                            con_db.commit()
                            # print(f'Добавил {dns_id} {ip_id} {ip_id}')
                # print()
    except mysql.connector.Error as err:
        print(err)
    # time.sleep(100)
    return


def add_ip(ip, con_db):
    try:
        db_query_insert = "INSERT INTO ip(ip) VALUES ('" + ip + "')"
        # print(db_query_insert)
        with con_db.cursor() as c_insert:
            c_insert.execute(db_query_insert)
            con_db.commit()
    except mysql.connector.Error as err:
        print(err)


def add_dns(name, con_db):
    try:
        db_query_insert = "INSERT INTO dns(dns) VALUES ('" + name + "')"
        # print(db_query_insert)
        with con_db.cursor() as c_insert:
            c_insert.execute(db_query_insert)
            con_db.commit()
    except mysql.connector.Error as err:
        print(err)


def print_log(l_ip, con_db):
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
                save_change_ip(service, ip_new, con_db)
            print(f'{service} - {ip_new}')
        time.sleep(1)
    print(datetime.now())


def save_change_ip(serv, ip, con_db):
    with con_db.cursor() as c_select:
        db_query_select = "SELECT ipt.id, ipt.cur_ip_id FROM ip_track ipt LEFT JOIN dns ON ipt.dns_id = dns.id " \
                          "WHERE dns = '" + serv + "'"
        # print(db_query_select)
        c_select.execute(db_query_select)
        result = c_select.fetchone()
        # print(result)
    with con_db.cursor() as c_select_id_from_ip:
        db_query_select_id_from_ip = "SELECT id FROM ip WHERE ip = '" + ip + "'"
        # print(db_query_select_id_from_ip)
        c_select_id_from_ip.execute(db_query_select_id_from_ip)
        result_ip_from_id = c_select_id_from_ip.fetchone()
        if result_ip_from_id is None:
            add_ip(ip, con_db)
            c_select_id_from_ip.execute(db_query_select_id_from_ip)
            result_ip_from_id = c_select_id_from_ip.fetchone()
            # print(result_ip_from_id)
        ip_id = result_ip_from_id[0]
        # print(ip_id)
    with con_db.cursor() as c_update:
        db_query_update = "UPDATE ip_track SET cur_ip_id = '" + str(ip_id) + "', old_ip_id = '" + str(
            result[1]) + "' WHERE ( id = '" + str(result[0]) + "')"
        # print(db_query_update)
        c_update.execute(db_query_update)
        con_db.commit()


def ping_ok(s_host):
    try:
        subprocess.check_output(
            "ping -{} 1 {}".format('n' if platform.system().lower() == "windows" else 'c', s_host), shell=True)
    except Exception as err:
        print(err)
        return False
    return True


def check_ip(l_ip, file, con_db):
    ip_status = {}
    dict_out = {}
    for ip in l_ip:
        if ping_ok(ip):
            ip_status[ip] = "OK"
            print(f'{ip} - {ip_status[ip]}')
        else:
            ip_status[ip] = "ALARM!"
            print(f'{ip} - {ip_status[ip]}')
        write_to_db(ip, ip_status[ip], con_db)
    dict_out["date"] = str(datetime.now())
    dict_out.update(ip_status)
    write_to_file(dict_out, file)
    return


def write_to_db(change_ip, status, con_db):
    with con_db.cursor() as c_update:
        db_query_update = "UPDATE ip SET status = '" + status + "', date = NOW() WHERE ( ip = '" + change_ip + "')"
        c_update.execute(db_query_update)
        print(db_query_update)
        con_db.commit()


def write_to_file(dict_in, file_out):
    with open(file_out, "w+") as f:
        yaml.dump(dict_in, f, indent=2, explicit_start=True, explicit_end=True)
    print()


def add_ip_row(list_ip, con_db):
    try:
        known_ip = []
        db_query_select = "SELECT * FROM ip"
        with con_db.cursor() as c_select:
            # print(db_query_select)
            c_select.execute(db_query_select)
            result = c_select.fetchall()
            for row in result:
                known_ip.append(row[1])
        for ip in list_ip:
            if ip not in known_ip:
                db_query_insert = "INSERT INTO ip(ip) VALUES ('" + ip + "')"
                # print(db_query_insert)
                with con_db.cursor() as c_insert:
                    c_insert.execute(db_query_insert)
                    con_db.commit()
    except mysql.connector.Error as err:
        print(err)


def add_dns_row(in_services, con_db):
    try:
        known_dns = []
        db_query_select = "SELECT * FROM dns"
        with con_db.cursor() as c_select:
            # print(db_query_select)
            c_select.execute(db_query_select)
            result = c_select.fetchall()
            for row in result:
                known_dns.append(row[1])
        for dns in in_services:
            if dns not in known_dns:
                db_query_insert = "INSERT INTO dns(dns) VALUES ('" + dns + "')"
                # print(db_query_insert)
                with con_db.cursor() as c_insert:
                    c_insert.execute(db_query_insert)
                    con_db.commit()
    except mysql.connector.Error as err:
        print(err)


def get_ip(con_db):
    with con_db.cursor() as c_select:
        db_query_select = "SELECT ip from ip"
        c_select.execute(db_query_select)
        result = c_select.fetchall()
        if result:
            list_ip_from_db = []
            for row in result:
                list_ip_from_db.append(row[0])
            return list_ip_from_db


def print_result(con_db):
    db_query_select = """
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
    with con_db.cursor() as c_select:
        c_select.execute(db_query_select)
        result_select = c_select.fetchall()
        for row in result_select:
            print(row)


if __name__ == '__main__':
    with open("input/services") as serv_files:
        services = serv_files.read().splitlines()
    with open("input/ip") as ip_file:
        list_input_ip = ip_file.read().splitlines()
    list_serv_ip = get_one_ip(services)
    conn = connect_db()
    if conn:
        # add_dns("abc.ru", conn)
        # add_ip("5.5.5.5", conn)
        add_ip_row(list_input_ip, conn)
        add_dns_row(services, conn)
        save_init_ip(list_serv_ip, conn)
        while True:
            try:
                ip_from_db = get_ip(conn)
                print_log(list_serv_ip, conn)
                check_ip(list_input_ip, "output/ip.yaml", conn)
                check_ip(ip_from_db, "output/ip_from_db.yaml", conn)
                print_result(conn)
            except Exception as e:
                print(e)
                close_db(conn)
                break
