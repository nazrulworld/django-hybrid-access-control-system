# -*- coding: utf-8 -*-
# ++ This file `test_query.py` is generated at 1/15/17 6:36 PM ++
import pytest
from tests.path import FIXTURE_PATH
from django.test import TransactionTestCase
from django.db.models import Q
from hacs.helpers import get_group_model
from hacs.globals import HACS_ACCESS_CONTROL_LOCAL
from hacs.security.helpers import attach_system_user
from hacs.security.helpers import release_system_user
from hacs.security.helpers import SYSTEM_USER
from hacs.security.helpers import ANONYMOUS_USER
from hacs.helpers import get_workflow_model
from hacs.helpers import get_user_model
from tests.fixture import model_fixture

FIXTURE = FIXTURE_PATH / "testing_fixture.json"

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class TestHacsQuerySet(TransactionTestCase):
    """
    """
    fixtures = (FIXTURE,)

    def setUp(self):
        """
        :return:
        """
        super(TestHacsQuerySet, self).setUp()
        model_fixture.init_data()

    def __test_unrestricted(self):
        """ One of the most important test case see how
        """
        HACS_ACCESS_CONTROL_LOCAL.current_user = model_fixture.memberuser
        results = model_fixture.models.get('news_item_cls').objects.all()
        # Member User Has no views permissions
        self.assertEqual(0, len(results))
        results = model_fixture.models.get('news_item_cls').objects.unrestricted().all()
        # Now should have access! all
        self.assertEqual(2, len(results))
        # Let's test Relational access
        news_item = results[1]
        self.assertIsNotNone(news_item.created_by)
        # More upper level
        self.assertGreaterEqual(1, len(news_item.created_by.roles.all()))

        HACS_ACCESS_CONTROL_LOCAL.current_user = ANONYMOUS_USER
        try:
            model_fixture.models.get('news_item_cls').objects.get(pk=1, __restricted__=True)
            raise AssertionError("Code should not come here!, as anonymous user has no permission")
        except model_fixture.models.get('news_item_cls').DoesNotExist:
            pass

        news_item = model_fixture.models.get('news_item_cls').objects.get(pk=1)
        # Now anonymous user can view all! because by default `get` method is unrestricted
        self.assertIsNotNone(news_item.created_by)
        # More upper level
        self.assertGreaterEqual(1, len(news_item.created_by.roles.all()))
        # UserModel._default_manager.get_by_natural_key(username)

    def __test_get(self):
        """
        :return:
        """
        HACS_ACCESS_CONTROL_LOCAL.current_user = model_fixture.memberuser
        try:
            model_fixture.models.get('news_item_cls').objects.get(pk=1, __restricted__=True)
            raise AssertionError("Code should not come here!, as member user has no permission")
        except model_fixture.models.get('news_item_cls').DoesNotExist:
            pass

        news_item = model_fixture.models.get('news_item_cls').objects.get(pk=1)
        self.assertIsNotNone(news_item.created_by)
        self.assertGreaterEqual(1, len(news_item.created_by.roles.all()))

        HACS_ACCESS_CONTROL_LOCAL.current_user = ANONYMOUS_USER
        try:
            model_fixture.models.get('news_item_cls').objects.get(pk=1, __restricted__=True)
            raise AssertionError("Code should not come here!, as anonymous user has no permission")
        except model_fixture.models.get('news_item_cls').DoesNotExist:
            pass

        news_item = model_fixture.models.get('news_item_cls').objects.get(pk=1)
        self.assertIsNotNone(news_item.created_by)
        self.assertGreaterEqual(1, len(news_item.created_by.roles.all()))

    def __test__extract_security_info(self):
        """"""
        date_folder_cls = model_fixture.models.get('date_folder_cls')
        hacs_query = date_folder_cls.objects.all()

        # No user is set yet! so security guard is disabled and obiously user is none
        self.assertEqual((False, None, date_folder_cls.__hacs_base_content_type__), hacs_query._extract_security_info())

        attach_system_user()
        # System is user is set, so security guard is disabled
        self.assertEqual((False, SYSTEM_USER, date_folder_cls.__hacs_base_content_type__),
                         hacs_query._extract_security_info())
        release_system_user()
        # Test With authenticated user
        HACS_ACCESS_CONTROL_LOCAL.current_user = model_fixture.memberuser
        # Test with member user
        self.assertEqual((True, model_fixture.memberuser, date_folder_cls.__hacs_base_content_type__),
                         hacs_query._extract_security_info())
        hacs_query = get_group_model().objects.all()
        self.assertEqual((True, model_fixture.memberuser, get_group_model().__hacs_base_content_type__),
                         hacs_query._extract_security_info())

        hacs_query = get_workflow_model().objects.all()
        self.assertEqual((True, model_fixture.memberuser, get_workflow_model().__hacs_base_content_type__),
                         hacs_query._extract_security_info())

    def test__add_security_guard(self):
        """
        :return:
        """
        news_folder = model_fixture.models.get('news_folder_cls').objects.get(pk=1)
        date_folder_cls = model_fixture.models.get('date_folder_cls')
        hacs_query = date_folder_cls.objects.filter(created_by=model_fixture.superuser, created_on__year=2017).\
            exclude(Q(slug='fake-slug') | ~Q(slug='2016-10-10')).filter(Q(recursive=True,
                                                                          parent_container_id=news_folder.pk) & Q(acquire_parent=True))

        hacs_query._add_security_guard(date_folder_cls.__hacs_base_content_type__, model_fixture.contributoruser)
        sql_str = str(hacs_query.query)
        """
        sql_str =
        'SELECT "test_date_folder"."id", "test_date_folder"."uuid", "test_date_folder"."name",
        "test_date_folder"."slug", "test_date_folder"."created_on", "test_date_folder"."created_by_id",
        "test_date_folder"."modified_by_id", "test_date_folder"."modified_on", "test_date_folder"."state",
        "test_date_folder"."permissions_actions_map", "test_date_folder"."roles_actions_map",
        "test_date_folder"."local_roles", "test_date_folder"."owner_id", "test_date_folder"."acquired_owners",
        "test_date_folder"."acquire_parent", "test_date_folder"."description", "test_date_folder"."workflow_id",
        "test_date_folder"."container_content_type_id", "test_date_folder"."parent_container_id",
        "test_date_folder"."recursive", "test_date_folder"."extra_info"
        FROM "test_date_folder"
        WHERE ("test_date_folder"."created_on" BETWEEN 2017-01-01 00:00:00+00:00 AND 2017-12-31 23:59:59.999999+00:00
        AND "test_date_folder"."created_by_id" = 5
        AND NOT (("test_date_folder"."slug" = fake-slug OR NOT ("test_date_folder"."slug" = 2016-10-10)))
        AND "test_date_folder"."parent_container_id" = 1
        AND "test_date_folder"."recursive" = True
        AND "test_date_folder"."acquire_parent" = True
        AND ("test_date_folder"."permissions_actions_map" -> \'object.view\' ?| [u\'hacs.PublicView\',
        u\'hacs.AuthenticatedView\', u\'hacs.ViewContent\', u\'hacs.AddContent\', u\'hacs.CanListObjects\',
        u\'hacs.CanTraverseContainer\']
        OR "test_date_folder"."acquired_owners" @> \'"contributor@test.com"\'
        OR "test_date_folder"."roles_actions_map" -> \'object.view\' ?|
        (ARRAY(SELECT jsonb_array_elements_text("test_date_folder"."local_roles" -> contributor@test.com)))
        OR "test_date_folder"."owner_id" = 3))'
        """
        attach_system_user()
        user_permissions = model_fixture.contributoruser.get_all_permissions()
        release_system_user()
        for perm in user_permissions:
            if perm not in sql_str:
                pass
                #raise AssertionError("%s permission should have inside SQL string" % perm)
        # ***********************************
        # Test Local Roles Works!
        # Test Ownership Works!
        # Test Required Permission Works!
        # Security Should Respect Local roles
        # ************************************
        # If news item in private state then `hacs.ManageContent` permission is required
        news_item_cls = model_fixture.models.get('news_item_cls')
        for item in news_item_cls.objects.unrestricted():
            item.state = "private"
            item.save()

        HACS_ACCESS_CONTROL_LOCAL.current_user = model_fixture.editoruser

        results = news_item_cls.objects.all()
        count = len(results)
        # Any Editor has required view permission even in private state
        self.assertEqual(2, count)

        HACS_ACCESS_CONTROL_LOCAL.current_user = model_fixture.contributoruser
        results = news_item_cls.objects.all()
        # Although in private state, contributor user has no views access but in case of `contributor@test.com`
        # she is owner of first news item and has local role editor of second news item
        # ultimately should have two news items in result
        count = len(results)
        self.assertEqual(2, count)

        HACS_ACCESS_CONTROL_LOCAL.current_user = get_user_model().objects.get_by_natural_key("contributor2@test.com")
        results = news_item_cls.objects.all()
        count = len(results)
        # In Private state contributor has no view permissions!
        self.assertEqual(0, count)

        attach_system_user()
        # Restore to original State
        for item in news_item_cls.objects.unrestricted():
            item.state = "draft"
            item.save()
        release_system_user()
        # Now Second contributor user also should have view permission
        results = news_item_cls.objects.all()
        count = len(results)
        self.assertEqual(2, count)

        # *************
        # @TODO: Test Acquired Owners works
        # @TODO: Test View Permission of Utils Model
        # @TODO: Test View Permission of Static Model


    def tearDown(self):
        """"""
        model_fixture.tear_down()
        super(TestHacsQuerySet, self).tearDown()
        HACS_ACCESS_CONTROL_LOCAL.__release_local__()
