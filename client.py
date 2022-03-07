#Change messages to an appended list.
#Add room information (Current, list, joined)
#Store UID

from types import NoneType
import PySimpleGUI as sg
import time
import asyncio
import websockets
import json

from request_processor import Request_Processor
class WebSocketClient():

    def __init__(self):
        pass

    async def connect(self, server):
        '''
            Connecting to webSocket server
            websockets.client.connect returns a WebSocketClientProtocol, which is used to send and receive messages
        '''
        try:
            self.connection = await websockets.connect(server)
            if self.connection.open:
                print('Connection stablished. Client correcly connected')
                # Send greeting
#                await self.sendMessage('Hey server, this is webSocket client')
                return self.connection
        except:
            print("Connection failed")
            return(NoneType)


    async def sendMessage(self, message):
        '''
            Sending message to webSocket server
        '''
        await self.connection.send(message)

    async def receiveMessage(self, connection):
        '''
            Receiving all server messages and handling them
        '''
        while True:
#            await asyncio.sleep(0.1)
            try:
                message = await connection.recv()
                rcvd_pipe.insert(0, message)
                print('Received message from server: ' + str(message))
            except websockets.exceptions.ConnectionClosed:
                print('Connection with server closed')
                break

    async def keepAlive(self, connection):
        '''
        Sending ping to server every 10 seconds
        Ping - pong messages to verify connection is alive
        '''
        while True:
            try:
                await connection.send('ping')
                await asyncio.sleep(30)
            except websockets.exceptions.ConnectionClosed:
                print('Connection with server closed')
                break
 
def make_window(theme=None):
    
    def name(name):
            dots = NAME_SIZE-len(name)-2
            return sg.Text(name + ' ' + '•'*dots, size=(NAME_SIZE,1), justification='r',pad=(0,0), font='Courier 10')

    # message_box_layout = [
    #     [
    #         sg.Text(size=(90,1), key=f'-OUTPUT{row}-'),
    #     ] 
    #     for row in range(10) 
    # ],

    left_layout = [
        [sg.Text('MESSAGES', font='Courier 10')],
        [sg.Text(size=(90,1), key=f'-OUTPUT0-')], 
        [sg.Text(size=(90,1), key=f'-OUTPUT1-')], 
        [sg.Text(size=(90,1), key=f'-OUTPUT2-')], 
        [sg.Text(size=(90,1), key=f'-OUTPUT3-')], 
        [sg.Text(size=(90,1), key=f'-OUTPUT4-')], 
        [sg.Text(size=(90,1), key=f'-OUTPUT5-')], 
        [sg.Text(size=(90,1), key=f'-OUTPUT6-')], 
        [sg.Text(size=(90,1), key=f'-OUTPUT7-')], 
        [sg.Text(size=(90,1), key=f'-OUTPUT8-')], 
        [sg.Text(size=(90,1), key=f'-OUTPUT9-')], 
        [sg.Input(s=90, key='-IN-', do_not_clear=False)],
        [sg.Button('Send',bind_return_key=True, visible=True)],
    ]

    right_layout = [
        [sg.Text('ROOMS', font='Courier 10')],
        [sg.Text('Create new room:', font='Courier 10')],
        [ 
            sg.Input(s=25, key='-CREATE-', do_not_clear=False), 
            sg.Button('Create'),
        ],
        [
            name('Room List'), 
            sg.Button('Update'),
            sg.Text('  User List(selected room)', font='Courier 10'),
        ],
        [
            sg.Listbox(values=[], enable_events=True, size=(30, 12), key="-ROOM LIST-"),
            sg.Listbox(values=[], enable_events=True, size=(30, 12), key="-USER LIST-"),
        ],
        [
            sg.Button('Join'),
            sg.Button('Leave'),
            sg.Button('Destroy', ),
            sg.Exit()
        ],
        
    ]

    final_layout = [
        [
            sg.Column(left_layout),
            sg.VerticalSeparator(),
            sg.Column(right_layout)
        ]
    ]

    sg.theme(theme)
    window = sg.Window(f'IRC Chat - {my_username}', layout=final_layout, finalize=True, right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_EXIT, keep_on_top=True, return_keyboard_events=True)
    return window

def scroll_messages(window, message_box):
    for i in range(MSG_BOX_SIZE-1):
        message_box[i] = message_box[i+1]
        window[f'-OUTPUT{i}-'].update(message_box[i])     
 
