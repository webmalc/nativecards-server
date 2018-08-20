from django.core.urlresolvers import reverse


def test_transaction_list_by_user(client):
    response = client.get(reverse('transaction-list'))
    assert response.status_code == 401


def test_transaction_list_by_admin(admin_client, settings):
    response = admin_client.get(reverse('transaction-list'))
    assert response.status_code == 200
    assert len(response.json()['results']) == 2
    id = response.json()['results'][1]['data']['id']
    assert id == 'ch_1BMDu2K2JgZdD3mVTvC8dXBw'


def test_transaction_display_by_admin(admin_client):
    response = admin_client.get(reverse('transaction-detail', args=[1]))
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['data']['id'] == 'ch_1BMDu2K2JgZdD3mVTvC8dXBw'


def test_transaction_display_by_user(client):
    response = client.get(reverse('transaction-detail', args=[1]))
    assert response.status_code == 401
