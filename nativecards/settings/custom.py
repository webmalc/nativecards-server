"""
Custom setting for nativecards project
"""
from .env import ENV

NC_DICTIONARIES = [
    'nativecards.lib.dicts.webster_learners.WebsterLearners',
    'nativecards.lib.dicts.free_dictionary.FreeDictionary',
]
NC_TRANSLATORS = [
    'nativecards.lib.trans.Lingualeo',
    'nativecards.lib.trans.GoogleTrans',
]

NC_FILES_DOMAIN = ENV.str('NC_FILES_DOMAIN')

NC_IMAGE_WIDTH = ENV.int('NC_IMAGE_WIDTH')

NC_ATTEMPTS_TO_REMEMBER = ENV.int('NC_ATTEMPTS_TO_REMEMBER')

NC_CARDS_PER_LESSON = ENV.int('NC_CARDS_PER_LESSON')

NC_CARDS_TO_REPEAT = ENV.int('NC_CARDS_TO_REPEAT')

NC_LESSON_LATEST_DAYS = ENV.int('NC_LESSON_LATEST_DAYS')

NC_LESSONS_PER_DAY = ENV.int('NC_LESSONS_PER_DAY')

NC_CARDS_REPEAT_IN_LESSON = ENV.int('NC_CARDS_REPEAT_IN_LESSON')

# API
NC_PIXABAY_KEY = ENV.str('NC_PIXABAY_KEY')

NC_WEBSTER_LEARNERS_KEY = ENV.str('NC_WEBSTER_LEARNERS_KEY')

NC_BIGHUGELABS_KEY = ENV.str('NC_BIGHUGELABS_KEY')