def login_window():
    layout1 = [
        [sg.Text('Username')], 
        [sg.Input(s=30, key='-USER-')],
        [sg.Text('Server')],
        [sg.Input(s=30, key='-SERVER-')],
        [sg.Button('Connect'), sg.Exit()] 
    ]
    login_window = sg.Window(title="Hello World", layout=layout1, margins=(100, 50))
    while (True):
        event, values = login_window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == 'Connect':
            server = "ws://localhost:8765" #values['-SERVER-']  
            my_username = values['-USER-']
            if (my_username != "" and server != ""):
                login_window.close()
                break
    return my_username, server

def update_message_box(window, message_box, message, room = '', sender_username = ''):
    scroll_messages(window, message_box)    
    current_time = time.strftime("%I:%M:%S")
    message_box[MSG_BOX_SIZE-1] = f"{current_time} #{room} <{sender_username}> {message}"
    window[f'-OUTPUT{MSG_BOX_SIZE-1}-'].update(message_box[MSG_BOX_SIZE-1])     
 
async def main_window(client, jr):
    current_room = None
    logged_in = False
    timeout = 0
    while(logged_in == False and timeout < 50):
        msg_queue_length = len(rcvd_pipe)
        if (msg_queue_length > 0):
            while (msg_queue_length > 0):
                incoming_message = rcvd_pipe.pop(0)
                message = jr.process_response(incoming_message)
                if (message[MESSAGE_TYPE] == 'USER_LOGGED_IN'):
                    uuid = message[2]
                    userId_to_username[uuid] = my_username
                    logged_in = True
#                    break
                else:
                    rcvd_pipe.append(incoming_message)
                msg_queue_length -= 1
        else:
            await asyncio.sleep(0.1)
            timeout += 1    
    if(timeout == 50):
        print("No LOGIN response from server")
        exit(0)
 
    window = make_window()
    room_list_box = window['-ROOM LIST-']
    user_list_box = window['-USER LIST-']

    while True:
        await asyncio.sleep(0.05)
        event, values = window.read(timeout=0)

        if event == sg.WIN_CLOSED or event == 'Exit':
            message = jr.build_json_request(['LOGOUT'])    
            await client.sendMessage(message)
            break

        if event == '-ROOM LIST-':
             if (room_list != [None]):
                current_room = values['-ROOM LIST-'][0]
                room_list_box.update(room_list)
                user_list_box.update(room_user_list[current_room])

        if event == 'Send':
            text = values['-IN-']
            if (current_room != None):
                if (current_room in my_rooms):
                    message = jr.build_json_request(['SEND_ROOM_MSG', roomName_to_roomId[current_room], text])
                    await client.sendMessage(message)
                    window['-IN-'].update("")
            else:
                update_message_box(window, message_box, "Join or create a room to send a message")                

        if event == 'Update':
            message = jr.build_json_request(['LIST_ALL_ROOMS'])
            await client.sendMessage(message)
            # else:
            #     update_message_box(window, message_box, "You are not in a room")                

        if event == 'Create':
            room_name = values['-CREATE-']
            if (room_name != ''):
                message = jr.build_json_request(['CREATE_ROOM', room_name])    
                await client.sendMessage(message)
                window['-CREATE-'].update("")
            else:
                update_message_box(window, message_box, "You are not in a room")                
 
        if event == 'Destroy':
            if (current_room != None):
                message = jr.build_json_request(['DESTROY_ROOM', roomName_to_roomId[current_room]])    
                await client.sendMessage(message)
            else:
                update_message_box(window, message_box, "You are not in a room")                

        if event == 'Join':
            if (current_room != None):
                if not (current_room in my_rooms):
                    message = jr.build_json_request(['JOIN_ROOM', roomName_to_roomId[current_room]])    
                    await client.sendMessage(message)
                else:
                    update_message_box(window, message_box, "You are already in that room")                
            else:
                update_message_box(window, message_box, "Select a room from the Room List to join")                

        if event == 'Leave':
            if (current_room != None):
                if (current_room in my_rooms):
                    message = jr.build_json_request(['LEAVE_ROOM', roomName_to_roomId[current_room]])    
                    await client.sendMessage(message)
            else:
                update_message_box(window, message_box, "Select a room you are in from the Room List to leave")                

        while (len(rcvd_pipe) > 0):
            incoming_message = rcvd_pipe.pop()
            message_data = jr.process_response(incoming_message)          
            server_message_type = server_message_types_list[message_data[SERVER_MESSAGE_TYPE]]
            message_type = message_data[MESSAGE_TYPE]
            (server_message_type[message_type])(window, message_data, current_room)

    window.close()
    exit(1)

