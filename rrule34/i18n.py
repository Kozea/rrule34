"""Cheap i18n"""

from dateutil.rrule import (
    DAILY, HOURLY, MINUTELY, MONTHLY, SECONDLY, WEEKLY, YEARLY, rrule)


class Word(object):
    def __init__(self, word, genre=None, plural=None):
        self.word = word
        self.plural = plural or self.get_default_plural()
        self.genre = genre

    def get_default_plural(self):
        return self.word + 's'


class en_US(object):
    FREQUENCIES = {
        SECONDLY: Word('second'),
        MINUTELY: Word('minute'),
        HOURLY: Word('hour'),
        DAILY: Word('day'),
        WEEKLY: Word('week'),
        MONTHLY: Word('month'),
        YEARLY: Word('year'),
    }

    def every(self, freq):
        word = self.FREQUENCIES.get(freq)
        return 'Every %s' % word.plural


class fr_FR(object):
    MASCULIN = object()
    FEMININ = object()

    FREQUENCIES = {
        SECONDLY: Word('seconde', FEMININ),
        MINUTELY: Word('minute', FEMININ),
        HOURLY: Word('heure', FEMININ),
        DAILY: Word('jour', MASCULIN),
        WEEKLY: Word('semaine', FEMININ),
        MONTHLY: Word('mois', MASCULIN, 'mois'),
        YEARLY: Word('ans', MASCULIN),
    }

    def every(self, freq):
        word = self.FREQUENCIES.get(freq)
        if word.genre is self.MASCULIN:
            return 'Tous les %s' % word.plural
        if word.genre is self.FEMININ:
            return 'Toutes les %s' % word.plural
