"""
:Name: control_computer
:Description: pilab module running on the control computer
:Date: 2023-03-28
:Version: 0.0.1
:Author(s): Hilario Greggi

"""

import socket
import struct
import json
import subprocess
import platform
import time 
from pathlib import Path
import traceback


class ControlComputer: 
    """This class contains all the commands available to control the pis. 

    Returns:
        _type_: _description_
    """
################################################################################################################
# INITIALIZATION ###############################################################################################
################################################################################################################

    def __init__(self, setup_id:tuple, mcast_grp:str = '224.1.1.1', mcast_port:int = 9998, tcp_port:int = 47822):
        """
        
        This method initializes an object with the given setup_id, mcast_grp, mcast_port, and tcp_port attributes. 

        It also initializes other attributes such as hostname, ipaddr, rpis_ids, and number_of_rpis. 
        It creates a UDP socket object using the socket() method of the socket module and sets its options using the setsockopt() method. 
        It also creates a TCP socket object using the same method and binds it to the IP address and TCP port specified in the object's attributes.

        Args:
            setup_id (_type_): name of the group of pis. e.g triaxial_1
            mcast_grp (str, optional): multicast group used to send data to all hosts that are member of that group. Defaults to '224.1.1.1'.
            mcast_port (int, optional): port number that the socket will use to send data to the multicast group. Defaults to 9998.
            tcp_port (int, optional): port number that the socket will use to send data via tcp/ip protocol. Defaults to 47822.
        """
        # arguments
        self.setup_id = setup_id
        self.mcast_grp = mcast_grp
        self.mcast_port = mcast_port
        self.tcp_port = tcp_port

        # created attributs
        self.hostname = socket.gethostname()
        self.ipaddr = socket.gethostbyname(self.hostname)
        self.rpis_ids = {}
        self.number_of_rpis = 0
        
        # sockets 
        ## UDP socket
        self.sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.ttl = struct.pack('b', 1)
        self.sock_udp.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.ttl)

    def __enter__(self):
        """
        This method is a context manager that returns the object itself when entering a 
        with block using the __enter__() method.

        Returns:
            class: see ControlComputer
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        This method is a context manager that closes the UDP socket object using the close_socket() 
        method when exiting a with block using the __exit__() method.
        """
        self.close_udp_socket()


################################################################################################################
# ControlComputer CLASS METHODS ################################################################################
################################################################################################################

    def close_udp_socket(self):
        """
        This method closes the UDP socket object using the close() method.
        """
        self.sock_udp.close()

    def create_json(self, command:str, arguments:str):
        """
        
        This method creates a JSON object with a command and its arguments. 
        
        It takes two arguments: command and arguments. It creates a dictionary with the command and its arguments, 
        then returns the dictionary as a JSON string with indentation of 2 spaces.

        Args:
            command (str): command sent to the raspberry pis
            arguments (dict): contains the arguments of the command

        Returns:
            str: dictionary as a JSON string with indentation of 2 spaces
        """
        _dict = {"command":command ,"arguments":arguments}
        return json.dumps(_dict, indent=2)
    
    def chek_the_ip(self, ip_addr:str):
        """
        
        This method checks if an IP address is in self.rpis_ids. 
        
        It takes two arguments: list_of_dictionaries and ip_addr. It iterates through each dictionary in the list_of_dictionaries
        (self.rpis_ids) and checks if the value of the 'ip_addr' key matches the ip_addr argument. If it finds a match, it returns True.

        Args:
            list_of_dictionnaries (list): in this code, this list is the list of dictionnaries for the pis 
            ip_addr (str): IP address of the tested device 

        Returns:
            bool: True if the tested device was recongnized before
        """
        for key, value in self.rpis_ids.items():
            if value['ip_addr'] == ip_addr:
                return True 
            
    def get_name_of_machine(self, my_dict:dict, ip_addr:str):
        """
        
        This method takes two arguments: my_dict and ip_addr. 
        
        It iterates through each key-value pair in the dictionary and checks if the value of the 'ip_addr' key matches 
        the ip_addr argument. If it finds a match, it returns the key.

        Args:
            my_dict (dict): dictionary that contains information about the tested raspberry pi
            ip_addr (str): IP address of the raspberry pi

        Returns:
            str: the name of a machine given its IP address
        """
        for key, value in my_dict.items():
            if value['ip_addr'] == ip_addr:
                return key 

