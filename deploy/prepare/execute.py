import argparse
import os

from deploy.config.network import NetworkConfig

KOLLA_CONF_PATH = '/etc/kolla/config'


def _make_dirs(path):
    if not os.path.isdir(path):
        os.makedirs(path, mode=0644)


def _write_conf_file(conf_file, conf):
    with open(conf_file, 'w') as f:
        f.write(conf)
        f.close()


def _config_service(service, subs):
    def _wrap(func):
        def _config(*args):
            conf_path = os.path.join(KOLLA_CONF_PATH, service)
            _make_dirs(conf_path)
            for sub in subs:
                conf_file = os.path.join(conf_path,
                                         '{}-{}.conf'.format(service, sub))
                _write_conf_file(conf_file, func(*args))
        return _config
    return _wrap


@_config_service('nova', ['api'])
def _set_default_floating_pool(network_file):
    xnet = NetworkConfig(network_file=network_file).external_network
    return '[DEFAULT]\n' \
           'default_floating_pool = {}\n'.format(xnet['network_name'])


@_config_service('heat', ['api', 'engine'])
def _set_trusts_auth():
    return '[DEFAULT]\n' \
           'deferred_auth_method = trusts\n' \
           'trusts_delegated_roles =\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-nw', '--network-file',
                        type=str,
                        required=True,
                        help='network configuration file')
    args = parser.parse_args()
    _set_default_floating_pool(args.network_file)
    _set_trusts_auth()


if __name__ == '__main__':
    main()
