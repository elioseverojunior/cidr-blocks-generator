#!/usr/bin/env python3
import sys
from pathlib import Path

from ruamel import yaml


class YAML(yaml.YAML):
    def __init__(self):
        yaml.YAML.__init__(self)
        self.preserve_quotes = True
        self.indent(mapping=4, sequence=4, offset=2)
        self.version = (1, 2)


def split_cidr_block(cidr_block_data):
    str_cidr_block = str(cidr_block_data)
    if '/' in str_cidr_block:
        cidr_block_split = str_cidr_block.split('/')[0].split('.')
    else:
        cidr_block_split = str_cidr_block.split('.')
    first_zero_index = len(cidr_block_split) - cidr_block_split[::-1].index('0') - 1
    return first_zero_index, cidr_block_split


if __name__ == '__main__':
    yml = YAML()
    yaml_config = Path('./cidr_blocks.yaml')
    cidr_blocks = yml.load(yaml_config)

    subnets = {}
    default_cidr_block_config = '{}/{}'.format(cidr_blocks['cidr_block'], cidr_blocks['network']['subnet_mask_bits'])
    first_zero_subnet_index, cidr_block_list = split_cidr_block(default_cidr_block_config)
    index = first_zero_subnet_index - 1
    subnet_id = subnet_range = 1
    subnet_mask_bits = cidr_blocks['network']['subnet_mask_bits']
    cidr_block_environments_map = {}
    quantity_subnets = len(cidr_blocks['availability_zones'])
    azs = {}

    for az in cidr_blocks['availability_zones']:
        azs.update({'{}{}'.format(cidr_blocks['region'], az): ''})
        print(azs)

    for environment in cidr_blocks['environments']:
        cidr_block_environments_map.update({environment: {}})
        for subnet in cidr_blocks['network']['subnets']:
            subnet_name = '{}_subnet'.format(subnet['name'])
            subnet.update({'azs': azs})
            subnet_id = subnet_range
            subnet_range = (subnet_id + quantity_subnets)
            subnets = {
                subnet_name: {
                    'network_cidr_blocks': {},
                    'network_mask_bit_init': subnet_id,
                    'network_mask_bit_end': subnet_range - 1,
                }
            }

            for az in azs:
                cidr_block_list[index] = str(subnet_id)
                subnet_mask_bits = cidr_blocks['network'].get('subnet_mask_bits')
                if subnet.get('subnet_mask_bits'):
                    subnet_mask_bits = subnet.get('subnet_mask_bits')
                cidr_block = '{}/{}'.format('.'.join(cidr_block_list), subnet_mask_bits)
                subnets[subnet_name]['network_cidr_blocks'].update({az: cidr_block})
                subnet_id += 1
            cidr_block_environments_map[environment].update(subnets)

    yml.dump(cidr_block_environments_map, sys.stdout)
    with open('network_cidr_block_configuration.yaml', 'w') as f:
        yaml.dump(cidr_block_environments_map, f)
