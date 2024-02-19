from os import path


class DictAsObject(object):
    def __init__(self, dict_data):
        if isinstance(dict_data, dict):
            self.__dict__.update(dict_data)

    def to_dict(self):
        return self.__dict__

    def make_copy(self):
        return self.__dict__.copy()


class SettingsHolder(object):
    def __init__(self, xls_templates_dir, store_source, on_save=lambda x, y: x):
        self.xls_templates_dir = xls_templates_dir
        self.should_save_as = store_source
        self.set_default_settings()
        self.on_save = on_save

    def save(self):
        self.on_save(self.should_save_as, self.get_settings_dict())

    def update_settings(self, settings_data):
        if self.validate_settings(settings_data):
            try:
                for k, v in settings_data.items():
                    self.set_settings_by_key(k, v)
            except Exception as err:
                print(err)
                self.set_default_settings()
        else:
            self.set_default_settings()

    def check_xl_templates(self):
        xls_s = self.xls_templates_dir  # WARNING бфло просто self.xls

        def check_template(template_path):
            return path.isfile(template_path) and 'xls' in template_path

        templates_meta = [
            {'key_id': 'a_path', 'name': "A"},
            {'key_id': 'a_sv_path', 'name': "A сводная"},
            {'key_id': 'b_path', 'name': "Ф22 зем."},
        ]
        for meta in templates_meta:
            t_key = meta['key_id']

            meta['default_set'] = False
            meta['default_set_incomplete'] = False

            if not check_template(getattr(xls_s, t_key)):
                default_a_path = xls_s.default_paths[t_key]
                if check_template(default_a_path):
                    meta['default_set'] = True
                    setattr(xls_s, t_key, default_a_path)
                else:
                    meta['default_set_incomplete'] = True
        set_to_default_templates = list(filter(lambda x: x['default_set'], templates_meta))
        if len(set_to_default_templates):
            self.save()
        return {
            'set_to_default_templates': set_to_default_templates,
            'unresolved_templates': list(filter(lambda x: x['default_set_incomplete'], templates_meta)),
        }

    @staticmethod
    def get_valid_settings_keys():
        return ['xls', 'rnd', 'balance', 'conditions', 'filter']

    def get_settings_dict(self):
        out = {}
        for key in SettingsHolder.get_valid_settings_keys():
            out[key] = getattr(self, key).__dict__
        return out

    @staticmethod
    def validate_settings(settings_dict):
        ok = True
        default = SettingsHolder.get_default_settings('')
        if isinstance(settings_dict, dict):
            for k in settings_dict.keys():
                if k not in SettingsHolder.get_valid_settings_keys():
                    ok = False
                elif isinstance(default[k], dict) and len(default[k].keys()) != len(settings_dict[k].keys()):
                    ok = False
        else:
            ok = False
        # if ok:
        #     try:
        #         ok = os.path.isfile(settings_dict['xls']['a_sv_path'])
        #     except:
        #         ok = False
        return ok

    def set_default_active_cond(self, select_conditions):
        for cond in select_conditions:
            if not cond['WhereCase']:
                self.conditions.active_cond = cond['Id']

    def set_settings_by_key(self, s_key, s_values):
        if s_key in SettingsHolder.get_valid_settings_keys():
            setattr(self, s_key, DictAsObject(s_values))

    def set_default_settings(self):
        d_settings = SettingsHolder.get_default_settings(self.xls_templates_dir)
        for k, v in d_settings.items():

            self.set_settings_by_key(k, v)

    @staticmethod
    def get_default_settings(xls_templates_dir):
        return {
            'xls': {
                'a_sv_l': u'A',
                'a_sv_n': 6,
                'a_l': u'F',
                'a_n': 16,
                'a_obj_l': u'M',
                'a_obj_n': 4,
                'b_l': u'D',
                'b_n': 7,
                'a_path': u'%s\\FA.xlsx' % xls_templates_dir,
                'a_sv_path': u'%s\\FV_svod.xlsx' % xls_templates_dir,
                'b_path': u'%s\\F22_I.xlsx' % xls_templates_dir,
                'default_paths': {
                    'a_path': u'%s\\FA.xlsx' % xls_templates_dir,
                    'a_sv_path': u'%s\\FV_svod.xlsx' % xls_templates_dir,
                    'b_path': u'%s\\F22_I.xlsx' % xls_templates_dir,
                },
                'a_sh_name': u'',
                'a_sv_sh_name': u'',
                'b_sh_name': u'',  # RB Форма22 зем.
                'is_mdb_start': False,
                'is_xls_start': False
            },
            'rnd': {
                'a_s_accuracy': 4,
                'b_accuracy': 0,
                'small_accur': 3,
                'a_sv_accuracy': 4,
                'show_small': True
            },
            'balance': {
                'include_a_balance': False,
                'include_a_sv_balance': False,
                'include_b_balance': True,
            },
            'conditions': {
                'melio1': '',
                'melio2': '',
                'servtype': '',
                'active_cond': '',
                'groupping_by': '',
                'custom': ''
            },
            'filter': {
                'enabled': False,
                'enable_melio': True,
                'enable_servtype': True,
                'melio': '',
                'servtype': ''
            }
        }
