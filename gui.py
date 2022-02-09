import PySimpleGUI as sg
import time
import asyncio
import websockets
 
NAME_SIZE=10
MSG_BOX_SIZE = 10

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
 
async def test_connection(server):
    async with websockets.connect(server) as websocket:
        await websocket.send("Connected")
        response = await websocket.recv()
    return response

async def test_messages(server, message):
    async with websockets.connect(server) as websocket:
        await websocket.send(f"RCVD: {message}")
        response = await websocket.recv()
    return response

def main(): 
    connected = False
    username = "dkohn"
    window = make_window()
    server = ""
    message_data = [""for i in range(MSG_BOX_SIZE)]

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == 'Read' and connected == True:
            scroll_messages(window, message_data)    
            current_time = time.strftime("%I:%M:%S")
            message_data[MSG_BOX_SIZE-1] = f"{current_time} <{username}> {values['-IN-']}"
            window[f'-OUTPUT{MSG_BOX_SIZE-1}-'].update(message_data[MSG_BOX_SIZE-1])     

            response = asyncio.get_event_loop().run_until_complete(test_messages(server, values['-IN-']))
            scroll_messages(window, message_data)    
            current_time = time.strftime("%I:%M:%S")
            message_data[MSG_BOX_SIZE-1] = f"{current_time} <{username}> {response}"
            window[f'-OUTPUT{MSG_BOX_SIZE-1}-'].update(message_data[MSG_BOX_SIZE-1])     
            window['-IN-'].update("")
        if event == 'Connect':
            server = values['-SERVER-']
            window['-CONNECTED-'].update(f"Attempting to connect...", visible=True)     
            response = asyncio.get_event_loop().run_until_complete(test_connection(server))
            if (response == 'Connected'):
                window['-CONNECTED-'].update(f"Connected: {server}", visible=True)
                window['-SERVER-'].update("")
                connected = True     
            else:
                window['-CONNECTED-'].update(f"Connection failed", visible=True)     

    window.close()


if __name__ == '__main__':
    main()