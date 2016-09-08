from datetime import date

from babel.dates import format_datetime, format_date
from dateutil.rrule import (
    DAILY, HOURLY, MINUTELY, MONTHLY, SECONDLY, WEEKLY, YEARLY, rrule)


class Word(object):
    def __init__(self, word, genre=None, plural=None):
        self.word = word
        self.plural = plural or self.get_default_plural()
        self.genre = genre

    def get_default_plural(self):
        return self.word + 's'

    def __str__(self):
        return self.word


class LangCollection(type):
    languages = {}

    def __new__(mcs, *args, **kwargs):
        cls = super().__new__(mcs, *args, **kwargs)
        if cls.__name__ != 'Lang':
            mcs.languages[cls.__name__] = cls
        return cls

    def __getitem__(cls, name):
        return cls.languages.get(name, 'en_US')()


class Lang(object, metaclass=LangCollection):
    def format_rrule(self, freq, until, count, interval,
                     by_rules, wkst, dtstart, tzinfo, include_start_date,
                     date_verbosity):

        parts = []
        parts.append(self.every(freq, interval))
        if include_start_date:
            parts.append(self.since(dtstart, tzinfo, date_verbosity))
        if until:
            parts.append(self.until(until, date_verbosity))

        for by, values in by_rules.items():
            if values:
                parts.append(self.by(by, values))

        if count:
            parts.append(self.count(count))

        return ' '.join(parts)


class en_US(Lang):
    FREQUENCIES = {
        SECONDLY: Word('second'),
        MINUTELY: Word('minute'),
        HOURLY: Word('hour'),
        DAILY: Word('day'),
        WEEKLY: Word('week'),
        MONTHLY: Word('month'),
        YEARLY: Word('year'),
    }

    def join_list(self, it):
        if len(it) == 1:
            return it[0]
        return ' and '.join(
            [', '.join(it[:-1]), it[-1]])

    def every(self, freq, interval):
        word = self.FREQUENCIES.get(freq)
        if interval > 1:
            return 'Every %s %s' % (interval, word.plural)
        return 'Every %s' % word

    def count(self, count):
        if count == 1:
            return 'only once'
        if count == 2:
            return 'only twice'
        return 'only %d times' % count

    def since(self, dtstart, tzinfo, date_verbosity):
        return 'since %s' % format_datetime(
            dtstart, date_verbosity, tzinfo=tzinfo,
            locale=self.__class__.__name__)

    def until(self, until, date_verbosity):
        return 'until %s' % format_datetime(
            until, date_verbosity,
            locale=self.__class__.__name__)

    def by(self, by, values):
        if by == 'bymonth':
            return 'on %s' % self.join_list([
                format_date(date(2000, month, 1), 'MMMM',
                            locale=self.__class__.__name__)
                for month in values
            ])
        return ''


class fr_FR(Lang):
    MASCULIN = object()
    FEMININ = object()

    FREQUENCIES = {
        SECONDLY: Word('seconde', FEMININ),
        MINUTELY: Word('minute', FEMININ),
        HOURLY: Word('heure', FEMININ),
        DAILY: Word('jour', MASCULIN),
        WEEKLY: Word('semaine', FEMININ),
        MONTHLY: Word('mois', MASCULIN, 'mois'),
        YEARLY: Word('an', MASCULIN),
    }

    def join_list(self, it):
        if len(it) == 1:
            return it[0]
        return ' et '.join(
            [', '.join(it[:-1]), it[-1]])

    def every(self, freq, interval):
        word = self.FREQUENCIES.get(freq)
        itvl = '%d ' % interval if interval > 1 else ''
        if word.genre is self.MASCULIN:
            return 'Tous les %s%s' % (itvl, word.plural)
        if word.genre is self.FEMININ:
            return 'Toutes les %s%s' % (itvl, word.plural)

    def count(self, count):
        if count == 1:
            return 'seulement 1 fois'
        return 'seulement %d fois' % count

    def since(self, dtstart, tzinfo, date_verbosity):
        return 'depuis le %s' % format_datetime(
            dtstart, date_verbosity, tzinfo=tzinfo,
            locale=self.__class__.__name__)

    def until(self, until, date_verbosity):
        return 'jusqu’au %s' % format_datetime(
            until, date_verbosity,
            locale=self.__class__.__name__)

    def by(self, by, values):
        if by == 'bymonth':
            return 'en %s' % self.join_list([
                format_date(date(2000, month, 1), 'MMMM',
                            locale=self.__class__.__name__)
                for month in values
            ])
        return ''


def format_rrule(
        rr, lang='en_US', include_start_date=False, date_verbosity='full'):
    return Lang[lang].format_rrule(
        rr._freq,
        rr._until,
        rr._count,
        rr._interval,
        rr._original_rule,
        rr._wkst,
        # From event
        rr._dtstart,
        rr._tzinfo,
        include_start_date=include_start_date,
        date_verbosity=date_verbosity
    )


def format_rruleset(rruleset_, lang='en_US', date_verbosity='full'):
    return ', '.join([
        format_rrule(rrule_, lang, True, date_verbosity)
        for rrule_ in rruleset_])