# BROADCAST MESSAGE HANDLERS
def b_room_message(window, message, current_room):
    if (LOGS == True):
        print('Broadcast: Room message rcvd')
        print(message)
    roomId = message[2]
    userId = message[3]
    data = message[4]
    username = userId_to_username[userId]
    roomName = roomId_to_roomName[roomId]
    update_message_box(window, message_box, data, roomName, username)
    if (LOGS == True):
        print('Message posted')

def b_user_joined_room(window, message, current_room):
    if (LOGS == True):
        print('Broadcast: User joined room')
        print(message)
    roomId = message[2]
    userId = message[3]
    username = message[4]
    roomName = roomId_to_roomName[roomId]
    userId_to_username[userId] = username
    room_user_list[roomName].append(username)
    if roomName == current_room:
        user_list_box = window['-USER LIST-']
        user_list_box.update(room_user_list[current_room])    
    if (LOGS == True):
        print('User added')

def b_user_left_room(window, message, current_room):
    if (LOGS == True):
        print('Broadcast: User left room')
        print(message)
    roomId = message[2]
    userId = message[3]
    roomName = roomId_to_roomName[roomId]
    username = userId_to_username[userId]
    room_user_list[roomName].remove(username)
    if (roomName == current_room):
        user_list_box = window['-USER LIST-']
        user_list_box.update(room_user_list[current_room])    
    if (LOGS == True):
        print('User removed')

def b_room_destroyed(window, message, current_room):
    if (LOGS == True):
        print('Broadcast: Destroying Room')
        print(message)
    roomId = message[2]
    roomName = roomId_to_roomName[roomId]
    if roomName in my_rooms:
        my_rooms.remove(roomName)
    room_user_list.pop(roomName)
    room_list.remove(roomName)
    roomId_to_roomName.pop(roomId)
    roomName_to_roomId.pop(roomName)
    if (current_room == roomName):
        current_room = None
    room_list_box = window['-ROOM LIST-']
    room_list_box.update(room_list)
    user_list_box = window['-USER LIST-']
    user_list_box.update(room_user_list[current_room])    
    if (LOGS == True):
        print('Room destroyed')

def b_user_logged_out(window, message, current_room):
    if (LOGS == True):
        print('Broadcast: User left room')
        print(message)
    userId = message[2]
    rooms = message[3]
    for roomId in rooms:
        roomName = roomId_to_roomName[roomId]
        username = userId_to_username[userId]
        room_user_list[roomName].remove(username)
    if roomName == current_room:
        user_list_box = window['-USER LIST-']
        user_list_box.update(room_user_list[current_room])    
    if (LOGS == True):
        print('User removed')

# RESPONSE MESAGE HANDLERS
def r_user_logged_in(window, message, current_room):
    pass

def r_user_logged_out(window, message, current_room):
    update_message_box(window, "You have been logged out")

def r_send_room_msg(window, message, current_room):
    update_message_box(window, window.values['-IN-'], current_room, my_username)

def r_list_of_users(window, message, current_room):
    if (LOGS == True):
        print('Updating room user list')
        print(message)
    user_list_box = window['-USER LIST-']
    new_user_list = message[2]
    if not (len(new_user_list) == 0):
        old_user_list = room_user_list[current_room] - new_user_list
        room_user_list[current_room] = old_user_list + new_user_list
        user_list_box.update(room_user_list[current_room])
    if (LOGS == True):
        print("Updated user list")

def r_room_created(window,  message, current_room):
    if (LOGS == True):
        print('Creating Room')
        print(message)
    room_list_box = window['-ROOM LIST-']
    roomId = message[2]
    roomName = message[3]
    roomId_to_roomName[roomId] = roomName
    roomName_to_roomId[roomName] = roomId
    room_list.append(roomName)
    room_list.sort()
    room_list_box.update(room_list)
    room_user_list[roomName] = []
    if (LOGS == True):
        print("Room created")


def r_room_joined(window, message, current_room):
    if (LOGS == True):
        print('Joining room')
        print(message)
    roomId = message[2]
    roomName = roomId_to_roomName[roomId]
    user_list = message[3]

    for user in user_list:
        userId = user['userId']
        username = user['username']
        userId_to_username[userId] = username
        (room_user_list[roomName]).append(username)
    my_rooms.append(roomName)
    current_room = roomName
    user_list_box = window['-USER LIST-']
    user_list_box.update(room_user_list[current_room])    
    if (LOGS == True):
        print("Joined")

