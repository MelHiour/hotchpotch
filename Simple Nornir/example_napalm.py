from nornir import InitNornir
from nornir.plugins.tasks import networking
from nornir.plugins.functions.text import print_result

nr = InitNornir(config_file="config.yaml", logging={"file": "mylogs", "level": "debug"})
routers = nr.filter()
result = routers.run(task=networking.napalm_get, getters=["facts"])
print_result(result)
