#!/usr/bin/env python
# -*- coding: utf-8 -*-



def get_config():
    ordered_fields = [
        'NOBKOZ_1',
        'NOBKOZ_3',
        'NOBKOZ_4',
		'NOBKOZ_0',
		'NBPP_1',
		'NBPP_3',
		'NBPP_4',
		'NBPP_0',
		'NND_1',
		'NND_3',
		'NND_4',
        'NND_0',
		'NDD_1',
		'NDD_3',
        'NDD_4',
        'NDD_0'
    ]
    return {
        'date_out_cell': u'A1',
        'rayon_out_cell': u'A2',
        'shz_out_cell': u'A3',
        'fields_to_validate': ordered_fields,
        'template_sheet_name': u'T22',
        'start_export_cell': u'A10',
        'data_configure_list': [
            {
                'header_title': u'',
                'include_title': u'',
                'include_rowspan': 0,
                'db_fields': ordered_fields,
                'loaded_data': [],
                'where_cases': [
                ]
            },

        ]
    }

