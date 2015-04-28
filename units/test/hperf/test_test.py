import test

d = {'usernames':['cacho', 'rojo', 'hacker'],
     'passwords':['1234', '12345', '123456'],
     'pairs':['admin', 'admin']}

def callback(username, password):
    print('[!] Login! username: {0} - password: {1}'.format(username, password))

c = test.Test(callback)

c.crack(**d)
