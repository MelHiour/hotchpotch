import ipaddress as ipad
from nornir import InitNornir
from nornir.plugins.tasks.text import template_file
from nornir.plugins.tasks.networking import netmiko_send_config, netmiko_save_config, napalm_get
from nornir.plugins.functions.text import print_result

nr = InitNornir(config_file="config.yaml")

def ospf_enabled(host):
    return 'ospf' in host.data['services']

def configure_ospf(task):
    task.host['template_config'] = task.run(task=template_file, template='ospf_template.j2', path='templates')
    task.run(task=netmiko_send_config, config_commands=task.host['template_config'].result)
    task.run(task=netmiko_save_config)
    task.run(task=napalm_get, getters=['facts', 'get_interfaces_ip'])

routers = nr.filter(filter_func=ospf_enabled)
r = routers.run(configure_ospf)
print_result(r)
