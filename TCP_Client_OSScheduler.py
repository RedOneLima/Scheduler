import socket

#setting up socket information
HOST, PORT = "localhost", 4445
data = ''
#Create socket where SOCK_STREAM indicates a TCP connection
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((HOST, PORT))
except socket.error:
    print socket.error
else:
    #Take in PPI
    print 'Hello Welcome to the scheduling system.\n'
    userInfo = raw_input('Enter Name:' )
    userInfo += ' '
    userInfo += raw_input('Enter Birthdate (mm/dd/yyyy): ')
    #Client begins communication with server at this point
    #the string '1' indicates protocol level
    sock.sendall('1'+userInfo)
    #Server responds with the provider information
    received = sock.recv(1024)
    docs = received.split(':')
    while 1:
        try:
            print '\nPlease Pick a Provider to set an appointment.\n'
            counter = 0
            #itterate through list of doctors to show as a list
            for items in docs:
                print counter+1, '.',docs[counter],'\n'
                counter+=1
            docSelection = raw_input('>> ')
            #'2' indicates the second level of the protocol is complete
            sock.sendall('2'+docSelection)
            #server responds with avalible times
            avalibleTimes = sock.recv(1024)
            avalibleTimes.split()
            counter = 9
            #since lists have no particular order an accumulator is used to display times in order
            if len(avalibleTimes) == 0:
                print "No available times"
            else:
                for time in avalibleTimes:
                    if str(counter) in avalibleTimes:
                        print str(counter)+':00'
                        counter+=1
                    else:
                        counter+=1
                timeSelection = raw_input("Pick an available time\n>>")
                if ':' in timeSelection:
                    timeSelection2 = timeSelection.split(':')
                    sock.sendall(str(timeSelection2[0]))
                else:
                    sock.sendall(timeSelection)
                #server will either respond with a -1 indicating the appointment was not made or a 200 confrimation
                received = sock.recv(1024)
                if '-1' in received:
                    print 'Sorry this appointment is not available.'
                elif '200'in received:
                    print '\n'
                    confirm = received.split(':')
                    name = confirm[1]
                    time = confirm[2]
                    #print confrimation info for user
                    print 'Appointment Confirmed\n' \
                          'Patient Info: ', name
                    print 'Time: ', time+':00'
                    print 'Thank you.'
                break
        except socket.error:
            #closes the socket in the event of an error.
          sock.close()
          print 'socket closed'
          break
    else:
            #ensures the socket is closed in any case other than an error.
        sock.close()
        print 'socket closed'