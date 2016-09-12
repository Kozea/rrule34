from datetime import date, time

from babel.dates import (
    format_date, format_datetime, format_time, get_day_names, get_month_names)
from dateutil.rrule import (
    DAILY, HOURLY, MINUTELY, MONTHLY, SECONDLY, WEEKLY, YEARLY)


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
    def format_rrule(
            self, rr, include_start_date=False, date_verbosity='full'):
        freq = rr._freq
        until = rr._until
        count = rr._count
        interval = rr._interval
        by_rules = rr._original_rule
        by_timeset = rr._timeset
        wkst = rr._wkst
        # From event
        dtstart = rr._dtstart
        tzinfo = rr._tzinfo
        if not hasattr(self, 'date_verbosity'):
            self.date_verbosity = date_verbosity

        parts = []
        parts.append(self.every(freq, interval))
        if include_start_date:
            parts.append(self.since(dtstart, tzinfo))
        if until:
            parts.append(self.until(until))

        for by in (
                'bysetpos', 'bymonth', 'bymonthday', 'byyearday', 'byweekno',
                'byweekday', 'byeaster'):
            values = by_rules.get(by)
            if values:
                parts.append(self.by(by, sorted([
                    getattr(v, 'weekday', v) for v in values])))

        if by_timeset:
            self.by_timeset(by_timeset)

        if count:
            parts.append(self.count(count))

        return ' '.join(parts)

    def format_rruleset(
            self, rrs, include_start_date=True, date_verbosity='full'):
        self.date_verbosity = date_verbosity

        rrules = [
            self.format_rrule(rr,
                include_start_date=include_start_date
            ) for rr in rrs._rrule]
        rdates = [self.format_dt(rdate) for rdate in rrs._rdate]
        exrules = [
            self.format_rrule(xr,
                include_start_date=include_start_date,
            ) for xr in rrs._exrule]
        exdates = [self.format_dt(exdate)for exdate in rrs._exdate]

        return self.join_set(rrules, rdates, exrules, exdates)


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

    def format_dt(self, dt, tzinfo=None):
        dtstr = format_datetime(
            dt, format=self.date_verbosity, locale='en_US', tzinfo=tzinfo)
        if (tzinfo or dt.tzinfo) is None:
            if self.date_verbosity == 'full':
                dtstr = dtstr.replace(' GMT+00:00', '')
            elif self.date_verbosity == 'long':
                dtstr = dtstr.replace(' +0000', '')
        return dtstr

    def join_list(self, it):
        it = list(map(str, it))
        if not len(it):
            return ''
        if len(it) == 1:
            return it[0]
        return ' and '.join(
            [', '.join(it[:-1]), it[-1]])

    def nth(self, number):
        if 10 < number < 14:
            return '%dth' % number
        if number % 10 == 1:
            return '%dst' % number
        if number % 10 == 2:
            return '%dnd' % number
        if number % 10 == 3:
            return '%drd' % number
        return '%dth' % number

    def every(self, freq, interval):
        word = self.FREQUENCIES.get(freq)
        if interval > 1:
            return 'every %s %s' % (interval, word.plural)
        return 'every %s' % word

    def count(self, count):
        if count == 1:
            return 'only once'
        if count == 2:
            return 'only twice'
        return 'only %d times' % count

    def since(self, dtstart, tzinfo):
        return 'since %s' % self.format_dt(dtstart, tzinfo)

    def until(self, until):
        return 'until %s' % self.format_dt(until)

    def by(self, by, values):
        if by == 'bysetpos':
            before = [-v for v in reversed(values) if v < 0]
            after = [v for v in values if v > 0]
            parts = []
            t = 0
            if after:
                if len(after) == 1 and after[0] == 1:
                    parts.append('the first')
                    t += 1
                else:
                    parts.append(
                        'the %s first' %
                        self.join_list([self.nth(val) for val in after]))
                    t += 2
            if before:
                if len(before) == 1 and before[0] == 1:
                    parts.append('the last')
                    t += 1
                else:
                    parts.append(
                        'the %s last' %
                        self.join_list([self.nth(val) for val in before]))
                    t += 2

            return ' and '.join(parts) + ' occurence%s' % (
                's' if t != 1 else '')

        if by == 'bymonth':
            return 'on %s' % self.join_list([
                get_month_names(locale=self.__class__.__name__)[month]
                for month in values
            ])

        if by == 'bymonthday':
            return 'the %s of month' % self.join_list(values)

        if by == 'byyearday':
            return 'the %s of year' % self.join_list(values)

        if by == 'byweekno':
            return 'the week%s n°%s' % (
                's' if len(values) > 1 else '',
                self.join_list(values))

        if by == 'byweekday':
            dow = get_day_names(locale=self.__class__.__name__)

            return 'on %s' % self.join_list([
                 dow[val] for val in values
            ])

        if by == 'byeaster':
            before = [-v for v in reversed(values) if v < 0]
            after = [v for v in values if v > 0]
            parts = []
            if before:
                if len(before) == 1 and before[0] == 1:
                    parts.append('1 day before Easter')
                else:
                    parts.append(
                        '%s days before Easter' % self.join_list(before))
            if after:
                if len(after) == 1 and before[0] == 1:
                    parts.append('1 day after Easter')
                else:
                    parts.append(
                        '%s days after Easter' % self.join_list(after))

            return ' and '.join(parts)

    def by_timeset(self, by_timeset):
        return 'at %s' % self.join_list([
             format_time(val, locale=self.__class__.__name__)
             for val in by_timeset
        ])

    def join_set(self, rrules, rdates, exrules, exdates):
        parts = []
        parts.extend(rrules)
        parts.extend(['on %s' % rd for rd in rdates])
        parts.extend(['except %s' % xr for xr in exrules])
        parts.extend(['except on %s' % xd for xd in exdates])
        return self.join_list(parts)


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

    def format_dt(self, dt, tzinfo=None):
        dtstr = format_datetime(
            dt, format=self.date_verbosity, locale='fr_FR', tzinfo=tzinfo)
        if (tzinfo or dt.tzinfo) is None:
            if self.date_verbosity == 'full':
                dtstr = dtstr.replace(' UTC+00:00', '')
            elif self.date_verbosity == 'long':
                dtstr = dtstr.replace(' +0000', '')
        return dtstr

    def join_list(self, it):
        it = list(map(str, it))
        if not len(it):
            return ''
        if len(it) == 1:
            return it[0]
        return ' et '.join(
            [', '.join(it[:-1]), it[-1]])

    def nth(self, number, genre=MASCULIN):
        if number == 1:
            return '1er' if genre is self.MASCULIN else '1ère'
        return '%dème' % number

    def every(self, freq, interval):
        word = self.FREQUENCIES.get(freq)
        itvl = '%d ' % interval if interval > 1 else ''
        if word.genre is self.MASCULIN:
            return 'tous les %s%s' % (itvl, word.plural)
        if word.genre is self.FEMININ:
            return 'toutes les %s%s' % (itvl, word.plural)

    def count(self, count):
        if count == 1:
            return 'seulement 1 fois'
        return 'seulement %d fois' % count

    def since(self, dtstart, tzinfo):
        return 'depuis le %s' % self.format_dt(dtstart, tzinfo)

    def until(self, until):
        return 'jusqu’au %s' % self.format_dt(until)

    def by(self, by, values):
        if by == 'bysetpos':
            before = [-v for v in reversed(values) if v < 0]
            after = [v for v in values if v > 0]
            parts = []
            t = 0
            if after:
                if len(after) == 1:
                    parts.append('la %s' % self.nth(after[0], self.FEMININ))
                    t += 1
                else:
                    t += 2
                    parts.append(
                    'les %s premières' %
                    self.join_list([self.nth(val) for val in after]))
            if before:
                if len(before) == 1:
                    if before[0] == 1:
                        parts.append('la dernière')
                    else:
                        parts.append(
                            'l’%sdernière' % ('avant-' * (before[0] - 1)))
                    t += 1
                else:
                    t += 2
                    parts.append(
                        'les %s dernières' %
                        self.join_list([self.nth(val) for val in before]))

            return ' et '.join(parts) + ' occurence%s' % (
                's' if t != 1 else '')

        if by == 'bymonth':
            return 'en %s' % self.join_list([
                get_month_names(locale=self.__class__.__name__)[month]
                for month in values
            ])
        if by == 'bymonthday':
            if len(values) == 1:
                return 'le %s jour du mois' % self.nth(val)
            return 'les %s jours du mois' % self.join_list(
                [self.nth(val) for val in values])

        if by == 'byyearday':
            if len(values) == 1:
                return 'le %s jour de l’année' % self.nth(val)
            return 'les %s jours de l’année' % self.join_list(
                [self.nth(val) for val in values])

        if by == 'byweekno':
            if len(values) == 1:
                return 'la semaine n°%d' % values[0]
            return 'les semaines n°%s' % self.join_list(values)

        if by == 'byweekday':
            dow = get_day_names(locale=self.__class__.__name__)

            return 'le %s' % self.join_list([
                 dow[val] for val in values
            ])

        if by == 'byeaster':
            before = [-v for v in reversed(values) if v < 0]
            after = [v for v in values if v > 0]
            parts = []
            if before:
                if len(before) == 1 and before[0] == 1:
                    parts.append('la veille de Pâques')
                else:
                    parts.append(
                        '%s jours avant Pâques' % self.join_list(before))
            if after:
                if len(after) == 1 and after[0] == 1:
                    parts.append('le lendemain de Pâques')
                else:
                    parts.append('%s jours après Pâques' % self.join_list(after))

            return ' et '.join(parts)

    def by_timeset(self, by_timeset):
        return 'à %s' % self.join_list([
             format_time(val, locale=self.__class__.__name__)
             for val in by_timeset
        ])

    def join_set(self, rrules, rdates, exrules, exdates):
        parts = []
        parts.extend(rrules)
        parts.extend(['le %s' % rd for rd in rdates])
        parts.extend(['sauf %s' % xr for xr in exrules])
        parts.extend(['sauf le %s' % xd for xd in exdates])
        return self.join_list(parts)


def capitalize(s):
    if not len(s):
        return ''
    if len(s) == 1:
        return s.upper()
    return s[0].upper() + s[1:]


def format_rrule(rr, locale='en_US', **kwargs):
    return capitalize(Lang[locale].format_rrule(rr, **kwargs))


def format_rruleset(rrs, locale='en_US', **kwargs):
    return capitalize(Lang[locale].format_rruleset(rrs, **kwargs))
