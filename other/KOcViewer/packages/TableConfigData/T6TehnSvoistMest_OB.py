#!/usr/bin/env python
# -*- coding: utf-8 -*-



def get_config():
    ordered_fields = [
        'Num_Rab',
        'NZUAREA',
        'NPRODGON',
        'NPOPGON',
        'NGON',
        'NUDSOPR',
        'NSNVP',
        'NSNVNOP',
        'NGSMP',
        'NGSMNOP',
        'NZTRPAH',
        'NZTRNOPAH',
        'NUDCUSF',
        'NUDCUS5',
        'NUDCUS4',
        'NUDCUS3',
        'NUDCUS2',
        'NUDCUS1',
        'NUDCUSE',
		'NUDCBRF',
		'NUDCBR5',
		'NUDCBR4',
		'NUDCBR3',
		'NUDCBR2',
		'NUDCBR1',
        'NUDCBRE'   
    ]
    return {
        'date_out_cell': u'A1',
        'rayon_out_cell': u'A2',
        'shz_out_cell': u'A3',
        'fields_to_validate': ordered_fields,
        'template_sheet_name': u'T6',
        'start_export_cell': u'A10',
        'data_configure_list': [
            {
                'header_title': u'Пахотные',
                'include_title': u'',
                'include_rowspan': 0,
                'db_fields': ordered_fields,
                'loaded_data': [],
               'where_cases': [
                    {'field': u'NLANDTYPE', 'value': 101},
                    {'field': u'NPRIZNAK', 'value': u'2'}
                ]
            },
            {
                'header_title': u'Под постоянными культурами',
                'include_title': u'',
                'include_rowspan': 0,
                'db_fields': ordered_fields,
                'loaded_data': [],
                'where_cases': [
                    {'field': u'NLANDTYPE', 'value': 102},
                    {'field': u'NPRIZNAK', 'value': '2'}
                ]
            },
            {
                'header_title': u'Луговые улучшенные',
                'include_title': u'',
                'include_rowspan': 0,
                'db_fields': ordered_fields,
                'loaded_data': [],
                'where_cases': [
                    {'field': u'NLANDTYPE', 'value': 103},
                    {'field': u'NPRIZNAK', 'value': '2'}
                ]
            },
            {
                'header_title': u'Всего по виду земель: Пахотные',
                'include_title': u'',
                'include_rowspan': 0,
                'db_fields': ordered_fields,
                'loaded_data': [],
                'where_cases': [
                    {'field': u'NLANDTYPE', 'value': 101},
                    {'field': u'NPRIZNAK', 'value': '7'}
                ]
            },
            {
                'header_title': u'',
                'include_title': u'в т.ч. осуш.',
                'include_rowspan': 3,
                'db_fields': ordered_fields[3:],
                'loaded_data': [],
                'where_cases': [
                    {'field': u'NPRIZNAK', 'value': '8'},
                    {'field': u'Vsego', 'value': u'Всего: Пахотные (в т.ч. осуш.)'}
                ]
            },
            {
                'header_title': u'Всего по виду земель: Под постоянными культурами',
                'include_title': u'',
                'include_rowspan': 0,
                'db_fields': ordered_fields,
                'loaded_data': [],
                'where_cases': [
                    {'field': u'NLANDTYPE', 'value': 102},
                    {'field': u'NPRIZNAK', 'value': '7'}
                ]
            },
            {
                'header_title': u'',
                'include_title': u'в т.ч. осуш.',
                'include_rowspan': 3,
                'db_fields': ordered_fields[3:],
                'loaded_data': [],
                'where_cases': [
                    {'field': u'NPRIZNAK', 'value': '8'},
                    {'field': u'Vsego', 'value': u'Всего: Под постоянными культурами (в т.ч. осуш.)'}
                ]
            },
            {
                'header_title': u'Всего по виду земель: Луговые улучшенные',
                'include_title': u'',
                'include_rowspan': 0,
                'db_fields': ordered_fields,
                'loaded_data': [],
                'where_cases': [
                    {'field': u'NLANDTYPE', 'value': 103},
                    {'field': u'NPRIZNAK', 'value': '7'}
                ]
            },
            {
                'header_title': u'',
                'include_title': u'в т.ч. осуш.',
                'include_rowspan': 3,
                'db_fields': ordered_fields[3:],
                'loaded_data': [],
                'where_cases': [
                    {'field': 'NPRIZNAK', 'value': '8'},
                    {'field': 'Vsego', 'value': u'Всего: Луговые улучшенные (в т.ч. осуш.)'}
                ]
            },
            {
                'header_title': u'Всего по обрабатываемым землям',
                'include_title': u'',
                'include_rowspan': 0,
                'db_fields': ordered_fields,
                'loaded_data': [],
                'where_cases': [
                    {'field': 'NPRIZNAK', 'value': '9'},
                    {'field': 'Vsego', 'value': u'Всего по обрабатываемым землям'}
                ]
            },
            {
                'header_title': u'',
                'include_title': u'в т.ч. осуш.',
                'include_rowspan': 3,
                'db_fields': ordered_fields[3:],
                'loaded_data': [],
                'where_cases': [
                    {'field': 'NPRIZNAK', 'value': '10'},
                    {'field': 'Vsego', 'value': u'Всего по обрабатываемым землям (в т.ч. осуш.)'}
                ]
            }
        ]
    }

