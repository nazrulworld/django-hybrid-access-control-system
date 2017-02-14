# -*- coding: utf-8 -*-
# ++ This file `test_decorators.py` is generated at 2/14/17 6:23 AM ++
from mock import Mock
from django.test import TestCase, RequestFactory
from hacs.decorators import permission_required
from .path import FIXTURE_PATH
from tests.fixture import model_fixture
from hacs.globals import HACS_ACCESS_CONTROL_LOCAL
from hacs.security.helpers import ANONYMOUS_USER, HACS_PORTAL_MANAGER_PERMISSION
from django.core.exceptions import PermissionDenied

__author__ = 'Md Nazrul Islam<connect2nazrul@gmail.com>'


class TestDecorators(TestCase):
    """"""
    fixtures = (FIXTURE_PATH / "testing_fixture.json",)

    def test_permission_required(self):
        """
        :return:
        """
        HACS_ACCESS_CONTROL_LOCAL.current_user = ANONYMOUS_USER
        # http://stackoverflow.com/questions/2738641/testing-python-decorators
        func = Mock()
        # decorated_view = permission_required('hacs.PublicView')(func)
        request_factory = RequestFactory()
        request = request_factory.request()
        request.user = ANONYMOUS_USER

        decorated_view = permission_required('hacs.PublicView')(func)
        decorated_view(request)

        self.assertTrue(func.called)
        self.assertEqual(1, func.call_count)

        func = Mock()
        decorated_view = permission_required('hacs.AuthenticatedView')(func)
        try:
            decorated_view(request)
            raise AssertionError("Code should not come here! As Anonymous User Has no permission to view")
        except PermissionDenied:
            pass

        # View Function is not called because exception
        self.assertFalse(func.called)

        request.user = model_fixture.memberuser
        HACS_ACCESS_CONTROL_LOCAL.current_user = request.user

        decorated_view(request)

        # Now Member User should have access
        self.assertTrue(func.called)

        func = Mock()
        decorated_view = permission_required('hacs.ManageContent')(func)
        try:
            decorated_view(request)
            raise AssertionError("Code should not come here! As Member User Has no permission to view")
        except PermissionDenied:
            pass

        # View Function is not called because exception
        self.assertFalse(func.called)

        request.user = model_fixture.contributoruser
        HACS_ACCESS_CONTROL_LOCAL.current_user = request.user

        try:
            decorated_view(request)
            raise AssertionError("Code should not come here! Even Contributor User Has no permission to view")
        except PermissionDenied:
            pass

        # View Function is not called because exception
        self.assertFalse(func.called)

        request.user = model_fixture.editoruser
        HACS_ACCESS_CONTROL_LOCAL.current_user = request.user

        decorated_view(request)
        # Editor Has Permission
        self.assertTrue(func.called)

        func = Mock()
        decorated_view = permission_required(HACS_PORTAL_MANAGER_PERMISSION)(func)
        try:
            decorated_view(request)
            raise AssertionError("Code should not come here! As Editor User Has no permission to view")
        except PermissionDenied:
            pass

        # View Function is not called because exception
        self.assertFalse(func.called)

        request.user = model_fixture.manageruser
        HACS_ACCESS_CONTROL_LOCAL.current_user = request.user

        decorated_view(request)
        # Manager User Has Permission
        self.assertTrue(func.called)

        request.user = model_fixture.superuser
        HACS_ACCESS_CONTROL_LOCAL.current_user = request.user

        # SuperUser has always on permission
        decorated_view(request)
        # Two calls already done!
        self.assertEqual(2, func.call_count)
