import arrow
import pytest
from django.conf import settings
from django.core.urlresolvers import reverse
from moneyed import EUR, RUB, Money

from billing.lib.test import json_contains
from clients.models import Client, ClientRu, ClientService, Company
from clients.tasks import client_services_update

from ..models import Order, Price, Service
from ..tasks import orders_clients_disable, orders_payment_notify

pytestmark = pytest.mark.django_db


def test_order_client_services_by_category(make_orders):
    order = Order.objects.get(pk=1)
    client_service = ClientService.objects.get(pk=2)
    service = Service.objects.get(pk=3)
    service.prices.add(
        Price.objects.create(
            price=Money(750, EUR),
            service=service,
        ))
    client_service.pk = None
    client_service.service = service
    client_service.save()

    order.client_services.add(1, 2, client_service)
    cats = order.client_services_by_category

    assert len(cats) == 2
    assert len(cats[1].client_services) == 2
    assert len(cats[0].client_services) == 1

    assert cats[0].price == Money(3750, EUR)
    assert cats[1].quantity == 7


def test_order_creation_and_modifications(mailoutbox):
    order = Order()
    order.client_id = 1
    order.note = 'test note'
    order.save()

    assert order.note == 'test note'
    assert order.price == Money(0, EUR)
    assert order.status == 'new'
    expired_date = arrow.get(order.created).shift(
        days=+settings.MB_ORDER_EXPIRED_DAYS).floor('second').datetime
    assert arrow.get(order.expired_date).floor('second') == expired_date

    assert len(mailoutbox) == 1
    mail = mailoutbox[0]
    html = mail.alternatives[0][0]

    assert 'New order created' in mail.subject
    assert mail.recipients() == ['user@one.com']
    assert '20 more days' in html
    assert 'User One' in html

    order.client_services.add(1, 2)
    assert order.price == Money(14001.83, EUR)
    assert 'Test service two' in order.note_en
    assert 'Тестовый сервис' in order.note_ru
    assert '1,999.98' in order.note

    order.price = Money(111.25, EUR)
    order.save()

    assert order.price == Money(111.25, EUR)

    order.price = 0
    order.save()
    assert order.price == Money(14001.83, EUR)
    assert 'Test service one' in order.note
    assert '12,001.85' in order.note


def test_ordrers_list_by_user(client):
    response = client.get(reverse('order-list'))
    assert response.status_code == 401


def test_order_list_by_admin(admin_client):
    client_services_update.delay()
    response = admin_client.get(reverse('order-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 3
    json_contains(response, 'Test service two - 7,000.00')
    json_contains(response, 'Test service one - 4,600.00')

    response = admin_client.get(
        reverse('order-list') + '?client__login=user-one')
    response_json = response.json()
    assert len(response_json['results']) == 1
    assert response_json['results'][0]['client'] == 'user-one'


def test_order_display_by_user(client):
    client_services_update.delay()
    response = client.get(reverse('order-detail', args=[2]))
    assert response.status_code == 401


def test_order_display_by_admin(admin_client):
    client_services_update.delay()
    order = Order.objects.first()
    response = admin_client.get(reverse('order-detail', args=[order.id]))
    assert response.status_code == 200

    json_contains(response, order.client.login)
    json_contains(response, str(order.price.amount))


def test_manager_get_for_payment_notification(make_orders):
    orders = Order.objects.get_for_payment_notification()
    assert orders.count() == 1
    assert orders[0].note == 'payment notification'
    assert orders[0].status in ('new', 'processing')
    assert orders[0].expired_date <= arrow.utcnow().shift(
        days=settings.MB_ORDER_PAYMENT_NOTIFY_DAYS).datetime


def test_orders_payment_notification(make_orders, mailoutbox):
    orders_payment_notify.delay()
    mail = mailoutbox[-1]
    html = mail.alternatives[0][0]

    assert mail.recipients() == ['user@one.com']
    assert 'Order will expire soon' in mail.subject
    assert 'We glad to see' not in html
    assert 'User One' in html

    Order.objects.filter(client_id=1, status='paid').delete()
    orders_payment_notify.delay()

    mail = mailoutbox[-1]
    html = mail.alternatives[0][0]

    assert 'We are glad to see' in html


def test_manager_get_expired(make_orders):
    orders = Order.objects.get_expired()
    assert orders.count() == 1
    assert orders[0].note == 'order expired'
    assert orders[0].status in ('new', 'processing')
    assert orders[0].expired_date <= arrow.utcnow()


def test_order_payer(make_orders, settings):
    def _get_order():
        return Order.objects.get(pk=1)

    client_filter = ('phone', )
    client = Client.objects.get(login='user-one')
    company = Company.objects.get(pk=2)
    phone = client.phone
    order = _get_order()

    assert order.get_payer() == client
    client.phone = None
    client.save()

    order = _get_order()

    assert order.get_payer(client_filter) is None

    client.phone = phone
    client.country_id = 192
    client.save()

    order = _get_order()
    assert order.get_payer() == company

    company.client_id = 2
    company.save()
    order = _get_order()

    assert order.get_payer() is None

    ClientRu.objects.create(
        client=client,
        passport_serial=1 * 4,
        passport_number=1 * 6,
        passport_date='2017-12-01T10:22:48.995041Z',
        passport_issued_by=1 * 10,
    )
    order = _get_order()
    assert order.get_payer() == client


def test_orders_clients_disable(make_orders, mailoutbox):
    orders_clients_disable.delay()
    mailoutbox = [m for m in mailoutbox if 'account is disabled' in m.subject]
    assert len(mailoutbox) == 1
    assert mailoutbox[0].recipients() == ['user@one.com']
    assert 'User One' in mailoutbox[-1].alternatives[0][0]
    assert '#3' in mailoutbox[-1].alternatives[0][0]

    client = Client.objects.get(login='user-one')
    assert client.status == 'disabled'
    format = '%d.%m.%Y %H:%I'
    assert client.disabled_at.strftime(format) == arrow.utcnow().\
        strftime(format)
    client.check_status()
    client.refresh_from_db()
    assert client.status == 'disabled'

    Order.objects.get(pk=3).set_paid('bill')
    client.refresh_from_db()
    assert client.status == 'active'


def test_orders_services_activation(make_orders):
    order = Order.objects.get(pk=1)
    order.client_services.add(1, 2)
    assert order.client_services.first().is_paid is False
    order.set_paid('bill')
    assert order.client_services.first().is_paid is True


def test_order_with_invalid_currencies():
    order = Order()
    order.client_id = 1
    order.save()
    assert order.price == Money(0, EUR)
    order.client_services.add(5)
    assert order.price == Money(4000, RUB)
    assert order.get_room_service.id == 2

    order.client_services.add(4)
    assert order.status == 'corrupted'
    assert order.price == Money(0, EUR)


def test_order_paid_email(make_orders, mailoutbox):
    order_en = Order.objects.get(pk=1)
    order_ru = Order.objects.get(pk=5)

    order_en.status = 'paid'
    order_en.save()

    assert mailoutbox[-1].recipients() == ['user@one.com']
    assert 'Your payment was successful' in mailoutbox[-1].subject
    assert 'User One' in mailoutbox[-1].alternatives[0][0]
    assert '#1' in mailoutbox[-1].alternatives[0][0]

    order_ru.status = 'paid'
    order_ru.save()

    assert mailoutbox[-1].recipients() == ['user@rus.com']
    assert 'Успешная оплата' in mailoutbox[-1].subject
    assert 'user rus' in mailoutbox[-1].alternatives[0][0]
    assert '№5' in mailoutbox[-1].alternatives[0][0]
