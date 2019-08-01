# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class IsolatedAction:
    """
    Utility for automatically creating and deleting
    a resource needed by a test. Can be used for managing test
    dependencies. An IsolatedAction can be used both as a decorator
    or a context manager. When used as a decorator, the resource
    will be passed as an argument to the test function and deleted
    once the function has completed. As a context manager,
    the resource will be passed as the context resource, and deleted
    once the context scope exits.

    Usage: inherit this class and override the following fields:
      - id_field (default is 'id')
      - actions

    Code example:

        def create_user(**parameters):
            pass

        def delete_user(user):
            pass

        class user_fixture(IsolatedAction):

            actions = {'generate': create_user,
                       'delete': delete_user}


        @user_fixture()
        def test_using_decorator(user):
            assert user['id'] is not None

        def test_using_context_manager():
            with user_fixture() as user:
                assert user['id'] is not None
    """

    actions = {}
    id_field = 'id'

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        # This function is called when using the IsolatedAction as a
        # context manager, it is also reused by the decorator for creating
        # resources
        callback = self.actions['generate']
        self.resource = callback(*self.args, **self.kwargs)
        return self.resource

    def __exit__(self, *args):
        # This function is called when exiting a context manager. It is also
        # reused by the decorator for deleting resources
        callback = self.actions.get('delete')
        if callback:
            callback(self.resource[self.id_field], check=False)
