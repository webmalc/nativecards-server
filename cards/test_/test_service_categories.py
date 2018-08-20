from django.core.urlresolvers import reverse

from billing.lib.test import json_contains


def test_service_categories_list_by_user(client):
    response = client.get(reverse('servicecategory-list'))
    assert response.status_code == 401


def test_service_category_categories_list_by_admin(admin_client):
    response = admin_client.get(reverse('servicecategory-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 3
    json_contains(response, 'Test category 1 description')


def test_service_category_categories_list_by_admin_ru(admin_client, settings):
    settings.LANGUAGE_CODE = 'ru'
    response = admin_client.get(reverse('servicecategory-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 3
    json_contains(response, 'Тестовая категория 2')


def test_service_category_display_by_admin(admin_client):
    response = admin_client.get(reverse('servicecategory-detail', args=[3]))
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['title'] == 'Test category 3'


def test_service_category_display_by_user(client):
    response = client.get(reverse('servicecategory-detail', args=[2]))
    assert response.status_code == 401
