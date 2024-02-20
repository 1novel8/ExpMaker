class SpravStructure:
    lc = "S_LandCodes"
    r_alias = "Alias_F_Config"
    a_r_str = "ExpA_R_Structure"
    a_f_str = "ExpA_F_Structure"
    b_r_str = "ExpB_R_Structure"
    b_f_str = "ExpB_F_Structure"
    b2e_1 = "BGDToEkp1"
    b2e_2 = "BGDToEkp2"
    soato = "S_SOATO"
    state = "S_State"
    f22 = "S_Forma22"
    mc = "S_MelioCode"
    slnad = "S_SlNad"
    ustype = "S_Usertype"
    select_conditions = "Select_Conditions"

    tabs_enum = [
        lc, r_alias, a_r_str, a_f_str, b_r_str, b_f_str, b2e_1, b2e_2,
        soato, state, f22, mc, slnad, ustype, select_conditions
    ]

    def get_tab_str(self, table):
        if table in self.tabs_enum:
            return SpravStructure._get_str()[table]
        else:
            raise Exception("faled to handle unsupported table")

    @staticmethod
    def _get_str():
        return {
            "S_LandCodes": {
                "lc": {
                    "name": "LandCode",
                    "type": "SMALLINT",
                },
                "f_num": {
                    "name": "field_Num",
                    "type": "SMALLINT",
                }
            },
            "Alias_F_Config": {
                "alias": {
                    "name": "alias",
                    "type": "VARCHAR",
                },
                "match_f": {
                    "name": "match_field",
                    "type": "VARCHAR",
                },
                "f_type": {
                    "name": "field_type",
                    "type": "VARCHAR",
                },
            },
            "ExpA_R_Structure": {
                "row_id": {
                    "name": "row_id",
                    "type": "INTEGER",
                },
                "codes": {
                    "name": "codes",
                    "type": "VARCHAR",
                },
                "row_name": {
                    "name": "row_name",
                    "type": "VARCHAR",
                },
                "group_field": {
                    "name": "group_field",
                    "type": "VARCHAR",
                },
                "balance_lvl": {
                    "name": "balance_level",
                    "type": "SMALLINT",
                },
                "balance_by": {
                    "name": "balance_by",
                    "type": "VARCHAR",
                }
            },
            "ExpA_F_Structure": {
                "f_num": {
                    "name": "f_num",
                    "type": "INTEGER",
                },
                "f_name": {
                    "name": "f_name",
                    "type": "VARCHAR",
                },
                "sum_fields": {
                    "name": "sum_fields",
                    "type": "VARCHAR",
                },
                "balance_lvl": {
                    "name": "balance_level",
                    "type": "SMALLINT",
                },
                "balance_by": {
                    "name": "balance_by",
                    "type": "VARCHAR",
                }
            },
            "ExpB_R_Structure": {
                "row_id": {
                    "name": "row_id",
                    "type": "INTEGER",

                },
                "row_key": {
                    "name": "row_key",
                    "type": "VARCHAR",
                },
                "f22_value": {
                    "name": "f22_value",
                    "type": "VARCHAR",
                },
                "sort_filter": {
                    "name": "sort_filter",
                    "type": "VARCHAR",
                },
                "sum_conditions": {
                    "name": "sum_conditions",
                    "type": "VARCHAR",
                },
                "balance_lvl": {
                    "name": "balance_level",
                    "type": "SMALLINT",
                },
                "balance_by": {
                    "name": "balance_by",
                    "type": "VARCHAR",
                }
            },
            "ExpB_F_Structure": {
                "f_num": {
                    "name": "f_num",
                    "type": "INTEGER",
                },
                "f_name": {
                    "name": "f_name",
                    "type": "VARCHAR",
                },
                "alias_codes": {
                    "name": "alias_codes",
                    "type": "VARCHAR",
                },
                "sum_fields": {
                    "name": "sum_fields",
                    "type": "VARCHAR",
                },
                "balance_lvl": {
                    "name": "balance_level",
                    "type": "SMALLINT",
                },
                "balance_by": {
                    "name": "balance_by",
                    "type": "VARCHAR",
                }
            },
            "BGDToEkp1": {
                "f22": {
                    "name": "F22",
                    "type": "VARCHAR",
                },
                "u_type": {
                    "name": "UTYPE",
                    "type": "VARCHAR",
                },
                "np_type": {
                    "name": "NPTYPE",
                    "type": "VARCHAR",
                },
                "state": {
                    "name": "STATE",
                    "type": "VARCHAR",
                },
                "sl_nad": {
                    "name": "SLNAD",
                    "type": "VARCHAR",
                },
                "new_us_name": {
                    "name": "NEWUSNAME",
                    "type": "SMALLINT",
                },
                "dop_us_name": {
                    "name": "DOPUSNAME",
                    "type": "VARCHAR",
                }
            },
            "BGDToEkp2": {
                "f22": {
                    "name": "F22",
                    "type": "VARCHAR",
                },
                "new_f22": {
                    "name": "NEWF22",
                    "type": "VARCHAR",
                },
                "u_type": {
                    "name": "UTYPE",
                    "type": "VARCHAR"},
                "np_type": {
                    "name": "NPTYPE",
                    "type": "VARCHAR",
                },
                "lc_min": {
                    "name": "LCODE_MIN",
                    "type": "SMALLINT",
                },
                "lc_max": {
                    "name": "LCODE_MAX",
                    "type": "SMALLINT",
                },
                "new_lc": {
                    "name": "NewLCODE",
                    "type": "SMALLINT",
                },
                "state": {
                    "name": "STATE",
                    "type": "VARCHAR",
                },
                "new_state": {
                    "name": "NewSTATE",
                    "type": "SMALLINT",
                },
                "sl_nad": {
                    "name": "SLNAD",
                    "type": "VARCHAR",
                },
                "new_us_name": {
                    "name": "NEWUSNAME",
                    "type": "SMALLINT",
                },
                "dop_us_name": {
                    "name": "DOPUSNAME",
                    "type": "VARCHAR",
                }
            },
            "S_SOATO": {
                # "id":   {"name": "OBJECTID",
                #          "type": "COUNTER"},
                "zn_1": {
                    "name": "znak1",
                    "type": "VARCHAR",
                },
                "zn_2": {
                    "name": "znak2",
                    "type": "SMALLINT",
                },
                "zn_57min": {
                    "name": "znak57min",
                    "type": "SMALLINT",
                },
                "zn_57max": {
                    "name": "znak57max",
                    "type": "SMALLINT",
                },
                "zn_810max": {
                    "name": "znak810max",
                    "type": "SMALLINT",
                },
                "zn_810min": {
                    "name": "znak810min",
                    "type": "SMALLINT",
                },
                "type_np": {
                    "name": "TypeNP",
                    "type": "SMALLINT",
                }
            },
            "S_State": {
                # "id":    {"name": "OBJECTID",
                #                  "type": "COUNTER"},
                "state_code": {
                    "name": "StateCode",
                    "type": "SMALLINT",
                }
            },
            "S_Forma22": {
                # "id":   {"name": "OBJECTID",
                #          "type": "COUNTER"},
                "f22_code": {
                    "name": "F22Code",
                    "type": "VARCHAR",
                },
                "f22_name": {
                    "name": "F22Name",
                    "type": "VARCHAR",
                }
            },
            "S_MelioCode": {
                # "id":
                #
                # {"name": "OBJECTID",
                #          "type": "COUNTER"},
                "mc": {
                    "name": "MelioCode",
                    "type": "SMALLINT",

                }
            },
            "S_SlNad": {
                # "id":  {"name": "OBJECTID",
                #          "type": "COUNTER"},
                "sl_nad_code": {
                    "name": "SLNADCode",
                    "type": "BYTE",

                }
            },
            "S_Usertype": {
                # "id":   {"name": "OBJECTID",
                #          "type": "COUNTER"},
                "user_type": {
                    "name": "UsertypeCode",
                    "type": "BYTE",
                }
            },
            "Select_Conditions": {
                "id": {
                    "name": "Id",
                    "type": ["INTEGER", "SMALLINT", "COUNTER"],
                },
                "title": {
                    "name": "Title",
                    "type": ["VARCHAR"],
                },
                "where_case": {
                    "name": "WhereCase",
                    "type": ["VARCHAR"],
                }
            }
        }
