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
    def format_rrule(self, freq, until, count, interval,
                     by_rules, by_timeset, wkst, dtstart, tzinfo,
                     include_start_date, date_verbosity):

        parts = []
        parts.append(self.every(freq, interval))
        if include_start_date:
            parts.append(self.since(dtstart, tzinfo, date_verbosity))
        if until:
            parts.append(self.until(until, date_verbosity))

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
        it = list(map(str, it))
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
        it = list(map(str, it))
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

def format_rrule(
        rr, lang='en_US', include_start_date=False, date_verbosity='full'):
    return Lang[lang].format_rrule(
        rr._freq,
        rr._until,
        rr._count,
        rr._interval,
        rr._original_rule,
        rr._timeset,
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
