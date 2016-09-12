from datetime import date, datetime

from dateutil.rrule import (
    DAILY, HOURLY, MINUTELY, MONTHLY, SECONDLY, WEEKLY, YEARLY, rrule,
    rruleset)

from ..formatting import format_rrule, format_rruleset


def rr(include_start_date=False, date_verbosity='full', **rr):
    return format_rrule(
        rrule(**rr), locale='fr_FR',
        include_start_date=include_start_date, date_verbosity=date_verbosity)


def rrs(rrs, include_start_date=False, date_verbosity='full'):
    return format_rruleset(
        rrs, locale='fr_FR',
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
            'Toutes les minutes depuis le dimanche 2 janvier 2000 à 12:00:00')

    assert rr(
        include_start_date=True, date_verbosity='short',
        freq=MINUTELY, dtstart=datetime(2000, 1, 2, 12)) == (
        'Toutes les minutes depuis le 02/01/2000 12:00')


def test_every_until():
    assert rr(
        freq=YEARLY, until=date(2030, 12, 25)) == (
        'Tous les ans jusqu’au mercredi 25 décembre 2030 à 00:00:00')

    assert rr(
        freq=YEARLY, until=datetime(2030, 12, 25, 11, 25)) == (
        'Tous les ans jusqu’au mercredi 25 décembre 2030 à 11:25:00')


def test_every_since_until():
    assert rr(
        include_start_date=True,
        freq=YEARLY, dtstart=datetime(2000, 1, 2, 12),
        until=datetime(2030, 12, 25, 11, 25)) == (
        'Tous les ans depuis le dimanche 2 janvier 2000 à 12:00:00 '
        'jusqu’au mercredi 25 décembre 2030 à 11:25:00')

    assert rr(
        include_start_date=True, date_verbosity='short',
        freq=YEARLY, dtstart=datetime(2000, 1, 2, 12),
        until=datetime(2030, 12, 25, 11, 25)) == (
        'Tous les ans depuis le 02/01/2000 12:00 jusqu’au 25/12/2030 11:25')


def test_every_count():
    assert rr(freq=DAILY, count=1) == 'Tous les jours seulement 1 fois'
    assert rr(freq=DAILY, count=12) == 'Tous les jours seulement 12 fois'


def test_every_bymonth():
    assert rr(freq=YEARLY, bymonth=3) == 'Tous les ans en mars'
    assert rr(freq=YEARLY, bymonth=11) == 'Tous les ans en novembre'
    assert rr(freq=YEARLY, bymonth=(1, 3)) == 'Tous les ans en janvier et mars'
    assert rr(freq=YEARLY, bymonth=(1, 3, 12)) == (
        'Tous les ans en janvier, mars et décembre')


def test_every_thing():
    assert rr(
        include_start_date=True, freq=MONTHLY,
        dtstart=datetime(2010, 1, 10, 10, 1, 10),
        until=datetime(2020, 2, 20, 20, 2, 20),
        bysetpos=(-4, -2, 1), bymonth=(2, 5, 11), bymonthday=(12, 15, 18, 20),
        byyearday=(12, 87, 350, 220), byweekno=(12, 13, 39),
        byweekday=(1, 2, 4, 5),
        byhour=(10, 15, 19), byminute=15, bysecond=(14, 29),
        byeaster=(-3, -2, 1)
    ) == (
        'Tous les mois depuis le dimanche 10 janvier 2010 à 10:01:10 '
        'jusqu’au jeudi 20 février 2020 à 20:02:20 la 1ère '
        'et les 2ème et 4ème dernières occurences en février, mai et novembre '
        'les 12ème, 15ème, 18ème et 20ème jours du mois les 12ème, 87ème, '
        '220ème et 350ème jours de l’année les semaines n°12, 13 et 39 '
        'le mardi, mercredi, vendredi et samedi 2 et 3 jours avant Pâques '
        'et le lendemain de Pâques')


def test_rrule_set():
    rrset = rruleset()
    rrset.rrule(rrule(freq=SECONDLY))
    assert rrs(rrset) == 'Toutes les secondes'
    rrset.rrule(rrule(freq=MONTHLY))
    assert rrs(rrset) == 'Toutes les secondes et tous les mois'
    rrset.rdate(datetime(2015, 5, 15, 15, 50, 25))
    assert rrs(rrset) == (
        'Toutes les secondes, tous les mois et le '
        'vendredi 15 mai 2015 à 15:50:25')
    rrset.exrule(rrule(freq=DAILY, byweekday=(1, 5)))
    assert rrs(rrset) == (
        'Toutes les secondes, tous les mois, le '
        'vendredi 15 mai 2015 à 15:50:25 et sauf '
        'tous les jours le mardi et samedi')
    rrset.exdate(datetime(2014, 4, 14, 14, 40, 24))
    assert rrs(rrset) == (
        'Toutes les secondes, tous les mois, le '
        'vendredi 15 mai 2015 à 15:50:25, sauf '
        'tous les jours le mardi et samedi et sauf le '
        'lundi 14 avril 2014 à 14:40:24')
