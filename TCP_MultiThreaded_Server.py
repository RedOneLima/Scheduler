import threading
import SocketServer


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
#---------------------------These are my own methods implemented in the handler class --------------------------------
    def sendAval(self, schedule):
        #This checks the dictionary that's passed in as schedule and any time key that has an assosiated value of
        # -1 means the time is avalible and its added to the string aval to return avalible times.
            aval = ''
            for key, value in schedule.iteritems():
                if value is -1:
                    aval += key+' '
            return aval

    def schedule(self,schedule,data, userInfo, ID):
        #The function that handles sceduling the appointment
        responseCode = '-1'
        self.lock.acquire()
        #Begin critical section
        if schedule[data] == -1:
        #Although unavalible times won't show to the client this is there to check if they entered something other
        #than the listed times.
            try:
                print 'data',data
                #write the appointment to the dictionary
                schedule.update({data: userInfo})
                #persistance in a file
                file = open("scheduleFile", 'a')
                file.write(ID+':'+data+':'+userInfo+'\n')
                file.close()
                print file, "Updated"
                #confrimation of successful scheduling
                responseCode = '200'
                print 'Update: ', schedule
            finally:
                #This ensures that the lock will be released regardless of what happens during the execution of the
                #critical section
                self.lock.release()
                return schedule, responseCode
        else:

            print 'Request Denied for date ',data
            return schedule, responseCode

#---------------------These are handler methods from the ServerSocket ThreadedTCPRequestHandler class-----------------
    def setup(self):
        print 'Client connected {}'.format(threading.current_thread().name)
        self.lock = threading.Lock()

    def finish(self):
        print 'Client finished {}'.format(threading.current_thread().name)
#----------------------------------------------------------------------------------------------------------------------

    def handle(self):
        #volitile instances of the scedule to be maintained as long as the server is running
        global BillAval
        global JennyAval
        global GeorgeAval
        docs = ''
        while 1:
            try:
                data = self.request.recv(1024)
                #Checks for protocol level being receved from client
                if data[0] == '1':
                    #First protocol level returns list of avalible providers
                    userInfo = data[1:]
                    self.request.sendall(doclist)
                elif data[0] == '2':
                    #Second protocol level indicates which provider was selected and dynamically builds the time
                    #avalibility for the selected provider
                    if data[1] == '2':
                        self.request.sendall(self.sendAval(BillAval))
                        #This is where the client sends selected time
                        data = self.request.recv(1024)
                        #calls function with critical section
                        BillAval, requestCode = self.schedule(BillAval,data,userInfo, '2')
                        #Sends back all the same info if the request was accepted or denied and client handles the result
                        self.request.sendall(requestCode+':'+userInfo+':'+data)
                    elif data[1] == '1':
                        aval = self.sendAval(JennyAval)
                        self.request.sendall(aval)
                        data = self.request.recv(1024)
                        JennyAval, requestCode = self.schedule(JennyAval,data,userInfo,'1')
                        self.request.sendall(requestCode+':'+userInfo+':'+data)
                    elif data[1] == '3':
                        aval = self.sendAval(GeorgeAval)
                        self.request.sendall(aval)
                        data = self.request.recv(1024)
                        GeorgeAval, requestCode = self.schedule(GeorgeAval,data,userInfo, '3')
                        self.request.sendall(requestCode+':'+userInfo+':'+data)
                    break
            except EnvironmentError:
                print 'Client {} on {} closed'.format(self.client_address, threading.current_thread().name)
                break

#----------------------------------------------------------------------------------------------------------------------

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

#----------------------------------------------------------------------------------------------------------------------
doclist = 'Jenny Billings\nGeneral Practice\n(303)888-3940\n1328 Smith Rd:' \
          'Bill Jefferey\nNutritionist\n(720)558-3794\n9820 88th Ave:' \
          'George Sanders\nPediatrics\n(70)559-8570\n4582 Cleavland St'
JennyAval = {'9':-1, '10':-1, '11':-1, '12':-1, '13':-1,'14':-1, '15':-1, '16':-1}
BillAval = {'9':-1, '10':-1, '11':-1, '12':-1, '13':-1,'14':-1, '15':-1, '16':-1}
GeorgeAval = {'9':-1, '10':-1, '11':-1, '12':-1, '13':-1,'14':-1, '15':-1, '16':-1}

#this function is outside of the class and will run only at the start up of the program
#reads any data that was saved during the execution of the critical section and persists any appointments that were made
#each line is marked with an identifier for which provider was scheduled and fills the appropriate dictionary prior to
#the server initalization.
file = open("scheduleFile", 'r')
for line in file:
    if line is '':
        break
    fillLine = line.split(':')
    print fillLine
    if fillLine[0] is '1':
        JennyAval.update({fillLine[1]:fillLine[2]})
    elif fillLine[0] is '2':
        BillAval.update({fillLine[1]:fillLine[2]})
    elif fillLine[0] is '3':
        GeorgeAval.update({fillLine[1]:fillLine[2]})
#---------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    #initalizing the server
    HOST, PORT = "localhost", 4445
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    print "Server loop running in thread:", server_thread.name

#----------------------------------------------------------------------------------------------------------------------





