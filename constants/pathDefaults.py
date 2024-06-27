from os import path


class CoreFilesPaths:
    project_dir = '.\\'
    spr_dir = path.join(project_dir, 'Spr')
    spr_default_path = path.join(spr_dir, 'DefaultSpr.pkl')
    tempDB_path = path.join(spr_dir, 'tempDbase.mdb')
    templ_db_path = path.join(spr_dir, 'template.mdb')
    xls_templates_dir = path.join(spr_dir, 'xls_forms')
