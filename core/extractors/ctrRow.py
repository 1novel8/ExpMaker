def catch_wrong_fkey(f_to_decor):
    def wrapper(self, *args, **kwargs):
        try:
            return f_to_decor(self, *args, **kwargs)
        except KeyError:
            raise Exception(u'Прервана попытка получить элемент по несуществующему ключу %s' % args[0])

    return wrapper


class CtrRow:
    def __init__(self, spr_holder, r_args, n):
        """
        land_code is always on index 0, slnad on index 1

        :param r_args: OBJECTID, SOATO, SlNad, State_1, LANDCODE, MELIOCODE, ServType08, Forma22_*,
                UserN_*,Usertype_*, Area_*, *dop_params
        # :param n_dop_args: len of dop params array in the end of r_args
        :param n: max number of parts in crostab table
        :param spr_holder: SpravHolder instance
        """
        self.row_ready = False
        self.has_err = False  # отанется False - контроль пройден,
        self.err_in_part = None
        self.structure: dict = spr_holder.attr_config
        self.n = n
        self.__r_args = r_args
        self.soato = self.get_el_by_fkey('nptype')
        self.object_id = self.get_el_by_fkey('id')
        np_type = CtrRow.make_nptype(self.soato, spr_holder.soato_npt)
        if np_type is None:
            self.has_err = 4
            self.err_in_part = 1
            return
        self.__r_args[self.structure['nptype']] = np_type
        self.new_lc = None
        self.dopname = [None] * self.n
        self.nusname = [None] * self.n
        self.run_bgd_control(spr_holder)
        if not self.has_err:
            self.remake_area()
            self.remake_usern()
            self.block_r_args()

    @staticmethod
    def make_nptype(kod, npt_sprav):
        for row in npt_sprav:
            if int(kod[0]) == 5:
                return row[6]
            elif int(kod[1]) == row[1]:
                if row[3] is None or row[2] <= int(kod[4:7]) <= row[3]:
                    if row[4] is None or row[4] <= int(kod[7:10]) <= row[5]:
                        return row[6]

    def simplify_to_d(self, n, need_keys):
        """
        unused keys are drops ,
        :rtype : object with keys from structure
        """
        return_di = dict.fromkeys(need_keys)
        for key in need_keys:
            elem = self.__r_args[self.structure[key]]
            if isinstance(elem, (list, tuple)):
                return_di[key] = elem[n]
            else:
                return_di[key] = elem
        return return_di

    @catch_wrong_fkey
    def get_el_by_fkey(self, f_key):
        """
        Use to get row elemets from structure keys.
        :param f_key: structure key of multiple
        :return: element by structure key from self.__r_args
        """
        return self.__r_args[self.structure[f_key]]

    @catch_wrong_fkey
    def get_el_by_fkey_n(self, f_key, n):
        """
        Use to get row elemets from structure keys.
        Usage for multiple objects only! if n parameter out of range - exception will raise
        :param f_key: structure key of multiple
        :param n: element index
        :return: n-th element by structure key from self.__r_args
        """
        return self.__r_args[self.structure[f_key]][n]

    @catch_wrong_fkey
    def set_el_by_fkey(self, f_key, val):
        if not self.row_ready:
            self.__r_args[self.structure[f_key]] = val

    @catch_wrong_fkey
    def set_el_by_fkey_n(self, f_key, n, val):
        if not self.row_ready:
            self.__r_args[self.structure[f_key]][n] = val

    def remake_area(self):
        if self.n > 1:
            areas = []
            shape_area = self.get_el_by_fkey(u'area')
            for part in self.get_el_by_fkey(u'part'):
                areas.append(shape_area * part / 100)
            self.set_el_by_fkey(u'area', areas)
        else:
            self.set_el_by_fkey(u'area', self.get_el_by_fkey(u'area'))

    def remake_usern(self):
        user_sad = self.get_el_by_fkey('usern_sad')
        if user_sad:
            self.__r_args[self.structure['usern']] = [user_sad for x in range(self.n)]

    def block_r_args(self, fix=True):
        def change_type(item):
            return tuple(item) if fix else list(item)

        r_args = self.__r_args
        for i in range(len(r_args)):
            if isinstance(r_args[i], (tuple, list)):
                r_args[i] = change_type(r_args[i])
        self.__r_args = change_type(r_args)
        self.row_ready = fix

    def has_code(self, n, param, codes):
        # if n <= self.n:
        val = self.get_el_by_fkey(param)
        if isinstance(val, (list, tuple)):
            val = val[n]
        return val in codes

    def check_filter_match(self, n, sort_filter):
        """
        Checks if row matches the filter
        :param n: N of the checking part
        :param sort_filter: an object containing filter params
        :return: Boolean
        """
        if not isinstance(sort_filter, dict) or not len(sort_filter.keys()):
            return False
        # match_result = True
        for k, v in sort_filter.items():
            if not isinstance(v, (list, tuple)):
                v = [v]
            if not self.has_code(n, k, v):
                return False
        return True

    def run_bgd_control(self, s_h):
        if self.n == 1:
            if self.bgd1_control(s_h, 0):
                pass
            elif self.bgd2_control(s_h, 0):
                if self.new_lc:
                    self.set_el_by_fkey('lc', self.new_lc)
            else:
                self.has_err = 1
                self.err_in_part = 1
        else:
            for n in range(self.n):
                if self.bgd1_control(s_h, n):
                    continue
                elif self.bgd2_control(s_h, n):
                    if self.new_lc:
                        self.set_el_by_fkey('lc', self.new_lc)
                else:
                    self.has_err = 2
                    self.err_in_part = n + 1
                    break

    def bgd1_control(self, spr, n):
        try:
            bgd_li = spr.bgd2ekp_1[self.get_el_by_fkey('f22')[n]][self.get_el_by_fkey('usertype')[n]][
                self.get_el_by_fkey('state')][self.get_el_by_fkey('slnad')]
            for b_row in bgd_li:  # bgd_row:
                #  f22 > UTYPE > State > SLNAD > NPTYPE_min, NPTYPE_max,  NEWUSNAME, DOPUSNAME,
                if b_row[0] <= self.get_el_by_fkey('nptype') <= b_row[1]:
                    self.nusname[n] = b_row[2]
                    self.dopname[n] = b_row[3]
                    return True
        except KeyError:
            pass
        return False

    def bgd2_control(self, spr, n):
        f22 = self.get_el_by_fkey('f22')[n]
        utype = self.get_el_by_fkey('usertype')[n]
        state = self.get_el_by_fkey('state')
        slnad = self.get_el_by_fkey('slnad')
        try:
            bgd_li = spr.bgd2ekp_2[f22][utype][state][slnad]
            # newF22,NPTYPE_min, NPTYPE_max, lc_min, lc_max, newlc, NEWUSNAME, DOPUSNAME
            for b_row in bgd_li:  # bgd_row: newF22(0), NPTYPE_min (1),
                # NPTYPE_max (2), lc_min(3), lc_max(4), newlc(5), NEWUSNAME(6), DOPUSNAME(7)
                if b_row[1] <= self.get_el_by_fkey('nptype') <= b_row[2] \
                        and b_row[3] <= self.get_el_by_fkey('lc') <= b_row[4]:
                    self.set_el_by_fkey_n('f22', n, b_row[0])
                    self.nusname[n] = b_row[6]
                    self.dopname[n] = b_row[7]
                    self.new_lc = b_row[5]
                    return True
        except KeyError:
            pass
        return False
