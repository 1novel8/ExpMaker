#!/usr/bin/env python
# -*- coding: utf-8 -*-


def get_config():
    ordered_fields = [
        'CHOZ',
        'NBALLUD1',
        'NBALLUD2',
        'NBALLUD3',
        'NBALLUD4',
        'NBALLUD'
    ]
    return {
        'date_out_cell': u'A1',
        'rayon_out_cell': u'A2',
        'shz_out_cell': u'A3',
        'fields_to_validate': ordered_fields,
        'template_sheet_name': u'T20',
        'start_export_cell': u'A10',
        'data_configure_list': [
            {
                'header_title': u'',
                'include_title': u'',
                'include_rowspan': 0,
                'db_fields': ordered_fields,
                'loaded_data': [],
                'where_cases': []
            },
           
        ]
    }

