from __future__ import absolute_import
from __future__ import unicode_literals
from testinfra.utils.ansible_runner import AnsibleRunner
import os
import pytest
import logging
import testinfra.utils.ansible_runner
import collections


logging.basicConfig(level=logging.DEBUG)
# # DEFAULT_HOST = 'all'
VAR_FILE = "../../vars/main.yml"
DEFAULT_FILE = "../../defaults/main.yml"

TESTINFRA_HOSTS = testinfra.utils.ansible_runner.AnsibleRunner(
        os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')
inventory = os.environ['MOLECULE_INVENTORY_FILE']
runner = AnsibleRunner(inventory)
# runner.get_hosts(DEFAULT_HOST)


@pytest.fixture()
def ansible_os_family(Ansible):
    return Ansible("setup")["ansible_facts"]["ansible_os_family"]


@pytest.fixture
def ansible_variables(host, ansible_os_family):
    variables = runner.run(
        TESTINFRA_HOSTS,
        'include_vars',
        VAR_FILE
    )
    return variables['ansible_facts']


@pytest.fixture
def ansible_defaults(host, ansible_os_family):
    variables = runner.run(
        TESTINFRA_HOSTS,
        'include_vars',
        DEFAULT_FILE
    )
    return variables['ansible_facts']


@pytest.fixture
def ansible_group_variables(host, ansible_os_family):
    if ansible_os_family == "Debian":
        vars_file = "../../vars/debian.yml"
    elif ansible_os_family == "Archlinux":
        vars_file = "../../vars/archlinux.yml"
    else:
        raise ValueError("Unsupported distribution: " + ansible_os_family)

    vars = runner.run(
        TESTINFRA_HOSTS,
        "include_vars",
        vars_file
    )
    return vars["ansible_facts"]


def converttostr(data):
    if isinstance(data, str):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(list(map(converttostr, iter(data.items()))))
    elif isinstance(data, collections.Iterable):
        return type(data)(list(map(converttostr, data)))
    else:
        return data


def test_binary_link(host, ansible_defaults):
    dict_defaults = converttostr(ansible_defaults)
    myversion = dict_defaults['circleci_version']
    myplatform = dict_defaults['circleci_platform']
    myfile = '/usr/local/bin/circleci'

    assert host.file(myfile).exists
    assert host.file(myfile).is_symlink
    assert host.file(myfile).linked_to == \
        '/opt/circleci/circleci-'+myversion+'/circleci-cli_'+myversion+'_linux_'+myplatform+'/circleci'
