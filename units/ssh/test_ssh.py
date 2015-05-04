import ssh

d = {'usernames':['cacho', 'rojo', 'hacker'],
     'passwords':['1234', '12345', '123456'],
     'pairs':[('admin', 'admin'), ('cacho', '111111')]}

def callback(username, password):
    print('[!] Login! username: {0} - password: {1}'.format(username, password))

c = ssh.SSH(callback)

c.crack(**d)
