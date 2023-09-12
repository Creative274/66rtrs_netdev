create table if not exists dhcp (
    id          integer not NULL primary key,
    mac         text,
    ip          text,
    vlan        text,
    full_name   text
);