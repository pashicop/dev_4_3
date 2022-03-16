import socket

if __name__ == '__main__':
    services = ['drive.google.com', 'mail.google.com', 'google.com']
    serv_ip = {}
    # print(type(socket.gethostbyname_ex('mail.google.com')))

    # print(ips)
    for service in services:
        serv_ip[service] = socket.gethostbyname_ex('mail.google.com')[2]
    print(serv_ip)