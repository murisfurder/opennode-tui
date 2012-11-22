import os
import yaml

from opennode.cli.actions.utils import execute2
from opennode.cli import config


def get_oms_server():
    """Read OMS server port and address from the configuration file"""
    minion_conf_file = config.c('salt', 'minion-conf')
    with open(minion_conf_file, 'r') as minion_conf:
        minion_config = yaml.safe_load(minion_conf.read())
        oms_server = minion_config.get('master', 'localhost')
        oms_server_port = minion_config.get('master_port', 4506)
        return (oms_server, oms_server_port)


def set_oms_server(server, port=4506):
    """Write OMS server address and port to the configuration file"""
    minion_conf_file = config.c('salt', 'minion-conf')

    with open(minion_conf_file, 'r') as minion_conf:
        minion_config = yaml.safe_load(minion_conf.read())
        if minion_config.get('master', None):
            minion_config['master'] = server
        if minion_config.get('master_port', None):
            minion_config['master_port'] = port

    with open(minion_conf_file, 'w') as conf:
        yaml.dump(minion_config, conf, default_flow_style=False)


def register_oms_server(server, port):
    """Register with a new OMS server:port."""
    # cleanup of the previous func cert
    set_oms_server(server, port)
    execute2('service salt-minion restart')


## OMS VM specific ##
def configure_oms_vm(ctid, ipaddr):
    """Adjust configuration of the VM hosting OMS"""
    base = "/vz/private/%s/" % ctid
    # set a hostname to be used as a binding interface
    master_conf_file = config.c('salt', 'master-conf')
    master_conf_file = os.path.join([base, master_conf_file])

    with open(master_conf_file, 'r') as master_conf:
        master_config = yaml.safe_load(master_conf.read())
        if master_config.get('master', None):
            master_config['interface'] = ipaddr

    with open(master_conf_file, 'w') as conf:
        yaml.dump(master_config, conf, default_flow_style=False)
