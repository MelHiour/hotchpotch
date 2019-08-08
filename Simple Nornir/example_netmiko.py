from nornir import InitNornir
from nornir.plugins.tasks import networking
from nornir.plugins.functions.text import print_result

nr = InitNornir(config_file="config.yaml", logging={"file": "mylogs", "level": "debug"})
routers = nr.filter()
result = routers.run(task=networking.netmiko_send_command, command_string="sh ip int br")
print_result(result)
