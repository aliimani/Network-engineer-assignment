#last updated: 12-02-2023 01:30am
from pprint import pprint
import tasks
import config

ROUTERS_ROOT= "./routers/"
ROUTER_VARS_ROOT= "./router_vars/"

def configure():
  routers = tasks.parse_yaml(ROUTERS_ROOT + "routers.yml")
  for router, router_info in routers.items():
    print(tasks.notify('\033[45m Starting "{} \033[m"'.format(router.upper())))
    configs = tasks.parse_yaml(ROUTER_VARS_ROOT + router + ".yml") 
    for cmd, configuration in configs.items():
      command_list = []
      match cmd:
        case "system":
            config.cfg_system(router, router_info, cmd, configs)
        case "interfaces":
            config.cfg_intefaces(router, router_info, cmd, configuration)    
        case "protocols":
            config.cfg_protocols(router, router_info, cmd, configuration)
        case "nat":
            config.cfg_nat(router, router_info, cmd, configuration)
        case "vpn":
            config.cfg_vpn(router, router_info, cmd, configuration)
        case "firewall":
            config.cfg_firewall(router, router_info, cmd, configuration)
        case _:
            print(tasks.notify('APPLYING "{}" CONFIGURATION'.format(cmd.upper()), align='>'))
            print("\033[31m WARNING: there is no configuration for the [" + cmd + "] section \033[m")     

    print(tasks.notify('\033[32mSAVING CONFIGURATION ON [{}]\033[m'.format(cmd.upper(), router.upper())))
    result = tasks.save_config(
        router_info['address'], router_info['port'], router_info['key_name'])
    print(tasks.show_result('Save config', result))


if __name__ == '__main__':
    configure()
