import socket

def main(dest_addr):
    
    port = 33434
    max_hops = 30
    #to receive data(ICMP) raw socket
    icmp = socket.getprotobyname('icmp')
    #send udp
    udp = socket.getprotobyname('udp')
    #increment ttl(counter), start from 1 to track routers
    ttl = 1
    
    while True:
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
        #set the incremented ttl value
        send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        #make recv_socket listen to connections from default port 33434
        recv_socket.bind(("", port))
        #make send_socket to send empty string to the destination via same port
        send_socket.sendto("", (dest_addr, port))
        
        curr_addr = None
        curr_name = None
        #try exception to avoid time out error if admins disable receving ICMP ECHO request
        try:
            #to eliminate the ip from the tuple of ip and port
            _, curr_addr = recv_socket.recvfrom(512)
            curr_addr = curr_addr[0]

        except socket.error:
            pass
        finally:
            send_socket.close()
            recv_socket.close()
            
        #printing ttl(router number) host name and ip address
        if curr_addr is not None:
            curr_host = "%s" % (curr_addr)
        else:
            curr_host = "*"
        print "%d\t%s" % (ttl, curr_host)

        ttl += 1

        #terminate the loop either get to the destination or exeeded max num of hops
        if curr_addr == dest_addr or ttl > max_hops:
            break

if __name__ == "__main__":
    main(raw_input("Enter destination ip adress to track routers : "))
