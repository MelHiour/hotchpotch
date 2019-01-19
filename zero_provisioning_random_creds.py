import yaml
import pexpect
import random
import concurrent.futures

devices = [i for i in range(32897, 32947)]
ids = [i for i in range(1,51)]
creds_yaml = '''
usernames:
    - misha
    - katya
    - petya
    - sasha
passwords:
    - SuperSecretPass1
    - G00D$ecurePa$$password2
    - WTF300
    - ILoveMyWife
'''
creds = yaml.load(creds_yaml)
creds_product = list(itertools.product(creds['usernames'], creds['passwords']))

def provision(devices, ids, limit = 50):
    with concurrent.futures.ThreadPoolExecutor(max_workers=limit) as executor:
        executor.map(zero_provisioning, devices, ids)

def zero_provisioning(port, id):
    loginpass = random.choice(creds_product)
    with pexpect.spawn('telnet 192.168.0.29 {}'.format(port)) as t:
        print('Provisioning R{} via port {}'.format(id, port))
        t.sendline()
        t.expect('no]:')
        t.sendline('no')
        t.expect('Press RETURN to get started!')
        t.sendline('\r\n')
        t.expect('[>#]')
        t.sendline('enable')
        t.expect('[>#]')
        t.sendline('conf t')
        t.expect('[>#]')
        t.sendline('no service config')
        t.expect('[>#]')
        t.sendline('hostname R{}'.format(id))
        t.expect('[>#]')
        t.sendline('interface e0/0')
        t.expect('[>#]')
        t.sendline('no shutdown')
        t.expect('[>#]')
        t.sendline('ip address 192.168.30.{} 255.255.255.0'.format(id))
        t.expect('[>#]')
        t.sendline('username {} priv 15 secret {}'.format(loginpass[0], loginpass[1]))
        t.expect('[>#]')
        t.sendline('enable secret melhiour')
        t.expect('[>#]')
        t.sendline('ip route 0.0.0.0 0.0.0.0 192.168.30.254')
        t.expect('[>#]')
        t.sendline('line vty 0 4')
        t.expect('[>#]')
        t.sendline('login local')
        t.expect('[>#]')
        t.sendline('transport input ssh telnet')
        t.expect('[>#]')
        t.sendline('ip domain-name py.hi')
        t.expect('[>#]')
        t.sendline('crypto key generate rsa modulus 2048')
        t.expect('[>#]')
        t.sendline('end')
        t.expect('[>#]')
        t.sendline('wr')
        t.expect('[>#]')

provision(devices, ids)
