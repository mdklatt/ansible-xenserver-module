""" The xen_instance_facts Ansible module.

This module will return metadata from a XenServer host. See the DOCUMENTATION
and EXAMPLES strings below for more information.

"""
# Ansible modules do not use the normal Python import machinery, so all imports
# must be absolute. Even then, there does not seem to be any way to import
# local libraries for sharing code within a project.
# <http://docs.ansible.com/ansible/latest/dev_guide/developing_modules.html>

from ansible.module_utils.basic import AnsibleModule
from contextlib import contextmanager
from datetime import datetime
from XenAPI import Session


__all__ = "main",


ANSIBLE_METADATA = {
    "metadata_version": "1.0",
    "status": "preview",
    "supported_by": "committer",
}


DOCUMENTATION = """
module: xen 
short_description: Gather facts about XenServer entities.
description: |
  Gather facts about XenServer entities.
requirements:
  - XenAPI (1.2+)
notes:
  - U(https://github.com/mdklatt/ansible-xenserver-module)
version_added: "2.2"
author: Michael Klatt
options:
  host:
    description: XenServer host URL.
    required: true
  username:
    description: XenServer root user.
    required: false
    default: root
  password:
    description: XenServer root password.
    required: true
"""  # must be valid YAML


EXAMPLES = """
- xen_instance_facts:
    host: http://123.45.67.89
    username: root
    password: abc123
"""  # plain text


_ARGS_SPEC = {
    "host": {
        "type": "str", 
        "required": True
    },
    "username": {
        "type": "str",
        "default": "root",
    },
    "password": {
        "type": "str",
        "required": True
    },
}


def main():
    """ Execute the module.

    """
    module = AnsibleModule(_ARGS_SPEC, supports_check_mode=False)
    module.log("connecting to {:s}".format(module.params["host"]))
    with _connect(module.params) as xen:
        instances = xen.VM.get_all_records().values()
    timefmt = "%Y%m%dT%H:%M:%SZ"
    for instance in instances:
        for key, obj in instance.iteritems():
            # TODO: Implement filtering.
            if obj.__class__.__name__ == "DateTime":
                # Replace an xmlrpclib.DateTime with a regular datetime.
                # This is an old-style class, so normal type checking can't be
                # used.
                instance[key] = datetime.strptime(obj.value, timefmt)
    module.exit_json(changed=False, instances=instances)  # calls exit(0)


@contextmanager
def _connect(params):
    """ Context manager for a XenAPI session.

    """
    # Even though all modules in this project need this function, it cannot be
    # put into a local library (see comments at top).
    session = Session(params["host"])
    username = params["username"]
    password = params["password"]
    session.login_with_password(username, password, "1.0", "ansible-xenserver")
    try:
        yield session.xenapi
    finally:
        session.xenapi.session.logout()
    return


# Make the module executable.

if __name__ == "__main__":
    main()  # calls exit()