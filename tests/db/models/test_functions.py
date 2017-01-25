# -*- coding: utf-8 -*-
# ++ This file `test_functions.py` is generated at 1/17/17 4:42 PM ++

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

"""
1. https://www.postgresql.org/docs/9.5/static/functions-json.html
2. http://www.w3resource.com/PostgreSQL/postgresql-json-functions-and-operators.php
3. https://hashrocket.com/blog/posts/faster-json-generation-with-postgresql
4. http://stackoverflow.com/questions/30101603/merging-concatenating-jsonb-columns-in-query
5. http://andilabs.github.io/django/django-1-8/expressions/func/f/2015/08/29/django-1.8-new-db-models-expressions-F-Func.html
6. https://docs.djangoproject.com/en/1.10/ref/models/expressions/
"""

# SELECT * FROM test_date_folder WHERE "test_date_folder"."permissions_actions_map" -> 'object.view' <@ '["hacs.CanTraverseContainer", "hacs.CanListObjects", "hacs.ViewContent", "hacs.AddContent", "hacs.PublicView", "hacs.AuthenticatedView"]';
# SELECT * FROM test_date_folder WHERE "test_date_folder"."roles_actions_map" -> 'object.view' <@ '["Manager", "hacs.PublicView"]';
# SELECT local_roles::jsonb -> 'contributor@test.com'   FROM test_news_item;
# SELECT name, jsonb_extract_path(local_roles::jsonb, 'contributor@test.com'), roles_actions_map -> 'object.view'   FROM test_news_item;

# Success
# SELECT name  FROM test_news_item WHERE roles_actions_map -> 'object.view' @> jsonb_extract_path(local_roles::jsonb, 'contributor@test.com');
# SELECT name  FROM test_news_item WHERE "test_news_item". "roles_actions_map" -> 'object.view' @> jsonb_extract_path("test_news_item"."local_roles"::jsonb, 'contributor@test.com');
# SELECT name  FROM test_news_item WHERE "test_news_item"."roles_actions_map" -> 'object.view' @> (jsonb_extract_path("test_news_item"."local_roles"::jsonb, contributor@test.com));
