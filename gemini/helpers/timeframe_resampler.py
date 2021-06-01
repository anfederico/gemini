import logging

logger = logging.getLogger(__name__)


def resample(data, period='D'):
    """
    Return resampled dataframe

    Allowed periods:
    * T - minute (15T - 15 minutes),
    * H - hour,
    * D - day,
    * W - week,
    * M - month

    :param data:
    :param period:
    :return:
    """

    if period[-1:] not in ['T', 'H', 'D', 'W', 'M']:
        logger.warning('Unknown period for resample: %s', period)
        return data

    data = data.resample(period).apply({
        'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last',
        'volume': 'sum',
    }).dropna()
    data['date'] = data.index

    return data
