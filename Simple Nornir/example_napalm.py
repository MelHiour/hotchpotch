from nornir import InitNornir
from nornir.plugins.tasks import networking, text
from nornir.plugins.functions.text import print_result
from pprint import pprint

nr = InitNornir(config_file="config.yaml",
#                logging={"file": "mylogs", "level": "debug"}       # <- uncomment for debug
                )

routers = nr.filter()

routers_facts = routers.run(task=networking.napalm_get, getters=["facts"])

routers_facts_dict = {}
for item, value in routers_facts.items():
    routers_facts_dict[item] = value.result['facts']

pprint(routers_facts_dict)

lldp_table_facts = routers.run(task=networking.napalm_get, getters=["get_lldp_neighbors"])

lldp_table_dict = {}
for item, value in lldp_table.items():
    lldp_table_dict[item] = value.result['facts']

pprint(lldp_table_dict)
