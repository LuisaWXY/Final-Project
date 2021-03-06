"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import json
import indexer
#for RSA encryption
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto import Random


class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        self.history = {}
        #threading
        self.peer_display = ''
        self.system_display = ''
        #encryption
        self.key = RSA.generate(2048)
        myKey = self.me + 'Key.pem'
        f = open(myKey,'wb')
        f.write(self.key.exportKey('PEM'))
        f.close()
        

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name
        myKey = self.me + 'Key.pem'
        f = open(myKey,'wb')
        f.write(self.key.exportKey('PEM'))
        f.close()

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            self.system_display += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
            self.system_display += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
            self.system_display += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
            self.system_display += 'User is not online, try again later\n'

        return(False)

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.system_display += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.system_display += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in
                    self.system_display += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.system_display += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in
                    self.system_display += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                        self.system_display += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.system_display += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'
                        self.system_display += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    #mysend(self.s, json.dumps({"action":"search", "target":term}))
                    #search_rslt = json.loads(myrecv(self.s))["results"].strip()
                    #search_rslt = '\n'.join([x[-1] for x in self.history[self.me].search(term)])
                    
                    search_rslt = []
                    for i in self.history[self.me]:
                        if term in i:
                            search_rslt.append(i)       
                    
                    
                    if (len(search_rslt)) > 0:
                        self.out_msg += str(search_rslt) + '\n\n'
                        self.system_display += str(search_rslt) + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'
                        self.system_display += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"]
                    # print(poem)
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                        self.system_display += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'
                        self.system_display += 'Sonnet ' + poem_idx + ' not found\n\n'

                else:
                    self.out_msg += menu
                    self.system_display += menu

            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.system_display += 'Request from ' + self.peer + '\n'
                    self.system_display += 'You are connected with ' + self.peer
                    self.system_display += '. Chat away!\n\n'
                    self.system_display += '------------------------------------\n'
                    self.state = S_CHATTING

#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                
                said = text_proc(my_msg, '[' + self.me + ']')
                if self.me in self.history:
                    self.history[self.me].append(said) 
                else: 
                    self.history[self.me] = [said]
                   
                if my_msg == 'bye':       
                    
                    #encryption
                    my_msg = my_msg.encode('utf-8')
                    h = SHA.new(my_msg)
                    
                    peerKey = self.peer + 'Key.pem'
                    f = open(peerKey,'r')
                    
                    
                    peerPubKey = RSA.importKey(f.read())
                    
                    cipher = PKCS1_v1_5.new(peerPubKey)
                    ciphertext = cipher.encrypt(my_msg+h.digest())
                    msg = ciphertext.decode("cp437")
                    
                    #end of encryption
                    
                    mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":msg}))
  
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
                
                else:
                    #encryption
                    my_msg = my_msg.encode('utf-8')
                    h = SHA.new(my_msg)
                    
                    peerKey = self.peer + 'Key.pem'
                    f = open(peerKey,'r')
                    
                    
                    peerPubKey = RSA.importKey(f.read())
                    
                    cipher = PKCS1_v1_5.new(peerPubKey)
                    ciphertext = cipher.encrypt(my_msg+h.digest())
                    msg = ciphertext.decode("cp437")
                    
                    #end of encryption
                    
                    mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":msg}))
            
            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                
                
                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                elif peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                    
                else:
                    
                    #decryption
                    
                    dsize = SHA.digest_size
                    sentinel = Random.new().read(15+dsize)      # Let's assume that average data length is 15
                    
                    msg = peer_msg["message"]
                    message = msg.encode("cp437")
                    
                    #show message before decryption
                    print(message)
                    
                    myKey = self.me + 'Key.pem'
                    f = open(myKey,'r')
                    myPrivateKey = RSA.importKey(f.read())
                    cipher = PKCS1_v1_5.new(myPrivateKey)
                    message = cipher.decrypt(message, sentinel)
                    
                    
                    message = message[:-dsize]
                    message = message.decode("utf-8")
                    peer_msg["message"] = message
                    
                    #end of decryption
                    
                    said2 = text_proc(message, peer_msg["from"])
                    if self.me in self.history:
                        self.history[self.me].append(said2) 
                    else: 
                        self.history[self.me] = [said2]
            
                    
                    self.out_msg += peer_msg["from"] + peer_msg["message"]
                    self.peer_display = peer_msg["from"] + peer_msg["message"]


            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
                self.system_display += menu
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            self.system_display += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
