import pytest
from django.core.urlresolvers import reverse

from billing.lib.test import json_contains
from finances.models import Price, Service
from hotels.models import Country

pytestmark = pytest.mark.django_db


def test_price_list_by_user(client):
    response = client.get(reverse('price-list'))
    assert response.status_code == 401


def test_price_list_by_admin(admin_client, settings):
    response = admin_client.get(reverse('price-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 6
    json_contains(response, '234234.00')


def test_price_display_by_user(client):
    response = client.get(reverse('price-detail', args=[7]))
    assert response.status_code == 401


def test_price_display_by_admin(admin_client):
    response = admin_client.get(reverse('price-detail', args=[11]))
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['price'] == '4500.00'
    assert response_json['country'] is None
    assert response_json['is_enabled'] is True
    assert response_json['for_unit'] is False


def test_price_new(make_prices):
    """
    All asserts in make_prices fixture
    """
    pass


def test_prices_filter_by_country(make_prices):

    service = Service.objects.get(pk=4)
    country_prices = Price.objects.filter_by_country(
        Country.objects.get(pk=1),
        service,
    )
    base_prices = Price.objects.filter_by_country(
        Country.objects.get(pk=3),
        service,
    )

    assert country_prices.count() == 3
    assert base_prices.count() == 4
    assert country_prices.first().country.pk == 1
    assert base_prices.first().country is None
