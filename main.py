import re
import yaml
import pprint
import sqlite3

# {10.174.20.120+, 10.174.20.150+, 10.174.20.111+, 10.174.20.112+, 10.174.20.103+,
# 10.174.20.102+, 10.174.20.101+, 10.174.20.100+, 10.174.20.113+, 10.174.20.107+}
#
#
#
# show configuration
# show arp
# show interfaces status - просмотр типа порта
# show vlan brief - описание вланов
# show mac address-table - запрос таблицы мак-адресов
# show cdp neighbors - список соседей
#

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

def parce_dhcp_log(dhcp_log):
    print(dhcp_log)



if __name__ == '__main__':
    cisco_router_d = dict()

    # work_ident - указывает, какие будут произведены манипуляции.
    # 1 - работа с удаленным оборудованием
    # 2 - парсинг файла DHCP-сервера
    work_ident = 1

    if work_ident == 1:
        # Подготовка базы данных
        db_name = 'dhcp_snooping.db'
        conn = sqlite3.connect(db_name)
        print('Подключение схемы БД')
        with open('dhcp_snooping_schema.sql', 'r') as f:
            schema = f.read()
            conn.executescript(schema)
        print("Создание схемы БД завершено")

        cisco_router = {
            'device_type': 'cisco_ios',
            'host': '10.174.10.174',
            'username': 'velin',
            'password': 'ranger1818',
            'secret': 'xtndthuitcnjt',
        }

#        print('Добавление данных в базу...')
#        # Подтягиваем учетные данные из внешней базы (пока будет файл cisco_base.yaml, формат обмена YAML)
#        with open("cisco_base.yaml", 'r') as yaml_base:
#            cisco_router_d = yaml.safe_load(yaml_base)

#        for cisco_router in cisco_router_d:
#            filename = cisco_router + "_arp.txt"
#            command = 'show arp'
#            with open(filename, 'w') as f:
#                f.write(cisco_parce(cisco_router_d[cisco_router], command))
#                f.close()

        # Парсер лога arp-ответа от Cisco
        raw_parce_arp = r'^\S+\s+(?P<ip_addr>[\d+.]+)\s+\S+\s+(?P<mac_addr>[0-9A-Fa-f.]{4}.[0-9A-Fa-f]{4}.[0-9A-Fa-f]{4})\s+\S+\s+(?P<vlan>\S+)'

        # Парсер экспорта базы dhcp-сервера Windows
        raw_parce_dhcp_win = r'^\[(?P<ip_addr>\S+)\]\s(?P<full_name>\S+)'

        command = 'show arp'
        filename = 'c892_arp.txt'
        with open(filename, 'w') as f:
            result_arp = cisco_parce(cisco_router, command)
            f.write(result_arp)
            f.close()

        for line in result_arp.split('\n'):
            match = re.search(raw_parce_arp, line)
            if match:
                ip_addr, mac_addr, vlan = match.group('ip_addr', 'mac_addr', 'vlan')

        filename = 'dhcp_2021.11.08.txt'
        with open(filename) as f:
            for line in f:
                result = re.match(raw_str, line)
                if result:
                    ip_addr, full_name = result.group('ip_addr', 'full_name')
                    # print(ip_addr, "->", full_name)
                    row = (ip_addr, full_name)
                    # print(row)
                    with conn:
                        query = '''INSERT INTO dhcp (ip, full_name)
                                           VALUES (?, ?)'''
                    conn.execute(query, row)
        conn.close()

    if work_ident == 2:
        # Парсинг логов фиксации IP-адресов
        raw_str = r'^\[(?P<ip_addr>\S+)\]\s(?P<full_name>\S+)'

        print("Запущена операция парсинга логов DHCP-сервера")
        filename = 'dhcp_2021.11.08.txt'
        with open(filename) as f:
            for line in f:
                result = re.match(raw_str, line)
                if result:
                    ip_addr, full_name = result.group('ip_addr', 'full_name')
                    print(ip_addr, "->", full_name)