from napalm import get_network_driver

def show_interfaces(ip, driver='ios', username='melhiour', password='melhiour'):
    driver = get_network_driver(driver)
    device = driver(ip, username, password)
    device.open()
    result = device.get_interfaces()
    device.close()
    return result

def show_sys(ip, driver='ios', username='melhiour', password='melhiour'):
    driver = get_network_driver(driver)
    device = driver(ip, username, password)
    device.open()
    result = device.get_facts()
    device.close()
    return result

def interface_oper(ip, interface_name, operation, driver='ios', username='melhiour', password='melhiour'):
    if operation == 'down':
        snippet = f'interface {interface_name}\nshutdown'
    elif operation == 'up':
        snippet = f'interface {interface_name}\nno shutdown'
    else:
        return 'Please use up or down operation'
    driver = get_network_driver(driver)
    device = driver(ip, username, password)
    device.open()
    device.load_merge_candidate(config=snippet)
    diff = device.compare_config()
    device.commit_config()
    device.close()
    return diff

if __name__ == '__main__':
    result = interface_oper('192.168.30.11', 'Ethernet0/1', 'down')
    print(result)
