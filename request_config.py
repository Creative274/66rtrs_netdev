import re
import yaml
import pprint
import sqlite3
import routeros

def cisco_parce(cisco_info, command):
    import netmiko
    from netmiko import ConnectHandler

    # Подключение к удаленному оборудованию
    telnet = ConnectHandler(**cisco_info)
    # Переход в привелегилированный режим
    telnet.enable()
    # Удаленное выполнения команды
    result = telnet.send_command(command)
    # Выход из привелегилированного режима
    telnet.exit_enable_mode()

    # Возврат результата
    return result

def mikrotik_parce(mikrotik_info, command):
    import netmiko
    from netmiko import ConnectHandler

    # Подключение к удаленному оборудованию
    sshCli = ConnectHandler(**mikrotik_info)
    if  sshCli:
        result = sshCli.send_command(command)
    else:
        result = "Connection Faild"

    # Возврат результата
    return result

if __name__ == '__main__':
    cisco_router_d = dict()

    oper_num = 2

    if oper_num==1:
        print('Обрабатываем оборудование Cisco...')
        # Подтягиваем учетные данные из внешней базы (пока будет файл cisco_base.yaml, формат обмена YAML)
        with open("cisco_tech_base_all.yaml", 'r') as yaml_base:
            cisco_router_d = yaml.safe_load(yaml_base)

            for cisco_router in cisco_router_d:
                filename = cisco_router + "_conf.txt"
                command = 'show running-config'
                with open(filename, 'w') as f:
                    f.write(cisco_parce(cisco_router_d[cisco_router], command))
                    f.close()

                filename = cisco_router + "_arp.txt"
                command = 'show mac address-table'
                with open(filename, 'w') as f:
                    f.write(cisco_parce(cisco_router_d[cisco_router], command))
                    f.close()

    if oper_num == 2:
        from netmiko import ConnectHandler
        print('Обрабатываем оборудование Mikrotik...')
        mikrotik_router_1 = {
            'device_type': 'mikrotik_routeros',
            'host': '10.174.10.25',
            'port': '22',
            'username': 'admin',
            'password': 'gtkbrfy'
        }

        command = "user add name=v  password=\"djc[jl19!\" disabled=no group=full"

        # Подключение к удаленному оборудованию
        sshCli = ConnectHandler(**mikrotik_router_1)
        output = sshCli.send_command(command, cmd_verify=True)
        print(output)
        sshCli.disconnect()


