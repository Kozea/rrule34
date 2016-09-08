from dateutil.rrule import (
    DAILY, HOURLY, MINUTELY, MONTHLY, SECONDLY, WEEKLY, YEARLY, rrule)
from datetime import datetime, date
from ..formatting import format_rrule


def rr(include_start_date=False, date_verbosity='full', **rr):
    return format_rrule(
        rrule(**rr), lang='fr_FR',
        include_start_date=include_start_date, date_verbosity=date_verbosity)


def test_every_rrules():
    assert rr(freq=SECONDLY) == 'Toutes les secondes'
    assert rr(freq=MINUTELY) == 'Toutes les minutes'
    assert rr(freq=HOURLY) == 'Toutes les heures'
    assert rr(freq=DAILY) == 'Tous les jours'
    assert rr(freq=WEEKLY) == 'Toutes les semaines'
    assert rr(freq=MONTHLY) == 'Tous les mois'
    assert rr(freq=YEARLY) == 'Tous les ans'


def test_every_n_rrules():
    assert rr(freq=DAILY, interval=1) == 'Tous les jours'
    assert rr(freq=DAILY, interval=2) == 'Tous les 2 jours'
    assert rr(freq=MONTHLY, interval=2) == 'Tous les 2 mois'
    assert rr(freq=DAILY, interval=23412) == 'Tous les 23412 jours'


def test_every_since():
    assert rr(
        include_start_date=True,
        freq=MINUTELY, dtstart=datetime(2000, 1, 2, 12)) == (
            'Toutes les minutes depuis le dimanche 2 janvier 2000 à 12:00:00 '
            'UTC+00:00')

    assert rr(
        include_start_date=True, date_verbosity='short',
        freq=MINUTELY, dtstart=datetime(2000, 1, 2, 12)) == (
        'Toutes les minutes depuis le 02/01/2000 12:00')


def test_every_until():
    assert rr(
        freq=YEARLY, until=date(2030, 12, 25)) == (
        'Tous les ans jusqu’au mercredi 25 décembre 2030 à 00:00:00 UTC+00:00')

    assert rr(
        freq=YEARLY, until=datetime(2030, 12, 25, 11, 25)) == (
        'Tous les ans jusqu’au mercredi 25 décembre 2030 à 11:25:00 UTC+00:00')


def test_every_since_until():
    assert rr(
        include_start_date=True,
        freq=YEARLY, dtstart=datetime(2000, 1, 2, 12),
        until=datetime(2030, 12, 25, 11, 25)) == (
        'Tous les ans depuis le dimanche 2 janvier 2000 à 12:00:00 '
        'UTC+00:00 jusqu’au mercredi 25 décembre 2030 à 11:25:00 UTC+00:00')

    assert rr(
        include_start_date=True, date_verbosity='short',
        freq=YEARLY, dtstart=datetime(2000, 1, 2, 12),
        until=datetime(2030, 12, 25, 11, 25)) == (
        'Tous les ans depuis le 02/01/2000 12:00 jusqu’au 25/12/2030 11:25')
