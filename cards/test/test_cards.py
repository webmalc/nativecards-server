"""
The test module for the cards application
"""
import json
import os

import pytest
from django.urls import reverse

from cards.models import Card
from nativecards.models import Settings

pytestmark = pytest.mark.django_db  # pylint: disable=invalid-name


def test_cards_get_random_words(admin):
    """
    Test the select_random_words method
    """
    with pytest.raises(ValueError) as error:
        Card.objects.select_random_words()
        assert error == 'the user and words fields are empty at the same time'
    words = Card.objects.select_random_words(admin)
    assert len(words) == 2

    random_words = Card.objects.get_random_words(admin)
    words = Card.objects.select_random_words(words=random_words,
                                             additional='additional')
    assert len(words) == 2

    for i in range(10):
        card = Card()
        card.word = 'word' + str(i)
        card.complete = 122
        card.created_by = admin
        card.deck_id = 1
        card.save()

    words = Card.objects.select_random_words(admin, additional='additional')
    words_next = Card.objects.select_random_words(admin,
                                                  additional='additional')
    assert len(words) == 4
    assert words != words_next

    assert 'additional' in words


def test_cards_guess_and_set_category(admin):
    """
    Should guess and set the word category
    """
    card = Card()
    card.word = 'word'
    card.created_by = admin
    card.save()

    assert card.category == 'word'

    card = Card()
    card.word = 'come up with'
    card.created_by = admin
    card.save()

    assert card.category == 'phrasal_verb'

    card = Card()
    card.word = 'get over'
    card.created_by = admin
    card.save()

    assert card.category == 'phrasal_verb'

    card = Card()
    card.word = 'to put it mildly'
    card.created_by = admin
    card.save()

    assert card.category == 'phrase'


def test_cards_default_deck(admin):
    """
    Should set the default deck for user
    """
    card = Card()
    card.word = 'word'
    card.created_by = admin
    card.save()

    assert card.deck_id == 1


def test_cards_limit_complete_deck(admin):
    """
    The card complete field can't be less then zero
    """
    card = Card()
    card.word = 'word'
    card.complete = 122
    card.created_by = admin
    card.deck_id = 1
    card.save()

    assert card.complete == 100

    card.complete = -23
    card.save()
    assert card.complete == 0


def test_cards_list_by_user(client):
    """
    Should return 401 error code for non authenticated users
    """
    response = client.get(reverse('cards-list'))
    assert response.status_code == 401


def test_cards_list_by_admin(admin_client):
    """
    Should return the cards list
    """
    response = admin_client.get(reverse('cards-list') + '?ordering=id')
    assert response.status_code == 200
    data = response.json()['results']
    assert len(data) == 2
    assert data[0]['definition'] == 'word one definition'


def test_cards_list_word_starts_with(admin_client, admin):
    """
    Should search a word by the query
    """
    Card.objects.create(word='ord', created_by=admin, deck_id=1)
    response = admin_client.get(
        reverse('cards-list') + '?word_starts=ord&ordering=id')
    assert response.status_code == 200
    data = response.json()['results']
    assert len(data) == 1
    assert data[0]['word'] == 'ord'


def test_cards_list_filter_by_admin(admin_client):
    """
    Should return the filtered cards list
    """
    response = admin_client.get(
        reverse('cards-list') + '?ordering=id&complete__lte=20')

    assert response.status_code == 200
    data = response.json()['results']
    assert len(data) == 1
    assert data[0]['complete'] == 20

    response = admin_client.get(
        reverse('cards-list') + '?ordering=id&complete__gte=40')

    assert response.status_code == 200
    data = response.json()['results']
    assert len(data) == 1
    assert data[0]['complete'] == 50


def test_cards_display_by_user(client):
    """
    Should return 401 error code for non authenticated users
    """
    response = client.get(reverse('cards-detail', args=[2]))
    assert response.status_code == 401


def test_cards_display_by_admin(admin_client):
    """
    Should return a word entry
    """
    response = admin_client.get(reverse('cards-detail', args=[2]))
    assert response.status_code == 200
    assert response.json()['word'] == 'word two'


