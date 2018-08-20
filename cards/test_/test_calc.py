import pytest
from clients.models import ClientService
from django.core.urlresolvers import reverse
from django.test import TestCase
from finances.lib.calc import Calc
from finances.lib.calc import Exception as CalcException
from finances.lib.calc import Other, Rooms
from finances.models import Service
from moneyed import EUR, RUB, Money

pytestmark = pytest.mark.django_db


def test_calc__get_service():
    service_by_id = Calc._get_service(1)
    service_by_instace = Calc._get_service(Service.objects.get(pk=2))
    service_by_client_service = Calc._get_service(
        ClientService.objects.get(pk=2))
    assert isinstance(service_by_id, Service)
    assert isinstance(service_by_instace, Service)
    assert isinstance(service_by_client_service, Service)
    assert service_by_id.pk == 1
    assert service_by_instace.pk == 2
    assert service_by_client_service.pk == 2


def test_calc_factory():
    rooms = Calc.factory(2)
    other = Calc.factory(3)

    assert isinstance(rooms, Rooms)
    assert isinstance(other, Other)


def test_calc_price(make_prices):
    ClientService.objects.filter(pk=1).update(service_id=4, quantity=35)
    client_service = ClientService.objects.get(pk=1)
    service = Service.objects.get(pk=4)
    price = Calc.factory(client_service).calc()
    price_by_params = Calc.factory(4).calc(quantity=35, country=1)
    price_base = Calc.factory(4).calc(quantity=35, country=3)

    ClientService.objects.filter(pk=1).update(service_id=4, quantity=11)
    client_service.refresh_from_db()
    price_another1 = Calc.factory(client_service).calc()
    price_another2 = Calc.factory(service).calc(quantity=5, country=1)
    price_another3 = Calc.factory(4).calc(quantity=10, country=1)
    price_entry = service.prices.get(
        country_id=1,
        period_from__isnull=True,
        period_to__isnull=True,
    )
    price_entry.price = Money(100, RUB)
    price_entry.save()

    with pytest.raises(TypeError):
        Calc.factory(4).calc(quantity=45, country=1)

    service.prices.filter(
        country_id=1,
        period_from__isnull=True,
        period_to__isnull=True,
    ).delete()
    price_cropped_period = Calc.factory(4).calc(quantity=45, country=1)

    assert price == Money(1897, EUR)
    assert price_by_params == Money(1897, EUR)
    assert price_base == Money(675, EUR)
    assert price_another1 == Money(457, EUR)
    assert price_another2 == Money(422, EUR)
    assert price_another3 == Money(422, EUR)
    assert price_cropped_period == Money(1487, EUR)

    service.prices.filter().delete()
    with pytest.raises(CalcException):
        Calc.factory(4).calc(quantity=12, country=1)


def test_calc_api_by_user(client):
    response = client.get(reverse('service-calc'))
    assert response.status_code == 401


def test_calc_api_invalid_by_admin(admin_client):
    url = reverse('service-calc')
    response_empty = admin_client.get(url)
    response_quantity = admin_client.get(
        url + '?quantity=1sd&country=ff&period=1')
    response_country = admin_client.get(
        url + '?quantity=1&country=ff&period=1')
    response_service = admin_client.get(
        url + '?quantity=12&country=ad&period=9')

    assert response_empty.status_code == 200
    assert response_empty.json() == {
        'errors': {
            'quantity': ['This field is required.'],
            'country': ['This field is required.']
        },
        'status': False
    }
    assert response_quantity.status_code == 200
    assert response_quantity.json() == {
        'errors': {
            'quantity': ['A valid integer is required.'],
        },
        'status': False
    }
    assert response_country.status_code == 200
    assert response_country.json() == {
        'errors': {
            'calc': ['Invalid country or quantity.'],
        },
        'status': False
    }
    assert response_service.status_code == 200
    assert response_service.json() == {
        'errors': {
            'service': ['service not found.'],
        },
        'status': False
    }


def test_calc_api_by_admin(admin_client, make_prices):
    url = reverse('service-calc')

    response_1 = admin_client.get(url + '?quantity=12&country=ad&period=3')
    response_2 = admin_client.get(url + '?quantity=12&country=ad&period=1')
    response_3 = admin_client.get(url + '?quantity=12&country=ad&period=3')
    response_4 = admin_client.get(url + '?quantity=12&country=ad')
    response_data_1 = {
        'status': True,
        'price': 27600.0,
        'price_currency': 'EUR',
        'period': 3
    }
    response_data_2 = {
        'status': True,
        'price': 492.0,
        'price_currency': 'EUR',
        'period': 1
    }
    response_data_3 = {
        'status': True,
        'prices': [response_data_2, response_data_1]
    }

    assert response_1.status_code == 200
    assert response_2.status_code == 200
    assert response_3.status_code == 200
    assert response_4.status_code == 200
    assert response_1.json() == response_data_1
    assert response_2.json() == response_data_2
    assert response_3.json() == response_data_1
    assert response_4.json() == response_data_3


@pytest.mark.usefixtures("make_prices")
class CalcTestCase(TestCase):
    def test_calc_api_cache(self):
        admin_client = self.client
        admin_client.login(username='admin', password='password')
        url = reverse('service-calc')

        with self.assertNumQueries(7):
            admin_client.get(url + '?quantity=12&country=ad&period=3')
        with self.assertNumQueries(7):
            admin_client.get(url + '?quantity=22&country=ad&period=3')
        with self.assertNumQueries(2):
            admin_client.get(url + '?quantity=12&country=ad&period=3')