################################################################################################################
# RASPBERRY PI COMMANDS ########################################################################################
################################################################################################################

    def ping(self, timeout:float = 5): 
        """
        
        Sends a ping request to the pis connected on the wlan. 
        
        The method takes an optional argument timeout which specifies the number of seconds to wait for a response before timing out. 
        The method then waits for a response from the devices and prints the number of responses received.

        Args:
            timeout (int, optional): number of seconds to wait for a response before timing out. Defaults to 5.
        """   

        # request   
        command = "ping"
        arguments = {"os_name":self.setup_id[0], "plateform":self.setup_id[1]}
        request = self.create_json(command, arguments)
        
        # sending data and waiting
        self.sock_udp.sendto(bytes(request, encoding="utf-8"), (self.mcast_grp, self.mcast_port))
        self.sock_udp.settimeout(timeout)
        
        while True:
            try: 
                data, addr = self.sock_udp.recvfrom(1024)
                if data: 
                    # print("received message: %s" % data)
                    self.number_of_rpis += 1
            
            except socket.timeout:
                break
        
        print(f"{self.number_of_rpis} raspberry pi(s) found on the wlan") 
                
    def get_raspberrypis_identification(self, timeout:float = 15):
        """
        
        This method is used to get the identification of the Raspberry Pis. 
        
        It sends a request via UDP to the Raspberry Pis. This request carries the IP address of the ControlComputer so the pis can respond via TCP.  
        Then it turns on server mode TCP and waits for a connection from the Raspberry Piq. When a connection is established, it receives data from 
        the Raspberry Pi and updates the dictionary of Raspberry Pi IDs with the name of the Raspberry Pi and its IP and MAC addresses. 
        It repeats this process until it has found all of the Raspberry Pis specified in the arguments. The number of expected Raspberry Pis is 
        updated after the ping method is run. Finally, it prints a message indicating that all of the Raspberry Pis were found.

        Args:
            timeout (int, optional): number of seconds to wait for a response before timing out. Defaults to 15.
        """
        # request 
        command = "id"
        arguments = {"id_address":self.ipaddr}
        request = self.create_json(command, arguments)

        # sending data via and waiting for tcp response 
        self.sock_udp.sendto(bytes(request, encoding="utf-8"), (self.mcast_grp, self.mcast_port))

        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_tcp.bind((self.ipaddr, self.tcp_port))
        sock_tcp.listen()
        sock_tcp.settimeout(timeout)

        number_of_found_rpi = 0
        try:
            while number_of_found_rpi != self.number_of_rpis:        
                # event loop waiting for connection 
                while True:
                    conn, addr = sock_tcp.accept()
                    if conn: 
                        data = conn.recv(1024)
                        parsed_data = json.loads(data)
                        # print(f"received data:\n {json.dumps(parsed_data, indent=2)}")

                        dict_of_ip_addr_and_macaddr = parsed_data["content"]
                        name_of_the_raspberrypi = parsed_data["content"]["hostname"]
                        print(f'{name_of_the_raspberrypi} found at {addr}')

                        # updates
                        number_of_found_rpi += 1
                        rpi_dict = {name_of_the_raspberrypi:dict((key, dict_of_ip_addr_and_macaddr[key]) for key in ('ip_addr', 'mac_addr'))}
                        self.rpis_ids.update(rpi_dict)

                        # finishing up 
                        conn.close()
                        break

            # closing the tcp socket         
            sock_tcp.close()           

        except Exception: 
            traceback.print_exc()
            sock_tcp.close()
            print(f"{self.number_of_rpis} raspberry pis expected but only {number_of_found_rpi} found")

    def configuration(self):
        pass 

    def take_pictures(self, delay:float, number_of_images:int, timeout:float = 30):
        """
        
        This method is used to take pictures. 
        
        It sends a request via UDP to the Raspberry Pis with the delay and number of images specified in the arguments. 
        Then it turns on server mode TCP and waits for a confirmation from each Raspberry Pi that the command is completed. 
        When a confirmation is received, it updates the dictionary of Raspberry Pi IDs with the directory of the images 
        taken by that Raspberry Pi.

        Args:
            delay (float): specifies the delay in seconds between each picture taken
            number_of_images (_type_): specifies the number of images to capture 
        """
        # request
        command = "capture"
        arguments = {"delay": delay, "number_of_images": number_of_images}
        request = self.create_json(command, arguments) 

        # sending data via and waiting for tcp response 
        self.sock_udp.sendto(bytes(request, encoding="utf-8"), (self.mcast_grp, self.mcast_port))

        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_tcp.bind((self.ipaddr, self.tcp_port))
        sock_tcp.listen()
        sock_tcp.settimeout(timeout)
        
        number_of_confirmation = 0 
        try:        
            while number_of_confirmation != self.number_of_rpis: 
                # event loop waiting for connection 
                while True:
                    conn, addr = sock_tcp.accept()
                    if conn:
                        # confirm that the connected device is in the known list 
                        if self.chek_the_ip(addr[0]): 
                            hostname_of_the_device = self.get_name_of_machine(self.rpis_ids, addr[0])
                            print(f'confirmation from {hostname_of_the_device}')
                        data = conn.recv(1024)
                        parsed_data = json.loads(data)   
                        # print(f"received data:\n {json.dumps(parsed_data, indent=2)}") 
    
                        image_dict = {'img_dir':parsed_data["content"]["dir"]}

                        # updates                     
                        number_of_confirmation += 1
                        self.rpis_ids[hostname_of_the_device].update(image_dict)
                        
                        # finishing up 
                        conn.close()
                        break

            # closing the tcp socket
            sock_tcp.close()
            return True 

        except Exception: 
            traceback.print_exc()
            sock_tcp.close()
            print(f"{self.number_of_rpis} raspberry pi(s) expected but {number_of_confirmation} confirmation received")
 
    def retrieve_images(self, server_path = Path(__file__).parent.absolute(), pi_password = "p4ssw0rd"):
        """
        
        This method retrieves images from a Raspberry Pi. 
        
        It takes two arguments: server_path and pi_password. If no value is provided for server_path, it defaults to 
        the absolute path of the directory containing the script that calls this method. If no value is provided for pi_password, 
        it defaults to "p4ssw0rd".

        The method iterates through each key in the dictionary self.rpis_ids.keys(), which contains information about each Raspberry Pi. 
        It gets the IP address and client path for each Raspberry Pi from the dictionary, then constructs a command to copy all .jpg files 
        from the client path to the server path using pscp.exe. Finally, it returns True.

        Args:
            server_path (_type_, optional): specifies the directory where the images should be saved on the server. 
            Defaults to Path(__file__).parent.absolute().
            pi_password (str, optional): password of the pis. Defaults to "p4ssw0rd".

        Returns:
            bool: True if the operation is successful
        """
        try: 
            for rpi_name in self.rpis_ids.keys():
                ip_addr = self.rpis_ids[rpi_name]["ip_addr"]
                client_path = self.rpis_ids[rpi_name]["img_dir"]
                cmd = f'pscp.exe -pw {pi_password} -P 22 pi@{ip_addr}:{client_path + "/*.jpg"} "{server_path}"'
                pid = subprocess.call(cmd, shell=True)
            return True 
        
        except Exception: 
            traceback.print_exc()


    def shutdown_setup(self):
        command = "shutdown"
        arguments = {"message":"shutdown -h now"}
        request = self.create_json(command, arguments)
        self.send_request_via_udp(request)


################################################################################################################
# RUN SCRIPT ###################################################################################################
################################################################################################################

if __name__ == '__main__':

    # setup_id = ('nt','Windows')
    setup_id = ('posix','Linux')

    with ControlComputer(setup_id) as computer:
        picture_taken = False
        computer.ping(timeout=3)
        if computer.number_of_rpis != 0:
            computer.get_raspberrypis_identification()
            picture_taken = computer.take_pictures(1,2)
            if picture_taken:
                computer.retrieve_images(server_path = Path(r'C:\Users\hilar\Documents\python_scripts\pilab\src\assets'))
            else: 
                print("The pictures were not captured")
                   
        # computer.shutdown_setup()

    
