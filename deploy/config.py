#last updated: 11-02-2023

import tasks
import settings
from pprint import pprint

def cfg_system(router, router_info, cmd, configs):
    command_list = []
    print(tasks.notify('APPLYING [{}] CONFIGURATION ON [{}]'.format(cmd.upper(), router.upper()), align='>'))
    command_list.append(['system', 'host-name',configs['system']['host-name']])
    login_user =  getattr(settings, router_info['login_user'])
    login_pwd =  getattr(settings, router_info['login_password'])
    command_list.append(['system', 'login', 'user', login_user, 'authentication', 'plaintext-password', login_pwd])
    print(tasks.notify('[System configuration]', align='-'))
    tasks.apply(router_info['address'], router_info['port'], command_list, router_info['key_name'])
    command_list.clear()    

def cfg_intefaces(router, router_info, cmd, configuration):
    command_list = []
    print(tasks.notify('APPLYING [{}] CONFIGURATION ON [{}]'.format(cmd.upper(), router.upper()), align='>'))
    for ethernet in configuration['ethernet']:
        command_list.append(['interfaces','ethernet', ethernet['name'] , 'address' , ethernet['address']])
        command_list.append(['interfaces','ethernet', ethernet['name'] , 'description' , ethernet['description']])
        
    print(tasks.notify('[Ethernet configuration]', align='-'))
    tasks.apply(router_info['address'], router_info['port'], command_list, router_info['key_name'])
    command_list.clear()

    if 'vxlan' in configuration:
        for vxlan in configuration['vxlan']:
            command_list.append(['interfaces','vxlan', vxlan['name'] , 'address' , vxlan['address']])
            # command_list.append(['interfaces','vxlan', vxlan['name'] , 'address' , vxlan['address_v6']])
            command_list.append(['interfaces','vxlan', vxlan['name'] , 'description' , vxlan['description']])
            command_list.append(['interfaces','vxlan', vxlan['name'] , 'port' , vxlan['port']])
            # command_list.append(['interfaces','vxlan', vxlan['name'] , 'source-interface' , vxlan['source-interface']])
            command_list.append(['interfaces','vxlan', vxlan['name'] , 'vni' , vxlan['vni']])
            # command_list.append(['interfaces','vxlan', vxlan['name'] , 'group' , vxlan['group']])
            command_list.append(['interfaces','vxlan', vxlan['name'] , 'remote' , vxlan['remote']])

        print(tasks.notify('[VXLAN configuration]', align='-'))
        tasks.apply(router_info['address'], router_info['port'], command_list, router_info['key_name'])
        command_list.clear()  

def cfg_nat(router, router_info, cmd, configuration):
    command_list = []
    print(tasks.notify('APPLYING [{}] CONFIGURATION ON [{}]'.format(cmd.upper(), router.upper()), align='>'))
    for rule in configuration['source']['rules']:         
        command_list.append(['nat', 'source', 'rule', rule['rule_id'], 'source', 'address', rule['source']])      
        command_list.append(['nat', 'source', 'rule', rule['rule_id'], 'outbound-interface', rule['outbound-interface']])
        
        if 'destination' in rule:          
            command_list.append(['nat', 'source', 'rule', rule['rule_id'], 'destination', 'address', rule['destination']])
            
        if 'exclude' in rule:
            command_list.append(['nat', 'source', 'rule', rule['rule_id'], 'exclude'])

        if "translation" in rule:
            command_list.append(['nat', 'source', 'rule', rule['rule_id'], 'translation', 'address', rule['translation']])

        print(tasks.notify('[NAT source rule id ['+ rule['rule_id'] + '] configuration result]' , align='-'))
        
        tasks.apply(router_info['address'], router_info['port'], command_list, router_info['key_name'])
        command_list.clear()

def cfg_firewall(router, router_info, cmd, configuration):
    command_list = []
    print(tasks.notify('APPLYING [{}] CONFIGURATION ON [{}]'.format(cmd.upper(), router.upper()), align='>'))
    
    if 'network-groups' in configuration:
        for network_group in configuration['network-groups']:
            for network in network_group['network']:
                command_list.append(['firewall', 'group', 'network-group', network_group['name'], 'network', network])
        print(tasks.notify('Creating firewall network group["{}"]'.format(network_group['name'].upper()) , align='-'))
        tasks.apply(router_info['address'], router_info['port'], command_list, router_info['key_name'])
        command_list.clear()
                
    if 'interface' in configuration:
        for interface in configuration['interface']:
            for rule in configuration['rules']:
                if rule['name'] == interface['in_name']:
                    command_list.append(['firewall', 'name', rule['name'], 'default-action', rule['default-action']])
                    command_list.append(['firewall', 'name', rule['name'], 'rule', rule['rule_id'], 'action', rule['action']])
                    command_list.append(['firewall', 'name', rule['name'], 'rule', rule['rule_id'], 'destination', 'address', rule['destination']])
                    command_list.append(['firewall', 'name', rule['name'], 'rule', rule['rule_id'], 'source', 'address', rule['source']])
                    command_list.append(['interfaces', 'ethernet', interface['name'], 'firewall', 'in', 'name', rule['name']])

                    print(tasks.notify('[Firewall configuration - Rule name "{}"]'.format(rule['name'].upper()) , align='-'))
                    tasks.apply(router_info['address'], router_info['port'], command_list, router_info['key_name'])
                    command_list.clear()
                
                if rule['name'] == interface['out_name']:
                    command_list.append(['firewall', 'name', rule['name'], 'default-action', rule['default-action']])
                    command_list.append(['firewall', 'name', rule['name'], 'rule', rule['rule_id'], 'action', rule['action']])
                    command_list.append(['firewall', 'name', rule['name'], 'rule', rule['rule_id'],  
                                            'source', 'group', 'network-group', rule['source']['network-group']])
                    command_list.append(['interfaces', 'ethernet', interface['name'], 'firewall', 'out', 'name', rule['name']])

                    print(tasks.notify('[Firewall configuration - Rule name "{}"]'.format(rule['name'].upper()) , align='-'))
                    tasks.apply(router_info['address'], router_info['port'], command_list, router_info['key_name'])
                    command_list.clear()

