# -*- coding: utf-8 -*-
# ++ This file `fixture.py` is generated at 12/12/16 5:20 PM ++
from hacs.db.models import HacsItemModel
from hacs.db.models import HacsContainerModel
from hacs.models import HacsContentType
from hacs.helpers import get_user_model
from hacs.helpers import get_workflow_model
from hacs.security.helpers import attach_system_user
from hacs.security.helpers import release_system_user
from django.utils.functional import cached_property
from django.contrib.contenttypes.models import ContentType
from tests.helpers import setupModels, tearDownModels

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class ModelFixture(object):

    def init_data(self):
        """
        :return:
        """
        try:
            attach_system_user()
            setupModels(*self.models.values())
            # Initialized Hacs ContentType
            self.init_hacs_content_types()
            # Initialized Hacs ContentType Data
            self.init_hacs_content_data()
        finally:
            release_system_user()

    def init_hacs_content_types(self):

        news_folder_cts = ContentType.objects.get_for_model(self.models['news_folder_cls'])
        folder_workflow = get_workflow_model().objects.get_by_natural_key("simple-folder-publication")
        news_folder_ct_obj = HacsContentType(
            name="new folder contenttype",
            slug="new-folder-contenttype",
            content_type=news_folder_cts,
            globally_allowed=True,
            workflow=folder_workflow,
            permissions_actions_map={
                "object.create": ["hacs.ManagePortal"],
                "object.view": ["hacs.ViewContent", "hacs.ManageContent"],
                "object.edit": ["hacs.ModifyContent"],
                "object.delete": ["hacs.DeleteContent"],
                "object.manage_state":["Hacs.ManageContentState"],
                "share": ["hacs.ManageContentState"],
                "list.traverse": ["hacs.CanTraverseContainer"],
                "list.view": ["hacs.CanListObjects"],
                "list.update": ["hacs.CanModifyObjects"],
                "list.delete": ["hacs.CanDeleteObjects"]
            },
            created_by=self.superuser

        )
        news_folder_ct_obj.save()

        date_folder_cts = ContentType.objects.get_for_model(self.models['date_folder_cls'])
        folder_workflow = get_workflow_model().objects.get_by_natural_key("simple-folder-publication")
        date_folder_ct_obj = HacsContentType(
            name="date folder contenttype",
            slug="date-folder-contenttype",
            content_type=date_folder_cts,
            globally_allowed=False,
            workflow=None,
            permissions_actions_map={
                "object.create": ["hacs.ManageContent"],
            },
            created_by=self.superuser

        )
        date_folder_ct_obj.save()

        news_item_cts = ContentType.objects.get_for_model(self.models['news_item_cls'])
        news_item_workflow = get_workflow_model().objects.get_by_natural_key("simple-item-publication")
        news_item_ct_obj = HacsContentType(
            name="news item contenttype",
            slug="news-item-contenttype",
            content_type=news_item_cts,
            globally_allowed=False,
            workflow=news_item_workflow,
            permissions_actions_map={
              "object.create": ["hacs.AddContent"],
              "object.view": ["hacs.ViewContent"],
              "object.edit": ["hacs.ModifyContent"],
              "object.delete": ["hacs.DeleteContent"],
              "object.manage_state":["Hacs.ManageContentState"],
              "share": ["hacs.ManageContentState"]
            },
            created_by=self.superuser

        )

        news_folder_ct_obj.allowed_content_types.add(date_folder_cts)
        date_folder_ct_obj.allowed_content_types.add(news_item_cts)

        news_item_ct_obj.save()
        ###############################################################

    def init_hacs_content_data(self):
        """"""
        folder_cls = self.models.get('news_folder_cls')
        data = {
            "name": "NewsFolder",
            "slug": "news-folder",
            "description": "News Folder",
            "created_by": self.superuser,
            "owner": self.superuser,
            "acquire_parent": False,
            "workflow": None,
            "container_content_type": None,
            "parent_container_id": None,
            "recursive": True
        }

        news_folder = folder_cls(**data)
        news_folder.save()

        date_folder_cls = self.models.get('date_folder_cls')
        data = {
            "name": "2016-10-10",
            "slug": "2016-10-10",
            "description": "10th December, 2016",
            "created_by": self.superuser,
            "local_roles": None,
            "owner": self.superuser,
            "acquire_parent": True,
            "workflow": None,
            "container_content_type": ContentType.objects.get_for_model(folder_cls),
            "parent_container_id": news_folder.pk,
            "recursive": True
        }

        date_folder = date_folder_cls(**data)
        date_folder.save()

        news_item_cls = self.models.get('news_item_cls')
        data = {
            "name": "news one",
            "slug": "news-one",
            "description": "news of HACS",
            "created_by": self.contributoruser,
            "owner": self.contributoruser,
            "acquire_parent": True,
            "container_content_type": ContentType.objects.get_for_model(date_folder_cls),
            "container_id": date_folder.pk
        }
        news_item = news_item_cls(**data)
        news_item.save()

        data2 = {
            "name": "news two with local roles",
            "slug": "news-two-with-local-roles",
            "description": "news of HACS with local roles",
            "created_by": self.editoruser,
            "owner": self.editoruser,
            "local_roles": {"contributor@test.com": ("Editor", "Member")},
            "acquire_parent": True,
            "container_content_type": ContentType.objects.get_for_model(date_folder_cls),
            "container_id": date_folder.pk
        }
        news_item2 = news_item_cls(**data2)
        news_item2.save()

    def tear_down(self):
        """
        :return:
        """
        try:
            attach_system_user()
            for model in self.models.values():
                try:
                    ct = ContentType.objects.get_for_model(model)
                    try:
                        HacsContentType.objects.get(content_type=ct).delete()
                    except HacsContentType.DoesNotExist:
                        pass
                    ct.delete()
                except model.DoesNotExist:
                    pass

            tearDownModels(*self.models.values())
        finally:
            release_system_user()

    @cached_property
    def models(self):
        """
        :return:
        """
        from hacs.db.models.fields import JSONField

        class NewsFolder(HacsContainerModel):

            extra_info = JSONField(null=True)

            class Meta:
                app_label = "hacs"
                db_table = "test_news_folder"

        class DateFolder(HacsContainerModel):

            extra_info = JSONField(null=True)

            class Meta:
                app_label = "hacs"
                db_table = "test_date_folder"

        class NewsItem(HacsItemModel):

            extra_info = JSONField(null=True)

            class Meta:
                app_label = "hacs"
                db_table = "test_news_item"

        return {
            "news_folder_cls": NewsFolder,
            "date_folder_cls": DateFolder,
            "news_item_cls": NewsItem
        }

    @cached_property
    def superuser(self):
        """
        :return:
        """
        return get_user_model().objects.get_by_natural_key("superuser@test.com")

    @cached_property
    def manageruser(self):
        """
        :return:
        """
        return get_user_model().objects.get_by_natural_key("manager@test.com")

    @cached_property
    def editoruser(self):
        """
        :return:
        """
        return get_user_model().objects.get_by_natural_key("editor@test.com")

    @cached_property
    def contributoruser(self):
        """
        :return:
        """
        return get_user_model().objects.get_by_natural_key("contributor@test.com")

    @cached_property
    def memberuser(self):
        """
        :return:
        """
        return get_user_model().objects.get_by_natural_key("member@test.com")

model_fixture = ModelFixture()
