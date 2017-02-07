#!/usr/bin/env python
# -*- coding: utf-8 -*-



def get_config():
    ordered_fields = [
        'Num_Rab',
        'NZUAREA',
        'NZUAREAOS',
        'NLUG',
        'NLUGPOPR',
        'NOKULTUR',
        'NNEOD',
        'NGEN',
        'NUDPER',
        'NEROD',
        'NKAM',
        'NMELSOST',
        'NKUST',
		'NGORIZ',
		'NGLIN',
        'NAGKL',
		'NKONT',
        'NSUH'
    ]
    return {
        'date_out_cell': u'A1',
        'rayon_out_cell': u'A2',
        'shz_out_cell': u'A3',
        'fields_to_validate': ordered_fields,
        'template_sheet_name': u'T17',
        'start_export_cell': u'A10',
        'data_configure_list': [
            {
                'header_title': u'Естественные луговые земли',
                'include_title': u'',
                'include_rowspan': 0,
                'db_fields': ordered_fields,
                'loaded_data': [],
                'where_cases': [
                    {'field': u'NPRIZNAK', 'value': u'2'}
                ]
            },
            {
                'header_title': u'Всего по естественным луговым землям',
                'include_title': u'',
                'include_rowspan': 0,
                'db_fields': ordered_fields,
                'loaded_data': [],
                'where_cases': [
                    {'field': 'NPRIZNAK', 'value': '9'}
                ]
            },
            {
                'header_title': u'',
                'include_title': u'в т.ч. осуш.',
                'include_rowspan': 3,
                'db_fields': ordered_fields[3:],
                'loaded_data': [],
                'where_cases': [
                    {'field': 'NPRIZNAK', 'value': '10'}
                ]
            }
        ]
    }

