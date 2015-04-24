import test

d = {'usernames':['cacho', 'rojo', 'hacker'],
     'passwords':['1234', '12345', '123456'],
     'pairs':['admin', 'admin']}

def callback(username, password):
    print('[!] Login! username: {0} - password: {1}'.format(username, password))

def algo():
    print('TEST FUNC')

c = test.Cracker("callback")

c.crack([1,2], [1,2], [2,3])