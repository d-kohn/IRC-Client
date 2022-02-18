from types import NoneType
import PySimpleGUI as sg
import time
import asyncio
import websockets

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
                await self.sendMessage('Hey server, this is webSocket client')
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

    layout = [
        [name('Server'), sg.Input(s=30, key='-SERVER-'), sg.Button('Connect'), sg.Text(size=(25,1), key="-CONNECTED-", visible=False)],
        [name('Messages')],
        [[sg.Text(size=(90,1), key=f'-OUTPUT{row}-')] for row in range(10)],
        [sg.Input(s=50, key='-IN-', do_not_clear=False)],
        [sg.Text(size=(1,1))],
        [sg.Button('Read',bind_return_key=True, visible=True), sg.Exit()] 
    ]
    sg.theme(theme)
    window = sg.Window('IRC Chat', layout, finalize=True, right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_EXIT, keep_on_top=True, return_keyboard_events=True)
    return window

def scroll_messages(window, message_data):
    for i in range(MSG_BOX_SIZE-1):
        message_data[i] = message_data[i+1]
        window[f'-OUTPUT{i}-'].update(message_data[i])     
 
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
            username = "blah" #values['-USER-']
            if (username != "" and server != ""):
                login_window.close()
                break
    return username, server

async def main_window(client): 
    message_data = [""for i in range(MSG_BOX_SIZE)]

    window = make_window()

    while True:
        await asyncio.sleep(0.05)
        event, values = window.read(timeout=0)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break

        if event == 'Read':
            scroll_messages(window, message_data)    
            current_time = time.strftime("%I:%M:%S")
            message_data[MSG_BOX_SIZE-1] = f"{current_time} <{username}> {values['-IN-']}"
            window[f'-OUTPUT{MSG_BOX_SIZE-1}-'].update(message_data[MSG_BOX_SIZE-1])     
            await client.sendMessage(values['-IN-'])
            window['-IN-'].update("")

        while (len(rcvd_pipe) > 0):           
            scroll_messages(window, message_data)    
            current_time = time.strftime("%I:%M:%S")
            message_data[MSG_BOX_SIZE-1] = f"{current_time} <{username}> {rcvd_pipe.pop()}"
            window[f'-OUTPUT{MSG_BOX_SIZE-1}-'].update(message_data[MSG_BOX_SIZE-1])

        # if event == 'Connect':
        #     server = values['-SERVER-']
        #     window['-CONNECTED-'].update(f"Attempting to connect...", visible=True)     
            
        #     window['-CONNECTED-'].update(f"Connected: {server}", visible=True)
        #     window['-SERVER-'].update("")
        #     connected = True     
        #     window['-CONNECTED-'].update(f"Connection failed", visible=True)     
    window.close()
    exit(1)

NAME_SIZE=10
MSG_BOX_SIZE = 10

if __name__ == '__main__':
    rcvd_pipe = []
    rcvd_pipe_lock = False
    connected = False
    connection = NoneType
    username = ""
    server = ""
    # Creating client object
    client = WebSocketClient()
    loop = asyncio.get_event_loop()

    while (connected == False):
        username, server = login_window()
        # Start connection and get client connection protocol
        connection = loop.run_until_complete(client.connect(server))
        if (connection != NoneType):
            connected = True

    # Start listener and heartbeat 
    tasks = [
        asyncio.ensure_future(client.keepAlive(connection)),
        asyncio.ensure_future(main_window(client)),
        asyncio.ensure_future(client.receiveMessage(connection)),
    ]

    loop.run_until_complete(asyncio.wait(tasks))