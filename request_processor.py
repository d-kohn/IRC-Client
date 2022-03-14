from copy import deepcopy
from http import server
import json
class Request_Processor:
    requests = {
               'LOGIN' : ['request', 'username'],
              'LOGOUT' : ['request'],
       'SEND_ROOM_MSG' : ['request', 'roomId', 'data'],
         'CREATE_ROOM' : ['request', 'room_name'],
           'JOIN_ROOM' : ['request', 'roomId'],
          'LEAVE_ROOM' : ['request', 'roomId'],
        'DESTROY_ROOM' : ['request', 'roomId'],
      'LIST_ALL_ROOMS' : ['request'],
   'LIST_ROOM_MEMBERS' : ['request', 'roomId']
    }

    broadcasts = {
            'ROOM_MESSAGE' : ['broadcast', 'roomId', 'userId', 'msg'],
        'USER_JOINED_ROOM' : ['broadcast', 'roomId', 'userId', 'username'],
          'USER_LEFT_ROOM' : ['broadcast', 'roomId', 'userId'],
          'ROOM_DESTROYED' : ['broadcast', 'roomId'],
         'USER_LOGGED_OUT' : ['broadcast', 'userId', 'rooms']
    }

    responses = {
         'USER_LOGGED_IN' : ['response', 'userId'],
        'USER_LOGGED_OUT' : ['response', 'userId'],
          'SEND_ROOM_MSG' : ['response'],
          'LIST_OF_USERS' : ['response', 'users'],
           'ROOM_CREATED' : ['response', 'roomId', 'roomName'],
            'ROOM_JOINED' : ['response', 'roomId', 'users'],
              'ROOM_LEFT' : ['response', 'roomId'],
          'LIST_OF_ROOMS' : ['response', 'rooms'],
         'ROOM_DESTROYED' : ['response', 'roomId'],
                  'ERROR' : ['response', 'msg']
    }

    server_message_types = {
        'broadcast' : broadcasts,
        'response' : responses
    }

    def __init__(s):
        pass
    
    # Takes a request type string, ie 'LOGIN', and a list of data for the request
    # Returns formated JSON request, eg { 'request' : '<request_type>', '<element>', <data>, '<element>', <data>, ...}
    def build_json_request(s, request_data):
#        print(f"Request Data: {request_data}")
        try:
            request_format = s.requests[request_data[0]]
        except:
            print(f"Invalid request type: {request_data}")
            return -1

        request = {}
#        request[request_format[0]] = request_data[0]
        for element in range(len(request_format)):
            try:
                request[request_format[element]] = request_data[element]
            except:
                print(f"Data length does not match format:")
                print(f"{request_format}")
                print(f"{request_data}")
                return -2
        request = json.dumps(request)
#        print(f"Request JSON: {request}")
        return request
    
    def process_response(s, incoming_json):
        print(f"Processing: {incoming_json}")
        try:
            incoming_message = json.loads(incoming_json)
        except:
            print("Improperly formatted server json")

        # Determine if message is 'broadcast' or 'response
        for server_message_type in s.server_message_types:
            if server_message_type in incoming_message:
               # Determine the type of message being sent
                for message_type in s.server_message_types[server_message_type]:
                    if (incoming_message[server_message_type] == message_type):
                        message = deepcopy((s.server_message_types[server_message_type])[message_type])
                        for i in range(len(message)):
                            try: 
                                field_key = message[i]
                                message[i] = incoming_message[field_key]
                            except:
                                print("Improperly formatted server message")
                                print(incoming_message)
                        message.insert(0, server_message_type)
                        break
                break
#        print(f"Message Data: {message}")
        return message
