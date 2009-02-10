# Written By Kevin "KJ" Jacobson (kj@csh.rit.edu)
# Based on a script written by Angelo Dinardi
# Version .01
# Must be run on a server with ldapsearch

"""
    Things that need to be added to this API
    0. Clear the damn buffer after recieving a messager
    1. Ability to authenticate users w/o iButton
    2. Access to user purchasing records
"""

import getpass
import os
import socket
import subprocess
import sys
import time


#Magic Numbers!
MAX_PACKET_SIZE = 1024
ANGELO_IS_FUCKING_PSYCHO = MAX_PACKET_SIZE
LDAP_NAME = "ldap"
MSG_STAT = 'STAT\n'
MSG_BALANCE = 'GETBALANCE\n'
MSG_OK = 'OK'
MSG_ERROR = 'ERR'


class Network:
    """Stores and retrieves information relevant to entire network of vending machine System (s). """
    domainURL = ""
    systems = []
  
    def __init__(self, domainURL):
        """Constructor for Network class. Sets the URL for the domain which the network resides. """
        self.domainURL = domainURL

    def add_systems(self, *networkSystems):
        """Adds the system to the Network"""
        for system in networkSystems:
            self.systems.append(system)
            
    def get_systems(self):
        """Returns a list of all the systems associated with a Network. """
        return self.systems
  
    def get_domain(self):
        """Returns the URL of the domain which the Network belongs to. """
        return self.domainURL

class System:
    """Represents the individual machine including it's name, location and inventory. """
    hostname = ""
    inventory = []
    connectedUsers = []
    port = None
    
    def __init__(self, name,hostname, port=4242):
        """Constructor for class System. """
        self.name = name
        self.hostname = hostname
        self.port = port
        
    def add_connection(self, *users):
        """Stores Users with open connections to this System. """
        for user in users:
            if user.authed: #and connected to THIS system
                self.connectedUsers.append(user)
                            
    def remove_connection(*users):
        """Disconnects the specified User(s) and purges disconnected User(s). """
        for user in users:
            user.disconnect()
        for user in self.connectedUsers:
            if not user.connected():
                self.connectedUsers.remove(user)
                
    def check_inventory(self, user):
        """Updates the local inventory of the System. Requires an authenticated and connected User. """
        if user.connected():
            self.inventory=[]
            user.connectionSocket.sendall(MSG_STAT)
            data =''
            data = user.connectionSocket.recv(MAX_PACKET_SIZE)
            if data.find(MSG_OK) == - 1 and data.find(MSG_ERROR) == - 1:
                self.__parse_inventory__(data)
            data = user.connectionSocket.recv(MAX_PACKET_SIZE)
                
                
    def __parse_inventory__(self, data):
       """Parses the text returned by the System and then puts the appropriate Item s into 'inventory'. """
       lines = data.splitlines()
       for line in lines:
           splitline = line.split('"')
           if len(splitline) < 3: #I <3 THIS LINE
               continue
           slot = splitline[0].strip()
           name = splitline[1].strip()
           remainingText = splitline[2].split(' ')
           price = remainingText[1]
           quantity = remainingText[2]
           self.inventory.append(Item(name, quantity, price, slot))
           
    def __str__(self):
           result = ""
           result += "Current System:\t"+self.name + '\n' + 'Slot\t'+'Item\t\t\tCost\tRemaining\n'
           for item in self.inventory:
               result += '\n'+str(item.slot) + '\t' + item.name.ljust(20) + '\t' + str(item.price) + '\t' + str(item.quantity)
           return result

    
                            
class User:
    """Represents a User, his/her current System connection, and purchases. """
    name = ""
    connectionSocket = None
    authed = False
    connectedSystem = None
    ibutton = None
  
    def __init__(self, name, ibutton=None):
        """Constructsor for User class, stores  User's username. """
        self.name = name
        self.ibutton = ibutton

    def connect_to_system(self, system, network):
        """Connects the User to the system. """
        self.connectionSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        url = system.hostname + "." + network.get_domain()
        self.connectionSocket.connect((url, system.port))
        data = self.connectionSocket.recv(MAX_PACKET_SIZE)
        if data[:2] == MSG_OK:
            if self.ibutton is None:
                authed = self.authenticate_user(self)
            else:
                authed = self.authenticate_user_ibutton(self.ibutton)
            if authed:
                self.connectedSystem = system
                self.connectedSystem.check_inventory(self)
        return authed

    def authenticate_user(self, user):
        """Confirms the legitimacy of the User and logs them into the System. """
        cmd = 'ldapsearch -h ldap.csh.rit.edu "(uid=' + user.name + ')" ibutton 2> /dev/null'
        process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        fin, fout = process.stdin, process.stdout
        line = fout.readline()
        smegma = 0
        while line.startswith('ibutton') != True and smegma < 100:
            line = fout.readline()
            smegma += 1
            
        authed = 0
        if line.startswith('ibutton'):
            self.connectionSocket.sendall('ibutton ' + line[9:25] + '\n')
            data = ''
            while data.find('\n') == - 1:
                data += self.connectionSocket.recv(MAX_PACKET_SIZE)
            if data.find(MSG_OK) != - 1:
                self.authed = True
                return True
        self.authed = False
        return False

    def authenticate_user_ibutton(self, ibutton):
      self.connectionSocket.sendall('ibutton ' + ibutton + '\n')
      data = ''
      while data.find('\n') == -1:
        data += self.connectionSocket.recv(MAX_PACKET_SIZE)
      if data.find(MSG_OK) != -1:
        self.authed = True
        self.name = data[9:len(data) - 2]
        return True
      self.authed = False
      return False
    
    def disconnect(self):
        """Disconnects the User from the currently connected System. """
        self.authed = False
        self.connectionSocket.close()
        self.connectionSocket = None
        self.connectedSystem = True
        
    def connected(self):
        """Returns whether or not the User is connected to a System. """
        return (bool)(self.authed and self.connectionSocket and self.connectedSystem)
        
    def get_credits_balance(self):
        """Finds the User's current credit balance. """
        if self.connected():
            self.connectionSocket.sendall(MSG_BALANCE)
            data = self.connectionSocket.recv(MAX_PACKET_SIZE)
            if data.find(MSG_OK) == - 1 and data.find(MSG_ERROR) == - 1:
                data += self.connectionSocket.recv(MAX_PACKET_SIZE)
            return int(data[3:100].split()[1].strip())
        
    
    def purchase(self, item, delay):
       """User purchases an Item from the System inventory. """
       if item.in_stock() and self.connected() and (item in self.connectedSystem.inventory):
           cmd = 'DROP ' + str(item.slot) + ' ' + str(delay) + '\n'
           self.connectionSocket.send(cmd)
           return self.connectionSocket.recv(MAX_PACKET_SIZE)
        
    
class Item:
    """Class representing an item and its quantity within a system. """
    name = ""
    price = 0
    quantity = 0
    slot = - 1
    def __init__(self, name, quantity, price, slot):
        """Constructor for Item class. """
        self.name = name
        self.quantity = int(quantity)
        self.price = int(price)
        self.slot = int(slot)
    
    def in_stock(self):
        """Checks whether or not an Item is in stock. """
        return self.quantity > 0


    
