# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os

from types import NoneType

from ansible.errors import AnsibleParserError
from ansible.parsing.yaml.objects import AnsibleBaseYAMLObject, AnsibleSequence


def load_list_of_blocks(ds, play, parent_block=None, role=None, task_include=None, use_handlers=False, variable_manager=None, loader=None):
    '''
    Given a list of mixed task/block data (parsed from YAML),
    return a list of Block() objects, where implicit blocks
    are created for each bare Task.
    '''
 
    # we import here to prevent a circular dependency with imports
    from ansible.playbook.block import Block

    if not isinstance(ds, (list, type(None))):
        raise AnsibleParserError('block has bad type: "%s". Expecting "list"' % type(ds).__name__, obj=ds)

    block_list = []
    if ds:
        for block in ds:
            b = Block.load(
                block,
                play=play,
                parent_block=parent_block,
                role=role,
                task_include=task_include,
                use_handlers=use_handlers,
                variable_manager=variable_manager,
                loader=loader
            )
            block_list.append(b)

    return block_list


def load_list_of_tasks(ds, play, block=None, role=None, task_include=None, use_handlers=False, variable_manager=None, loader=None):
    '''
    Given a list of task datastructures (parsed from YAML),
    return a list of Task() or TaskInclude() objects.
    '''

    # we import here to prevent a circular dependency with imports
    from ansible.playbook.block import Block
    from ansible.playbook.handler import Handler
    from ansible.playbook.task import Task

    if not isinstance(ds, list):
        raise AnsibleParserError('task has bad type: "%s". Expected "list"' % type(ds).__name__, obj=ds)

    task_list = []
    for task in ds:
        if not isinstance(task, dict):
            raise AnsibleParserError('task/handler has bad type: "%s". Expected "dict"' % type(task).__name__, obj=task)

        if 'block' in task:
            t = Block.load(
                task,
                play=play,
                parent_block=block,
                role=role,
                task_include=task_include,
                use_handlers=use_handlers,
                variable_manager=variable_manager,
                loader=loader,
            )
        else:
            if use_handlers:
                t = Handler.load(task, block=block, role=role, task_include=task_include, variable_manager=variable_manager, loader=loader)
            else:
                t = Task.load(task, block=block, role=role, task_include=task_include, variable_manager=variable_manager, loader=loader)

        task_list.append(t)

    return task_list


def load_list_of_roles(ds, current_role_path=None, variable_manager=None, loader=None):
    '''
    Loads and returns a list of RoleInclude objects from the datastructure
    list of role definitions
    '''

    # we import here to prevent a circular dependency with imports
    from ansible.playbook.role.include import RoleInclude

    if not isinstance(ds, list):
        raise AnsibleParserError('roles has bad type: "%s". Expectes "list"' % type(ds).__name__, obj=ds)

    roles = []
    for role_def in ds:
        i = RoleInclude.load(role_def, current_role_path=current_role_path, variable_manager=variable_manager, loader=loader)
        roles.append(i)

    return roles

