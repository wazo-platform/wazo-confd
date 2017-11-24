# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import inspect

from functools import wraps


class IsolatedAction(object):
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

    def __call__(self, func):
        # This function is called when using the IsolatedAction as a decorator

        if inspect.isgeneratorfunction(func):
            # This is a hack in order to make sure
            # that test generators still work with nosetest.
            # A function must have a "yield" inside the function body
            # so that nose can see the test function as a generator.
            # Therefore, we decorate by using a function that
            # will also appear as a generator
            @wraps(func)
            def generator_decorated(*args, **kwargs):
                resource = self.__enter__()
                # Pass the resource as an argument to the test function
                new_args = list(args) + [resource]
                for result in func(*new_args, **kwargs):
                    yield result
                self.__exit__()
            return generator_decorated
        else:
            @wraps(func)
            def decorated(*args, **kwargs):
                resource = self.__enter__()
                # Pass the resource as an argument to the test function
                new_args = list(args) + [resource]
                result = func(*new_args, **kwargs)
                self.__exit__()
                return result
            return decorated

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
