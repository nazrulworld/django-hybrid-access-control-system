# -*- coding: utf-8 -*-
# ++ This file `test_functions.py` is generated at 1/17/17 4:42 PM ++

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

"""
1. https://www.postgresql.org/docs/9.4/static/functions-json.html
2. http://www.w3resource.com/PostgreSQL/postgresql-json-functions-and-operators.php
3. https://hashrocket.com/blog/posts/faster-json-generation-with-postgresql
4. http://stackoverflow.com/questions/30101603/merging-concatenating-jsonb-columns-in-query
5. http://andilabs.github.io/django/django-1-8/expressions/func/f/2015/08/29/django-1.8-new-db-models-expressions-F-Func.html
6. https://docs.djangoproject.com/en/1.10/ref/models/expressions/
7. http://dba.stackexchange.com/questions/54283/how-to-turn-json-array-into-postgres-array
8. http://www.postgresonline.com/journal/archives/228-PostgreSQL-Array-The-ANY-and-Contains-trick.html
9. http://grokbase.com/t/postgresql/pgsql-general/12cetwm4kp/implicit-casts-to-array-types
10. https://www.postgresql.org/message-id/4336A43AB8A446CEBAF7AFBD2D050292@andrusnotebook
11. https://www.postgresql.org/message-id/flat/CABRT9RBTKzSWvuwd7ztXx=b7Sh0Z4gutdXPeE=j30sfV5acCMA@mail.gmail.com#CABRT9RBTKzSWvuwd7ztXx=b7Sh0Z4gutdXPeE=j30sfV5acCMA@mail.gmail.com
"""

# SELECT * FROM test_date_folder WHERE "test_date_folder"."permissions_actions_map" -> 'object.view' <@ '["hacs.CanTraverseContainer", "hacs.CanListObjects", "hacs.ViewContent", "hacs.AddContent", "hacs.PublicView", "hacs.AuthenticatedView"]';
# SELECT * FROM test_date_folder WHERE "test_date_folder"."roles_actions_map" -> 'object.view' <@ '["Manager", "hacs.PublicView"]';
# SELECT local_roles::jsonb -> 'contributor@test.com'   FROM test_news_item;
# SELECT name, jsonb_extract_path(local_roles::jsonb, 'contributor@test.com'), roles_actions_map -> 'object.view'   FROM test_news_item;

# Success
# SELECT name  FROM test_news_item WHERE roles_actions_map -> 'object.view' @> jsonb_extract_path(local_roles::jsonb, 'contributor@test.com');
# SELECT name  FROM test_news_item WHERE "test_news_item". "roles_actions_map" -> 'object.view' @> jsonb_extract_path("test_news_item"."local_roles"::jsonb, 'contributor@test.com');
# SELECT name  FROM test_news_item WHERE "test_news_item"."roles_actions_map" -> 'object.view' @> (jsonb_extract_path("test_news_item"."local_roles"::jsonb, contributor@test.com));

# select id from test_news_item WHERE roles_actions_map -> 'object.view'  ?| ("test_news_item"."local_roles" -> 'contributor@test.com');
# select query from pg_stat_activity;
# select id, array(select jsonb_array_elements_text("test_news_item"."local_roles" -> 'contributor@test.com')) from test_news_item;
#select id from test_news_item WHERE roles_actions_map -> 'object.view'  ?| array(select jsonb_array_elements_text("test_news_item"."local_roles" -> 'contributor@test.com'));
# Working!
# select id from test_news_item WHERE roles_actions_map -> 'object.view'  ?| (ARRAY(SELECT jsonb_array_elements_text("test_news_item"."local_roles" -> 'contributor@test.com')));
"""
PG LOG
SELECT "test_news_item"."id", "test_news_item"."uuid", "test_news_item"."name", "test_news_item"."slug", "test_news_item"."created_on", "test_news_item"."created_by_id", "test_news_item"."modified_by_id", "test_news_item"."modified_on", "test_news_item"."state", "test_news_item"."permissions_actions_map", "test_news_item"."roles_actions_map", "test_news_item"."local_roles", "test_news_item"."owner_id", "test_news_item"."acquired_owners", "test_news_item"."acquire_parent", "test_news_item"."description", "test_news_item"."container_content_type_id", "test_news_item"."container_id", "test_news_item"."extra_info" FROM "test_news_item" WHERE "test_news_item"."roles_actions_map" -> 'object.view' ?| ARRAY['Editor', 'Contributor', 'Manager']
2017-01-31 16:50:21 UTC [2690-160] hacs_admin@hacs_db LOG:  statement: SELECT "hacs_users"."id", "hacs_users"."password", "hacs_users"."last_login", "hacs_users"."first_name", "hacs_users"."last_name", "hacs_users"."email", "hacs_users"."is_active", "hacs_users"."is_staff", "hacs_users"."is_superuser" FROM "hacs_users" WHERE "hacs_users"."id" = 3

DJANGO PRINT
SELECT "test_news_item"."id", "test_news_item"."uuid", "test_news_item"."name", "test_news_item"."slug", "test_news_item"."created_on", "test_news_item"."created_by_id", "test_news_item"."modified_by_id", "test_news_item"."modified_on", "test_news_item"."state", "test_news_item"."permissions_actions_map", "test_news_item"."roles_actions_map", "test_news_item"."local_roles", "test_news_item"."owner_id", "test_news_item"."acquired_owners", "test_news_item"."acquire_parent", "test_news_item"."description", "test_news_item"."container_content_type_id", "test_news_item"."container_id", "test_news_item"."extra_info" FROM "test_news_item" WHERE "test_news_item"."roles_actions_map" -> 'object.view' ?| [u'Editor', u'Contributor', u'Manager']
"""
