import re
import yaml
import pprint
import sqlite3
import routeros

def cisco_parce(cisco_info, command, no_pager, type_command):
    import netmiko
    from netmiko import ConnectHandler

    try:
    # Подключение к удаленному оборудованию
        with ConnectHandler(**cisco_info) as ssh:
            # Переход в привелегилированный режим
            ssh.enable()
            if no_pager:
                ssh.send_config_set("no pager")

            # Удаленное выполнения команды
            if type_command:
                # Конфигурируем устройство
                print("Конфигурируем устройство...")
                result = ssh.send_config_set(command)
#                result = ssh.send_config_from_file("command_set.txt")
                result += "\n"
                result += ssh.send_command("write memory")
            else:
                # производим запрос конфигурации
                print("Производим запрос конфигурации...")
                result = ssh.send_command(command)

            if no_pager:
                ssh.send_config_set("pager lines 24")
            # Выход из привелегилированного режима
            ssh.exit_enable_mode()

            # Возврат результата
            return result
    except (NetmikoTimeoutException, NetmikoAuthenticationException, netmiko.exceptions.ReadTimeout) as error:
        print(error)

if __name__ == '__main__':
    cisco_router_d = dict()
    no_pager = 0    # флаг ставиться в 1 если нужно убрать постраничное отображения файла конфигурации
    type_command = 0 # флаг типа запроса: 0 - чтение конфигурации; 1 - конфигурирование устройства

    print('=== Обрабатываем оборудование Cisco...')
    # Подтягиваем учетные данные из внешней базы (пока будет файл cisco_base.yaml, формат обмена YAML)
    with open("sve_cisco_base_2023.09.12.yaml", 'r') as yaml_base:
        cisco_router_d = yaml.safe_load(yaml_base)

        for cisco_router in cisco_router_d:
            filename = cisco_router + "_2023.09.12_result.txt"
            command = 'show running-config'
#            command = ['object network SERVERS-FILIAL',
#                       'subnet 10.166.9.128 255.255.255.128']
            print("--> Обрабатывается: " + cisco_router)

            no_pager = 1
            type_command = 0 # флаг типа запроса: 0 - чтение конфигурации; 1 - конфигурирование устройства

            with open(filename, 'w') as f:
                f.write(cisco_parce(cisco_router_d[cisco_router], command, no_pager, type_command))
                f.close()

