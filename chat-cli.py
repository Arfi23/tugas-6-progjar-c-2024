import socket
import os
import json

TARGET_IP = "127.0.0.1"
TARGET_PORT = 8889

class ChatClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP,TARGET_PORT)
        self.sock.connect(self.server_address)
        self.tokenid=""
    def proses(self,cmdline):
        j=cmdline.split(" ")
        try:
            command=j[0].strip()
            if (command=='auth'):
                username=j[1].strip()
                password=j[2].strip()
                return self.login(username,password)
            elif (command=='send'):
                usernameto = j[1].strip()
                message=""
                for m in j[2:]:
                   message="{} {}" . format(message,m)
                return self.sendmessage(usernameto,message)
            elif (command=='inbox'):
                return self.inbox()
            elif (command=='sendgroup'):
                group_name = j[1].strip()
                message=""
                for m in j[2:]:
                   message="{} {}" . format(message,m)
                return self.sendgroupmessage(group_name, message)
            elif (command == 'sendrealm'):
                username_to = j[1].strip()
                message = ""
                for m in j[2:]:
                    message = "{} {}".format(message, m)
                return self.send_realm_message(username_to, message)
            elif (command=='sendgrouprealm'):
                # realm_id = j[1].strip()
                group_name = j[1].strip()
                message=""
                for m in j[2:]:
                    message="{} {}" . format(message,m)
                return self.send_group_realm_message(group_name, message)
            elif (command == 'getrealminbox'):
                realm_id = j[1].strip()
                return self.get_realm_inbox(realm_id)
            else:
                return "*Maaf, command tidak benar"
        except IndexError:
                return "-Maaf, command tidak benar"
    def sendstring(self,string):
        try:
            self.sock.sendall(string.encode())
            receivemsg = ""
            while True:
                data = self.sock.recv(64)
                print("diterima dari server",data)
                if (data):
                    receivemsg = "{}{}" . format(receivemsg,data.decode())  #data harus didecode agar dapat di operasikan dalam bentuk string
                    if receivemsg[-4:]=='\r\n\r\n':
                        print("end of string")
                        return json.loads(receivemsg)
        except:
            self.sock.close()
            return { 'status' : 'ERROR', 'message' : 'Gagal'}
    def login(self,username,password):
        string="auth {} {} \r\n" . format(username,password)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=result['tokenid']
            return "username {} logged in, token {} " .format(username,self.tokenid)
        else:
            return "Error, {}" . format(result['message'])
    def sendmessage(self,usernameto="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="send {} {} {} \r\n" . format(self.tokenid,usernameto,message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])
    def inbox(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inbox {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['messages']))
        else:
            return "Error, {}" . format(result['message'])
        
    def sendgroupmessage(self,group_name="xxx",message="yyy"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="sendgroup {} {} {} \r\n" . format(self.tokenid, group_name, message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent to {}" . format(group_name)
        else:
            return "Error, {}" . format(result['message'])
    
    def send_realm_message(self, username_to, message):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="sendrealm {} {} {} \r\n" . format(self.tokenid, username_to, message)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "Message sent to {} in the other realm".format(username_to)
        else:
            return "Error, {}".format(result['message'])
        
    def send_group_realm_message(self, group_name, message):
        if self.tokenid=="":
            return "Error, not authorized"
        string="sendgrouprealm {} {} {} \r\n" . format(self.tokenid, group_name, message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent to group {} in realm 2" .format(group_name)
        else:
            return "Error {}".format(result['message'])

    def get_realm_inbox(self, realm_id):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="getrealminbox {} {} \r\n" . format(self.tokenid, realm_id)
        print("Sending: " + string)
        result = self.sendstring(string)
        print("Received: " + str(result))
        if result['status']=='OK':
            return "Message received from realm {}: {}".format(realm_id, result['messages'])
        else:
            return "Error, {}".format(result['message'])

if __name__=="__main__":
    cc = ChatClient()
    while True:
        cmdline = input("Command {}:" . format(cc.tokenid))
        print(cc.proses(cmdline))