def test_cards_display_another_user_by_admin(admin_client):
    """
    Should return 404 error code for non authenticated users
    """
    response = admin_client.get(reverse('cards-detail', args=[3]))
    assert response.status_code == 404


def test_cards_create_by_admin(admin_client):
    """
    Should create a word entry
    """
    data = json.dumps({
        'word': 'new test word',
        'deck': 1,
        'definition': 'test word definition',
        'remote_image': 'https://via.placeholder.com/550x400'
    })
    response = admin_client.post(reverse('cards-list'),
                                 data=data,
                                 content_type="application/json")
    data = response.json()

    assert data['word'] == 'new test word'
    assert data['created_by'] == 'admin'
    assert data['deck'] == 1
    assert '.png' in data['image']

    response = admin_client.get(reverse('cards-list'))
    assert len(response.json()['results']) == 3

    card = Card.objects.get(pk=data['id'])
    os.remove(card.image.path)


def test_cards_images_by_user(client):
    """
    Should return an authentication error
    """
    response = client.get(reverse('cards-images'))
    assert response.status_code == 401


def test_cards_images_by_admin(admin_client, mocker):
    """
    Should return a JSON response with images information
    """
    with mocker.patch(
            'cards.views.get_images',
            mocker.MagicMock(
                return_value={'error': 'The word parameter not found.'})):
        response = admin_client.get(reverse('cards-images'))
        assert response.status_code == 200
        assert response.json()['error'] == 'The word parameter not found.'

    with mocker.patch(
            'cards.views.get_images',
            mocker.MagicMock(return_value=[{
                'previewURL': 'image1.png'
            }, {
                'previewURL': 'image2.png'
            }, {
                'previewURL': 'image3.png'
            }])):

        response = admin_client.get(reverse('cards-images') + '?word=dog')
        assert response.status_code == 200
        assert len(response.json()) == 3
        assert response.json()[0]['previewURL'] == 'image1.png'


def test_cards_translation_by_user(client):
    """
    Should return an authentication error
    """
    response = client.get(reverse('cards-translation'))
    assert response.status_code == 401


def test_cards_translation_by_admin(admin_client, admin):
    """
    Should return a word translations
    """
    response = admin_client.get(reverse('cards-translation'))
    assert response.status_code == 200
    assert response.json()['error'] == 'The word parameter not found.'

    response = admin_client.get(reverse('cards-translation') + '?word=dog')
    assert response.status_code == 200
    assert response.json()['error'] == 'The language parameter not found.'

    settings = Settings.objects.get_by_user(admin)
    settings.language = 'ru'
    settings.save()

    response = admin_client.get(reverse('cards-translation') + '?word=dog')
    assert response.status_code == 200
    assert 'собака' in response.json()['translation']


def test_cards_synonyms_by_user(client):
    """
    Should return an authentication error
    """
    response = client.get(reverse('cards-synonyms'))
    assert response.status_code == 401


def test_cards_synonyms_by_admin(admin_client, mocker):
    """
    Should return a JSON response with the synonyms information
    """

    with mocker.patch(
            'cards.views.get_synonyms',
            mocker.MagicMock(
                return_value={'error': 'The word parameter not found.'})):
        response = admin_client.get(reverse('cards-synonyms'))
        assert response.status_code == 200
        assert response.json()['error'] == 'The word parameter not found.'

    with mocker.patch(
            'cards.views.get_synonyms',
            mocker.MagicMock(return_value={
                'synonyms': 'beloved, word',
                'antonyms': 'hate, word'
            })):
        response = admin_client.get(reverse('cards-synonyms') + '?word=love')
        assert response.status_code == 200
        assert 'beloved' in response.json()['synonyms']
        assert 'hate' in response.json()['antonyms']


def test_cards_definition_by_user(client):
    """
    Should return an authentication error
    """
    response = client.get(reverse('cards-definition'))
    assert response.status_code == 401


