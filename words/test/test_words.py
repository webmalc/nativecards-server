"""
The words test module
"""
import pytest

from nativecards.lib.dicts.models import DictionaryEntry
from words.models import Word

pytestmark = pytest.mark.django_db  # pylint: disable=invalid-name


def test_word_create_or_update():
    """
    Should create and update the word object
    """
    not_word = Word.objects.create_or_update('test')
    word = Word.objects.create_or_update(
        'test',
        translation='trans',
        language='es',
    )
    word_pk = word.pk
    dict_entry = DictionaryEntry(
        'definition',
        'examples',
        'pronunciation',
        'transcription',
    )
    word_update = Word.objects.create_or_update(
        'test',
        synonyms='one, two',
        antonyms='two, one',
        entry=dict_entry,
    )

    assert not_word is None
    assert word.translations == {'es': 'trans'}
    assert word.synonyms is None
    assert word_update.pk == word_pk
    assert word_update.synonyms == 'one, two'
    assert word_update.antonyms == 'two, one'
    assert word_update.definition == 'definition'
    assert word_update.examples == 'examples'
    assert word_update.pronunciation == 'pronunciation'
    assert word_update.transcription == 'transcription'


def test_word_guess_category():
    """
    Should guess and set the word category
    """
    word = Word()
    word.word = 'word'
    word.save()

    assert word.category == 'word'

    word = Word()
    word.word = 'come up with'
    word.save()

    assert word.category == 'phrasal_verb'

    word = Word()
    word.word = 'get over'
    word.save()

    assert word.category == 'phrasal_verb'

    word = Word()
    word.word = 'to put it mildly'
    word.save()

    assert word.category == 'phrase'
