import network
import socket
import time
import machine

#kod pre klienta - server vytvara aj WIFI AP
SERVER_IP = "192.168.4.1"   #IP adresa druhej strany, teda servera
SERVER_PORT : int = 65000    #zistit od servera
nic : network.WLAN = network.WLAN(network.STA_IF)
s : socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

nic.active(False)
time.sleep_ms(500)
nic.active(True)
#pripojenie sa na existujucu wifi siet ktoru vytvara server
nic.connect("ESP_MATUS_test", "heslo1234")    #SSID a heslo wifi siete

#test či sa pripojime
while True:
    status : list[int] = nic.status()
    if status == network.STAT_GOT_IP:
        print(f"The ESP32 has been connected to wifi network ")#ak ESP dostalo uspesne IP adresu
        print(f"network configuration is {nic.ifconfig()}")   #vypis
        break  #vystupim z while slučky
    elif status == network.STAT_WRONG_PASSWORD: # ak siet existuje ale zadal som zle heslo
        print(f"The Wifi password is wrond")
        machine.soft_reset() #reset ESP
    elif status == network.STAT_NO_AP_FOUND: #wifi s takym heslom neexistuje!
        print(f"The Wifi name is wrong")
        machine.soft_reset()
    elif status == network.STAT_CONNECT_FAIL: # nie som v dosahu napr
        print(f"Connection to WiFi failed")
        machine.soft_reset()

    #vypisem status
    print(f"Current WiFi status: {nic.status()}")
    time.sleep(1)


s.connect((SERVER_IP, SERVER_PORT))
print("Pripojený k serveru")

while True:
    user_msg = input("Zadaj spravu pre server: ")
    s.sendall(user_msg.encode("UTF-8"))
    time.sleep_ms(500)

    data = s.recv(1024)
    if not data:
        print("Server ukončil spojenie")
        s.close()
        break

    message = data.decode("UTF-8").strip()
    print("Server:", message)

    if message.lower() == "koniec":
        print("Pokyn na ukončenie spojenia")
        s.close()
        break


