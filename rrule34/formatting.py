from dateutil.rrule import WEEKLY, rrule, rruleset
from . import i18n


def format_rrule(rrule_, language='en_US'):
    # Frequence
    lang = getattr(i18n, language)()
    return lang.every(rrule_._freq)


def format_rruleset(rruleset_):
    return ', '.join([format_rrule(rrule_) for rrule_ in rruleset_])
