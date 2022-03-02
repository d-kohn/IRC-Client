class JSON_Request:
    login_format = ['request', 'username']
    logout_format = ['request', 'uuid']
    send_format = ['request', 'uuid', 'roomId', 'data']
    create_room_format = ['request', 'room_name']
    join_room_format = ['request', 'uuid', 'roomId']
    leave_room_format = ['request', 'uuid', 'roomId']
    destroy_room_format = ['request', 'roomId']
    update_format = ['request', 'uuid']

    requests = {
               'LOGIN' : login_format,
              'LOGOUT' : logout_format,
                'SEND' : send_format,
         'CREATE_ROOM' : create_room_format,
           'JOIN_ROOM' : join_room_format,
          'LEAVE_ROOM' : leave_room_format,
        'DESTROY_ROOM' : destroy_room_format,
              'UPDATE' : update_format
     }

    def __init__(s):
        pass
    
    # Takes a request type string, ie 'LOGIN', and a list of data for the request
    # Returns formated JSON request, eg { 'request' : '<request_type>', '<element>', <data>, '<element>', <data>, ...}
    def build_json_request(s, request_data):
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
                return -1

        return request
            