def cfg_protocols(router, router_info, cmd, configuration):
    command_list = []
    print(tasks.notify('APPLYING [{}] CONFIGURATION ON [{}]'.format(cmd.upper(), router.upper()), align='>'))
    for route in configuration['static']['route']:
        command_list.append(['protocols','static','route', route['network'], 'next-hop', route['next-hop']])

    print(tasks.notify('[Protocols configuration]', align='-'))
    tasks.apply(router_info['address'], router_info['port'], command_list, router_info['key_name'])

def cfg_vpn(router, router_info, cmd, configuration):
    command_list = []
    print(tasks.notify('APPLYING [{}] CONFIGURATION ON [{}]'.format(cmd.upper(), router.upper()), align='>'))

    for config in configuration['ipsec']['esp-group']:
        command_list.append(['vpn', 'ipsec', 'esp-group', config['name'], 'compression', config['compression']])
        command_list.append(['vpn', 'ipsec', 'esp-group', config['name'], 'lifetime', config['lifetime']])
        command_list.append(['vpn', 'ipsec', 'esp-group', config['name'], 'mode', config['mode']])
        command_list.append(['vpn', 'ipsec', 'esp-group', config['name'], 'pfs', config['pfs']])
        command_list.append(['vpn', 'ipsec', 'esp-group', config['name'], 'proposal', config['proposal_id'], 'encryption', config['encryption']])
        command_list.append(['vpn', 'ipsec', 'esp-group', config['name'], 'proposal', config['proposal_id'], 'hash', config['hash']])
    
    print(tasks.notify('[VPN ipsec [esp-group] configuration]' , align='-'))

    tasks.apply(router_info['address'], router_info['port'], command_list, router_info['key_name'])
    command_list.clear()

    for config in configuration['ipsec']['ike-group']:
        command_list.append(['vpn', 'ipsec', 'ike-group', config['name'], 'ikev2-reauth', config['ikev2-reauth']])
        command_list.append(['vpn', 'ipsec', 'ike-group', config['name'], 'key-exchange', config['key-exchange']])
        command_list.append(['vpn', 'ipsec', 'ike-group', config['name'], 'lifetime', config['lifetime']])
        command_list.append(['vpn', 'ipsec', 'ike-group', config['name'], 'proposal', config['proposal_id'], 'encryption', config['encryption']])
        command_list.append(['vpn', 'ipsec', 'ike-group', config['name'], 'proposal', config['proposal_id'], 'hash', config['hash']])
    
    print(tasks.notify('[VPN ipsec [ike-group] configuration]' , align='-'))
            
    tasks.apply(router_info['address'], router_info['port'], command_list, router_info['key_name'])
    command_list.clear()

    for peer in configuration['ipsec']['site-to-site']['peer']:
        command_list.append(['vpn', 'ipsec', 'site-to-site', 'peer', peer['name'], 'authentication', 'mode', peer['authentication']['mode']])
        command_list.append(['vpn', 'ipsec', 'site-to-site', 'peer', peer['name'], 'authentication', 'pre-shared-secret', peer['authentication']['pre-shared-secret']])
        command_list.append(['vpn', 'ipsec', 'site-to-site', 'peer', peer['name'], 'ike-group', peer['ike-group']])
        command_list.append(['vpn', 'ipsec', 'site-to-site', 'peer', peer['name'], 'local-address', peer['local-address']])
        # command_list.append(['vpn', 'ipsec', 'site-to-site', 'peer', peer['name'], 'remote-address', peer['remote-address']])
        command_list.append(['vpn', 'ipsec', 'site-to-site', 'peer', peer['name'], 'ike-group', peer['ike-group']])
        
        for tunnel in peer['tunnel']:
            command_list.append(['vpn', 'ipsec', 'site-to-site', 'peer', peer['name'], 'tunnel', tunnel['tunnel_id'], 'esp-group', tunnel['esp-group']])
            command_list.append(['vpn', 'ipsec', 'site-to-site', 'peer', peer['name'], 'tunnel', tunnel['tunnel_id'], 'local','prefix', tunnel['local-prefix']])
            command_list.append(['vpn', 'ipsec', 'site-to-site', 'peer', peer['name'], 'tunnel', tunnel['tunnel_id'], 'remote','prefix', tunnel['remote-prefix']])
        
        command_list.append(['vpn', 'ipsec', 'ipsec-interfaces', 'interface', configuration['ipsec']['interface']])

    print(tasks.notify('[VPN ipsec [site-to-site] configuration]' , align='-'))

    tasks.apply(router_info['address'], router_info['port'], command_list, router_info['key_name'])
    command_list.clear()



