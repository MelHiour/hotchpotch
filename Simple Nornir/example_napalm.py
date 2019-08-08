from nornir import InitNornir
from nornir.plugins.tasks import networking, text
from nornir.plugins.functions.text import print_result
from pprint import pprint

nr = InitNornir(config_file="config.yaml",
#                logging={"file": "mylogs", "level": "debug"}       # <- uncomment for debug
                )
routers = nr.filter()
result = routers.run(task=networking.napalm_get, getters=["facts"])

# Just printing it
# print_result(result)

# Iterate and create a dictionary from print_result
result_dict = {}
for item, value in result.items():
    result_dict[item] = value.result['facts']

pprint(result_dict)
