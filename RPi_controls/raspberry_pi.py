"""
:Name: raspberry_pi 
:Description: pilab module running on the raspberry pi
:Date: 2023-03-28
:Version: 0.0.1
:Author(s): Hilario Greggi

"""

import socket
import json
import platform
import os
import struct
from getmac import get_mac_address
import time 
import traceback

# Platform infos
if platform.system() == "Linux":
    from picamera2 import Picamera2 


class ControlledDevice: 
    """_summary_

    Returns:
        _type_: _description_
    """
################################################################################################################
# INITIALIZATION ###############################################################################################
################################################################################################################

    def __init__(self, mcast_grp:str = '224.1.1.1', mcast_port:int = 9998, tcp_port:int = 47822):
        """_summary_

        Args:
            mcast_grp (str, optional): _description_. Defaults to '224.1.1.1'.
            mcast_port (int, optional): _description_. Defaults to 9998.
            tcp_port (int, optional): _description_. Defaults to 47822.
        """
        self.mcast_grp = mcast_grp
        self.mcast_port = mcast_port
        self.tcp_port = tcp_port

        self.hostname = socket.gethostname()
        self.mac_addr = get_mac_address()
        if platform.system() != "Linux":
            self.ip_addr = socket.gethostbyname(self.hostname)
        else:
            self.ip_addr = self.get_wlan_ip()

        self.current_directory = os.getcwd() 

    # def __enter__(self):
    #     return self
    
    # def __exit__(self, exc_type, exc_value, traceback):
    #     del self

################################################################################################################
# ControlComputer CLASS METHODS ################################################################################
################################################################################################################

    def get_wlan_ip(self):
        """_summary_

        Returns:
            _type_: _description_
        """        
        routes = json.loads(os.popen("ip -j -4 route").read())
        for r in routes:
            if r.get("dev") == "wlan0" and r.get("prefsrc"):
                wlan_ipaddr = r['prefsrc']
                continue
        return wlan_ipaddr
    
    def tcp_protocol_send(self, server_ip:str, response:str):   
        """_summary_

        Args:
            server_ip (_type_): _description_
            response (_type_): _description_
        """
        server_address = (server_ip, self.tcp_port)
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try: 
                    s.connect(server_address)
                except ConnectionRefusedError:
                    print("Connection refused, retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                s.sendall(bytes(response, 'utf-8'))
            break 

    def create_json(self, type_of_info:str, content:str): # must modify so it's not callable as a method
        """_summary_

        Args:
            type_of_info (_type_): _description_
            content (_type_): _description_

        Returns:
            _type_: _description_
        """        
        _dict = {"type_of_info":type_of_info ,"content":content}
        return json.dumps(_dict, indent=2)
    
# A RANGER #####################################################################################################

    if platform.system() == "Linux":

        def capture_picture(self, delay, number_of_images): 
            # using a high level API to take pictures
            picam2 = Picamera2()
            # picam2.sensor_mode = 2
            picam2.start_and_capture_files(f"{self.hostname}"+"_img{:03d}.jpg", initial_delay = 1, delay = delay, num_files = number_of_images, show_preview = False)
            return True
        
        def capture_2(self, delay, number_of_images):
            camera = Picamera2()
            camera.resolution = (640, 480)
            camera.framerate = 30
            seconds_between_pictures = delay
            number_of_pictures = number_of_images
            for i in range(number_of_pictures):
                camera.capture(f"{self.hostname}"+"_img{:03d}.jpg")
                time.sleep(seconds_between_pictures)
            camera.close()
            return True

        def capture_3(self, delay, num_images):
            picam2 = Picamera2()
            print('check1')
            still_config = picam2.create_still_configuration()
            print('check2')
            preview_config = picam2.create_preview_configuration()
            print('check3')
            picam2.configure(preview_config)
            print('check4')
            picam2.start()
            print('check5')
            for i in range(num_images):
                print('check6')
                job = picam2.switch_mode_and_capture_file(still_config, f"{self.hostname}"+f"_img{i:03d}.jpg", wait=False)
                print('check7')
                time.sleep(delay)
                print('check8')
                metadata = picam2.wait(job)
                print('check9')
            return True 

################################################################################################################
# RASPBERRY PI LISTEN AND SEND RESPONSES #######################################################################
################################################################################################################

    def stand_by_for_request(self, timeout:int = 30):
        """_summary_
        """    

        MCAST_GRP = '224.1.1.1' 
        MCAST_PORT = 9998
        
        # create socket to listen for requests on the '224.1.1.1' multicast group
        sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        sock_udp.bind(('', MCAST_PORT))
        mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
        sock_udp.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        # receive/respond loop 
        sock_udp.settimeout(timeout)
        print('standing by...')

        try:
            while True:
                print("check 1")
                data, addr = sock_udp.recvfrom(1024)
                
                # parsing the data 
                parsed_data = json.loads(data)
                # print(f"received data: {json.dumps(parsed_data, indent=2)}")
                command = parsed_data['command']
                arguments = parsed_data['arguments']

                if command == "ping":
                    print("[START] ping command")
                    os_name = os.name
                    plateform_system = platform.system()
                    checks = [os_name == arguments["os_name"], plateform_system == arguments["plateform"]]
                    # print(all(checks))
                    if all(checks):
                        sock_udp.sendto(b"pong", addr)
                        print('response sent')

                if command == "id":
                    print("[START] id command")
                    self.controler_ip = arguments["id_address"]
                    type_of_info = "pi_id"
                    content = {"hostname":self.hostname, "ip_addr":self.ip_addr, "mac_addr":self.mac_addr}
                    response = self.create_json(type_of_info, content)
                    self.computer_ipaddr = arguments["id_address"]
                    self.tcp_protocol_send(self.computer_ipaddr, response) 
                    print('response sent') 

                if command == "capture":
                    print("[START] capture command") 
                    delay = float(arguments["delay"])
                    number_of_images = int(arguments["number_of_images"])
                    confirmation = self.capture_3(delay, number_of_images)
                    if confirmation:
                        type_of_info = "confirmation"
                        content = {"dir":self.current_directory}
                        response = self.create_json(type_of_info, content)
                        self.tcp_protocol_send(self.computer_ipaddr, response)
                        print('response sent')

                if command == "shutdown":
                    os.system(arguments["message"])

        except Exception: 
            traceback.print_exc()
            sock_udp.close()

################################################################################################################
# RUN SCRIPT ###################################################################################################
################################################################################################################
   
if __name__ == "__main__" :
    RPi = ControlledDevice()
    RPi.stand_by_for_request()