def r_room_left(window, message, current_room):
    if (LOGS == True):
        print("Leaving Room")
        print(message)
    roomId = message[2]
    roomName = roomId_to_roomName[roomId]
    my_rooms.remove(roomName)
    room_user_list[roomName] = []
#    if roomName == current_room:
    current_room = None
    user_list_box = window['-USER LIST-']
    user_list_box.update(room_user_list[current_room])    
    if (LOGS == True):
        print("Room left")

def r_list_of_rooms(window, message, current_room):
    if (LOGS == True):
        print("Updating room list")
        print(message)
    room_list_box = window['-ROOM LIST-']
    new_room_list = message[2]
    if not(len(new_room_list) == 0):
        for room in new_room_list:
            roomId = room['roomId']
            roomName = room['roomName']
            if not (roomName in roomName_to_roomId or roomId in roomId_to_roomName):
                roomId_to_roomName[roomId] = roomName
                roomName_to_roomId[roomName] = roomId
                room_list.append(roomName)
                if not (roomName in room_user_list):
                    room_user_list[roomName] = []                       
        room_list_box.update(room_list)

    if (LOGS == True):
        print("Updated room list")

def r_room_destroyed(window, message, current_room):
    if (LOGS == True):
        print('Destroying Room')
        print(message)
    roomId = message[2]
    roomName = roomId_to_roomName[roomId]
    if roomName in my_rooms:
        my_rooms.remove(roomName)
    room_user_list.pop(roomName)
    room_list.remove(roomName)
    roomId_to_roomName.pop(roomId)
    roomName_to_roomId.pop(roomName)
    current_room = None
    room_list_box = window['-ROOM LIST-']
    room_list_box.update(room_list)
    user_list_box = window['-USER LIST-']
    user_list_box.update(room_user_list[current_room])    
    if (LOGS == True):
        print('Room destroyed')

def r_error(window, message, current_room):
    msg = message[2]
    update_message_box(window, f'ERROR Received!!!! {msg}')
    


NAME_SIZE=20
MSG_BOX_SIZE = 10
MESSAGE_TYPE = 1
SERVER_MESSAGE_TYPE = 0
LOGS = True

broadcast_functions = {
        'ROOM_MESSAGE' : b_room_message,
    'USER_JOINED_ROOM' : b_user_joined_room,
      'USER_LEFT_ROOM' : b_user_left_room,
      'ROOM_DESTROYED' : b_room_destroyed,
     'USER_LOGGED_OUT' : b_user_logged_out
}

response_functions = {
     'USER_LOGGED_IN' : r_user_logged_in,
    'USER_LOGGED_OUT' : r_user_logged_out,
      'SEND_ROOM_MSG' : r_send_room_msg,
      'LIST_OF_USERS' : r_list_of_users,
       'ROOM_CREATED' : r_room_created,
        'ROOM_JOINED' : r_room_joined,
          'ROOM_LEFT' : r_room_left,
      'LIST_OF_ROOMS' : r_list_of_rooms,
     'ROOM_DESTROYED' : r_room_destroyed,
              'ERROR' : r_error
}

server_message_types_list = {
    'broadcast' : broadcast_functions,
    'response' : response_functions
}

if __name__ == '__main__':
    rcvd_pipe = []
    rcvd_pipe_lock = False
    connected = False
    connection = NoneType
    my_username = ""
    server = ""
    uuid = ""
    userId_to_username = {}
    roomName_to_roomId = {}
    roomId_to_roomName = {}
    room_user_list = {}
    room_user_list[None] = []
    room_list = []
    my_rooms = []
#    current_room = None
    message_box = [""for i in range(MSG_BOX_SIZE)]

    # Creating client object
    client = WebSocketClient()
    jr = Request_Processor()
    loop = asyncio.get_event_loop()

    while (connected == False):
        my_username, server = login_window()
        # Start connection and get client connection protocol
        connection = loop.run_until_complete(client.connect(server))
        if (connection != NoneType):
            connected = True
            login_info = jr.build_json_request(['LOGIN', my_username])
            print(login_info)
            loop.run_until_complete(client.sendMessage(login_info))
  
    # Start listener and heartbeat 
    tasks = [
#        asyncio.ensure_future(client.keepAlive(connection)),
        asyncio.ensure_future(main_window(client, jr)),
        asyncio.ensure_future(client.receiveMessage(connection)),
    ]

    loop.run_until_complete(asyncio.wait(tasks))