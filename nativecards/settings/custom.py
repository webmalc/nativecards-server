"""
Custom setting for nativecards project
"""
from .env import ENV

NC_IMAGE_WIDTH = ENV.int('NC_IMAGE_WIDTH')

NC_ATTEMPTS_TO_REMEMBER = ENV.int('NC_ATTEMPTS_TO_REMEMBER')

NC_CARDS_PER_LESSON = ENV.int('NC_CARDS_PER_LESSON')

NC_CARDS_TO_REPEAT = ENV.int('NC_CARDS_TO_REPEAT')

NC_LESSON_LATEST_DAYS = ENV.int('NC_LESSON_LATEST_DAYS')

NC_LESSONS_PER_DAY = ENV.int('NC_LESSONS_PER_DAY')

NC_CARDS_REPEAT_IN_LESSON = ENV.int('NC_CARDS_REPEAT_IN_LESSON')

NC_PIXABAY_KEY = ENV.str('NC_PIXABAY_KEY')

NC_OXFORD_ID = ENV.str('NC_OXFORD_ID')

NC_OXFORD_KEY = ENV.str('NC_OXFORD_KEY')

NC_WEBSTER_LEARNERS_KEY = ENV.str('NC_WEBSTER_LEARNERS_KEY')

NC_BIGHUGELABS_KEY = ENV.str('NC_BIGHUGELABS_KEY')