def test_cards_definition_by_admin(admin_client, mocker):
    """
    Should return a JSON response with a definition
    """
    with mocker.patch(
            'cards.views.get_defenition',
            mocker.MagicMock(
                return_value={'error': 'The word parameter not found.'})):
        response = admin_client.get(reverse('cards-definition'))
        assert response.status_code == 200
        assert response.json()['error'] == 'The word parameter not found.'

    with mocker.patch(
            'cards.views.get_defenition',
            mocker.MagicMock(
                return_value={
                    'pronunciation': 'test.wav',
                    'examples': '*dog*',
                    'definition': 'favorite animal',
                    'transcription': 'ˈdɑ:g',
                })):
        response = admin_client.get(reverse('cards-definition') + '?word=dog')
        assert response.status_code == 200
        assert '.wav' in response.json()['pronunciation']
        assert '*dog*' in response.json()['examples']
        assert 'animal' in response.json()['definition']
        assert "ˈdɑ:g" in response.json()['transcription']


def test_cards_lesson_by_user(client):
    """
    Should return an authentication error
    """
    response = client.get(reverse('cards-lesson'))
    assert response.status_code == 401


def test_cards_lesson_ordered(admin_client, admin):
    """
    Should return the ordered word list
    """
    settings = Settings.objects.get_by_user(admin)
    settings.cards_per_lesson = 1
    settings.save()
    response = admin_client.get(
        reverse('cards-lesson') + '?deck=1&ordering=-priority')
    assert response.status_code == 200
    data_ordered = response.json()

    assert min([d['priority'] for d in data_ordered]) > 1


def test_cards_lesson_complete_gte(admin_client):
    """
    Should return the word list filtered by the complete field
    """
    response = admin_client.get(
        reverse('cards-lesson') + '?deck=1&complete__gte=49&ordering=invalid')
    assert response.status_code == 200
    data = response.json()

    assert min([d['complete'] for d in data]) > 49


def test_cards_lesson_complete_lte(admin_client):
    """
    Should return the word list filtered by the complete field
    """
    response = admin_client.get(
        reverse('cards-lesson') + '?deck=1&complete__lte=30&ordering=invalid')
    assert response.status_code == 200
    data = response.json()

    assert max([d['complete'] for d in data]) < 30


def test_cards_lesson_category(admin_client, admin):
    """
    Should return the lesson list filtered by the category field
    """
    Card.objects.create(word='new word',
                        created_by=admin,
                        deck_id=1,
                        category='phrase')
    response = admin_client.get(
        reverse('cards-lesson') + '?deck=1&category=phrase')
    assert response.status_code == 200
    data = response.json()
    categories = {d['category'] for d in data}
    assert len(categories) == 1
    assert categories.pop() == 'phrase'


def test_cards_lesson_latest_days(admin_client, admin):
    """
    Should return the lesson list filtered by the is_latest field
    """
    settings = Settings.objects.get_by_user(admin)
    settings.lesson_latest_days = 1
    settings.save()

    Card.objects.create(word='new word', created_by=admin, deck_id=1)
    Card.objects.create(word='completed word',
                        created_by=admin,
                        complete=100,
                        deck_id=1)

    response = admin_client.get(reverse('cards-lesson') + '?is_latest=1')
    assert response.status_code == 200
    data_latest = response.json()

    words = [d['word'] for d in data_latest]
    words.sort()

    assert len(data_latest) == 4
    assert set(words) == {'completed word', 'new word'}


def test_cards_lesson_by_admin(admin_client):
    """
    Should return the lesson list
    """
    response = admin_client.get(reverse('cards-lesson') + '?deck=1')
    assert response.status_code == 200
    data_one = response.json()

    response = admin_client.get(reverse('cards-lesson') + '?deck=1')
    assert response.status_code == 200
    data_two = response.json()

    assert len(data_one) == 6
    assert len(data_two) == 6
    assert data_one[0]['word'] in data_one[0]['choices']
    assert data_one != data_two


def test_cards_lesson_not_include_completed_cards(admin_client, admin):
    """
    Should return the lesson list without the completed words
    """
    settings = Settings.objects.get_by_user(admin)
    settings.cards_to_repeat = 0
    settings.save()
    Card.objects.create(word='new word', created_by=admin, deck_id=1)
    Card.objects.create(word='completed word',
                        created_by=admin,
                        complete=100,
                        deck_id=1)
    response = admin_client.get(reverse('cards-lesson') + '?deck=1')
    assert response.status_code == 200
    data = response.json()

    assert max([d['complete'] for d in data]) < 100
