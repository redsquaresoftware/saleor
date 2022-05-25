import graphene
import pytest
from freezegun import freeze_time

from .....core.jwt import create_access_token_for_app
from ....tests.utils import assert_no_permission, get_graphql_content

QUERY_APP = """
    query ($id: ID){
        app(id: $id){
            id
            created
            isActive
            permissions{
                code
            }
            tokens{
                authToken
            }
            webhooks{
                name
            }
            name
            type
            aboutApp
            dataPrivacy
            dataPrivacyUrl
            homepageUrl
            supportUrl
            configurationUrl
            appUrl
            accessToken
            extensions{
                id
                label
                url
                view
                type
                target
                permissions{
                    code
                }
            }
        }
    }
    """


@freeze_time("2012-01-14 11:00:00")
@pytest.mark.parametrize("app_type", ("external", "custom"))
def test_app_query(
    app_type,
    staff_api_client,
    permission_manage_apps,
    permission_manage_staff,
    app,
    external_app,
    webhook,
):
    app = app if app_type == "custom" else external_app
    app.permissions.add(permission_manage_staff)

    webhook = webhook
    webhook.app = app
    webhook.save()

    id = graphene.Node.to_global_id("App", app.id)
    variables = {"id": id}
    response = staff_api_client.post_graphql(
        QUERY_APP,
        variables,
        permissions=[permission_manage_apps],
    )
    content = get_graphql_content(response)

    tokens = app.tokens.all()
    app_data = content["data"]["app"]
    tokens_data = app_data["tokens"]
    assert tokens.count() == 1
    assert tokens_data[0]["authToken"] == tokens.first().auth_token[-4:]

    assert app_data["isActive"] == app.is_active
    assert app_data["permissions"] == [{"code": "MANAGE_STAFF"}]
    assert len(app_data["webhooks"]) == 1
    assert app_data["webhooks"][0]["name"] == webhook.name
    assert app_data["type"] == app.type.upper()
    assert app_data["aboutApp"] == app.about_app
    assert app_data["dataPrivacy"] == app.data_privacy
    assert app_data["dataPrivacyUrl"] == app.data_privacy_url
    assert app_data["homepageUrl"] == app.homepage_url
    assert app_data["supportUrl"] == app.support_url
    assert app_data["configurationUrl"] == app.configuration_url
    assert app_data["appUrl"] == app.app_url
    if app_type == "external":
        assert app_data["accessToken"] == create_access_token_for_app(
            app, staff_api_client.user
        )
    else:
        assert app_data["accessToken"] is None


def test_app_query_no_permission(
    staff_api_client, permission_manage_staff, permission_manage_users, app
):
    app.permissions.add(permission_manage_staff)

    id = graphene.Node.to_global_id("App", app.id)
    variables = {"id": id}
    response = staff_api_client.post_graphql(QUERY_APP, variables, permissions=[])
    assert_no_permission(response)

    response = staff_api_client.post_graphql(
        QUERY_APP,
        variables,
        permissions=[permission_manage_users, permission_manage_staff],
    )
    assert_no_permission(response)


def test_app_with_access_to_resources(
    app_api_client,
    app,
    permission_manage_orders,
    order_with_lines,
):
    query = """
      query {
        orders(first: 5) {
          edges {
            node {
              id
            }
          }
        }
      }
    """
    response = app_api_client.post_graphql(query)
    assert_no_permission(response)
    response = app_api_client.post_graphql(
        query, permissions=[permission_manage_orders]
    )
    get_graphql_content(response)


def test_app_without_id_as_staff(
    staff_api_client, app, permission_manage_apps, order_with_lines, webhook
):
    response = staff_api_client.post_graphql(
        QUERY_APP, permissions=[permission_manage_apps]
    )
    content = get_graphql_content(response)
    assert content["data"]["app"] is None


def test_own_app_without_id(
    app_api_client, app, permission_manage_orders, order_with_lines, webhook
):
    response = app_api_client.post_graphql(
        QUERY_APP,
    )
    content = get_graphql_content(response)

    tokens = app.tokens.all()
    app_data = content["data"]["app"]
    tokens_data = app_data["tokens"]
    assert tokens.count() == 1
    assert tokens_data[0]["authToken"] == tokens.first().auth_token[-4:]

    assert app_data["isActive"] == app.is_active
    assert len(app_data["webhooks"]) == 1
    assert app_data["webhooks"][0]["name"] == webhook.name
    assert app_data["type"] == app.type.upper()
    assert app_data["aboutApp"] == app.about_app
    assert app_data["dataPrivacy"] == app.data_privacy
    assert app_data["dataPrivacyUrl"] == app.data_privacy_url
    assert app_data["homepageUrl"] == app.homepage_url
    assert app_data["supportUrl"] == app.support_url
    assert app_data["configurationUrl"] == app.configuration_url
    assert app_data["appUrl"] == app.app_url


def test_app_query_without_permission(
    app_api_client,
    app,
    order_with_lines,
):
    id = graphene.Node.to_global_id("App", app.id)
    variables = {"id": id}
    response = app_api_client.post_graphql(
        QUERY_APP,
        variables,
    )
    assert_no_permission(response)


def test_app_query_without_permission_and_id(
    staff_api_client,
    app,
    order_with_lines,
):
    response = staff_api_client.post_graphql(
        QUERY_APP,
    )
    assert_no_permission(response)


def test_app_query_with_permission(
    app_api_client, permission_manage_apps, app, external_app, webhook
):
    app.permissions.add(permission_manage_apps)
    id = graphene.Node.to_global_id("App", app.id)
    variables = {"id": id}
    response = app_api_client.post_graphql(
        QUERY_APP,
        variables,
    )
    content = get_graphql_content(response)

    tokens = app.tokens.all()
    app_data = content["data"]["app"]
    tokens_data = app_data["tokens"]
    assert tokens.count() == 1
    assert tokens_data[0]["authToken"] == tokens.first().auth_token[-4:]

    assert app_data["isActive"] == app.is_active
    assert len(app_data["webhooks"]) == 1
    assert app_data["webhooks"][0]["name"] == webhook.name
    assert app_data["type"] == app.type.upper()
    assert app_data["aboutApp"] == app.about_app
    assert app_data["dataPrivacy"] == app.data_privacy
    assert app_data["dataPrivacyUrl"] == app.data_privacy_url
    assert app_data["homepageUrl"] == app.homepage_url
    assert app_data["supportUrl"] == app.support_url
    assert app_data["configurationUrl"] == app.configuration_url
    assert app_data["appUrl"] == app.app_url


def test_query_app_for_federation(api_client, app):
    app_id = graphene.Node.to_global_id("App", app.pk)
    variables = {
        "representations": [
            {
                "__typename": "App",
                "id": app_id,
            },
        ],
    }
    query = """
      query GetAppInFederation($representations: [_Any]) {
        _entities(representations: $representations) {
          __typename
          ... on App {
            id
            name
          }
        }
      }
    """

    response = api_client.post_graphql(query, variables)
    content = get_graphql_content(response)
    assert content["data"]["_entities"] == [
        {
            "__typename": "App",
            "id": app_id,
            "name": app.name,
        }
    ]
