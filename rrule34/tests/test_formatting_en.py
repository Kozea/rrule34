from datetime import date, datetime

from dateutil.rrule import (
    DAILY, HOURLY, MINUTELY, MONTHLY, SECONDLY, WEEKLY, YEARLY, rrule)

from ..formatting import format_rrule


def rr(include_start_date=False, date_verbosity='full', **rr):
    return format_rrule(
        rrule(**rr), lang='en_US',
        include_start_date=include_start_date, date_verbosity=date_verbosity)


def test_every_rrules():
    assert rr(freq=SECONDLY) == 'Every second'
    assert rr(freq=MINUTELY) == 'Every minute'
    assert rr(freq=HOURLY) == 'Every hour'
    assert rr(freq=DAILY) == 'Every day'
    assert rr(freq=WEEKLY) == 'Every week'
    assert rr(freq=MONTHLY) == 'Every month'
    assert rr(freq=YEARLY) == 'Every year'


def test_every_n_rrules():
    assert rr(freq=DAILY, interval=1) == 'Every day'
    assert rr(freq=DAILY, interval=2) == 'Every 2 days'
    assert rr(freq=MONTHLY, interval=2) == 'Every 2 months'
    assert rr(freq=DAILY, interval=23412) == 'Every 23412 days'


def test_every_since():
    assert rr(
        include_start_date=True,
        freq=MINUTELY, dtstart=datetime(2000, 1, 2, 12)) == (
            'Every minute since Sunday, January 2, 2000 at '
            '12:00:00 PM GMT+00:00')

    assert rr(
        include_start_date=True, date_verbosity='short',
        freq=MINUTELY, dtstart=datetime(2000, 1, 2, 12)) == (
            'Every minute since 1/2/00, 12:00 PM')


def test_every_until():
    assert rr(
        freq=YEARLY, until=date(2030, 12, 25)) == (
        'Every year until Wednesday, '
        'December 25, 2030 at 12:00:00 AM GMT+00:00')

    assert rr(
        freq=YEARLY, until=datetime(2030, 12, 25, 11, 25)) == (
        'Every year until Wednesday, '
        'December 25, 2030 at 11:25:00 AM GMT+00:00')


def test_every_since_until():
    assert rr(
        include_start_date=True,
        freq=YEARLY, dtstart=datetime(2000, 1, 2, 12),
        until=datetime(2030, 12, 25, 11, 25)) == (
        'Every year since Sunday, January 2, 2000 at 12:00:00 PM GMT+00:00 '
        'until Wednesday, December 25, 2030 at 11:25:00 AM GMT+00:00')

    assert rr(
        include_start_date=True, date_verbosity='short',
        freq=YEARLY, dtstart=datetime(2000, 1, 2, 12),
        until=datetime(2030, 12, 25, 11, 25)) == (
        'Every year since 1/2/00, 12:00 PM until 12/25/30, 11:25 AM')


def test_every_count():
    assert rr(freq=DAILY, count=1) == 'Every day only once'
    assert rr(freq=DAILY, count=12) == 'Every day only 12 times'


def test_every_bymonth():
    assert rr(freq=YEARLY, bymonth=3) == 'Every year on March'
    assert rr(freq=YEARLY, bymonth=11) == 'Every year on November'
    assert rr(freq=YEARLY, bymonth=(1, 3)) == 'Every year on January and March'
    assert rr(freq=YEARLY, bymonth=(1, 3, 12)) == (
        'Every year on January, March and December')
