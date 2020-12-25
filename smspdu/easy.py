# coding: utf-8
# Copyright (c) Qotto, 2018-2019
# Open-source software, see LICENSE file for details

from .fields import SMSDeliver
from io import StringIO

from typing import Any, Dict

__all__ = ['easy_sms']

def easy_sms(data: str) -> Dict[str, Any]:
    sms = SMSDeliver.decode(StringIO(data))
    sender = sms['sender']['number']
    if sms['sender']['toa']['ton'] == 'international':
        sender = '+' + sender
    date = sms['scts']
    content = sms['user_data']['data']
    header = sms['user_data'].get('header')
    partial: Any = False
    if header:
        for element in header.get('elements', list()):
            if element['iei'] in [0x00, 0x08]:
                el_data = element['data']
                partial = {
                    'reference': f"{el_data['reference']}-{el_data['parts_count']}",
                    'parts_count': el_data['parts_count'],
                    'part_number': el_data['part_number'],
                }
    return {
        'sender': sender,
        'date': date,
        'content': content,
        'partial': partial,
    }
