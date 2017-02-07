#!/usr/bin/env python
# -*- coding: utf-8 -*-



def get_config():
    ordered_fields = [
        'Num_Rab',
        'NZUAREA',
        'NZUAREAOS',
        'N0',
        'N1',
        'N2',
        'N3',
        'N4',
        'N5',
        'N6',
        'N7',
        'N9',
        'N10',
		'N11',
		'N12',
        'N14',
		'N15',
        'N17',
		'N18',
        'N19',
        'N20',
        'N21',
        'N22',
        'N23'   
    ]
    return {
        'date_out_cell': u'A1',
        'rayon_out_cell': u'A2',
        'shz_out_cell': u'A3',
        'fields_to_validate': ordered_fields,
        'template_sheet_name': u'T7',
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
                    {'field': 'NLANDTYPE', 'value': 102},
                    {'field': 'NPRIZNAK', 'value': '2'}
                ]
            },
            {
                'header_title': u'Луговые улучшенные',
                'include_title': u'',
                'include_rowspan': 0,
                'db_fields': ordered_fields,
                'loaded_data': [],
                'where_cases': [
                    {'field': 'NLANDTYPE', 'value': 103},
                    {'field': 'NPRIZNAK', 'value': '2'}
                ]
            },
            {
                'header_title': u'Всего по виду земель: Пахотные',
                'include_title': u'',
                'include_rowspan': 0,
                'db_fields': ordered_fields,
                'loaded_data': [],
                'where_cases': [
                    {'field': 'NLANDTYPE', 'value': 101},
                    {'field': 'NPRIZNAK', 'value': '7'}
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
                    {'field': 'Vsego', 'value': u'Всего: Пахотные (в т.ч. осуш.)'}
                ]
            },
            {
                'header_title': u'Всего по виду земель: Под постоянными культурами',
                'include_title': u'',
                'include_rowspan': 0,
                'db_fields': ordered_fields,
                'loaded_data': [],
                'where_cases': [
                    {'field': 'NLANDTYPE', 'value': 102},
                    {'field': 'NPRIZNAK', 'value': '7'}
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
                    {'field': 'Vsego', 'value': u'Всего: Под постоянными культурами (в т.ч. осуш.)'}
                ]
            },
            {
                'header_title': u'Всего по виду земель: Луговые улучшенные',
                'include_title': u'',
                'include_rowspan': 0,
                'db_fields': ordered_fields,
                'loaded_data': [],
                'where_cases': [
                    {'field': 'NLANDTYPE', 'value': 103},
                    {'field': 'NPRIZNAK', 'value': '7'}
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

