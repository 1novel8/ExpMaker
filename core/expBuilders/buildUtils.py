

class ExpBuilder:
    to_ga = 10000.0

    @staticmethod
    def sum_dict_values(basic, add_dicts_li, add_ok=True):
        """
        :param basic: main dict with values you are going to add to
        :param add_dicts_li: list or tuple od additional dicts
        :param add_ok: operation with elements, sum or deduct
        :return: :raise:
        """
        if isinstance(basic, dict):
            resultdict = basic.copy()
            if add_ok:
                def apply_changes(target_d, key):
                    if key in target_d:
                        resultdict[key] += target_d[key]
            else:
                def apply_changes(target_d, key):
                    if key in target_d:
                        resultdict[key] -= target_d[key]

            for item in add_dicts_li:
                try:
                    for k in list(resultdict.keys()):
                        apply_changes(item, k)
                except KeyError as err:
                    print(err)
                except Exception:
                    raise
            return resultdict
        else:
            raise TypeError('Wrong basic parameter received')

    @staticmethod
    def round_row_data(data, accuracy=4, show_small=False, small_accur=3, **kwargs):
        # TODO: Remake inputs without __dict__
        accuracy = int(accuracy)

        def rnd(digit):
            # return round(digit/ExpBuilder.to_ga, accuracy)
            if show_small:
                return ExpBuilder.complex_round(digit / ExpBuilder.to_ga, accuracy, small_accur)
            else:
                return round(digit / ExpBuilder.to_ga, accuracy)

        try:
            if isinstance(data, dict):
                d = {}
                for k, v in data.items():
                    d[k] = rnd(v) if v else 0
                return d
            elif isinstance(data, (list, tuple)):
                return map(rnd, data)
            elif isinstance(data, (float, int)):
                return rnd(data)
            else:
                raise Exception('Передан неверный тип обрабатываемых данных')
        except TypeError as err:
            raise Exception('Возникла ошибка при попытке округления %s.\n%s' % (str(data), err.message))

    @staticmethod
    def complex_round(amount, accuracy, small_accur):
        min_step = 10 ** -accuracy
        try:
            if amount < min_step:
                return round(amount, accuracy + small_accur)
            else:
                return round(amount, accuracy)
        except TypeError as err:
            raise Exception('Возникла ошибка при попытке округления %s.\n%s' % (str(amount), err.message))

    @staticmethod
    def round_and_modify(data_dict, settings):
        """
        :param data_dict: dictionary with field keys and their float values
        :param settings: settings instance with parameters that round_row_data def required
        :return: dict with modified structure. after round tails are saved
        """
        setts = settings if isinstance(settings, dict) else settings.__dict__
        modified = data_dict.copy()
        modified = ExpBuilder.round_row_data(modified, **setts)
        for key, val in modified.items():
            modified[key] = {
                'val': val,
                'tail': data_dict[key] / ExpBuilder.to_ga - val
            }
        return modified
