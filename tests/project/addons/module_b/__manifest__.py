{
    'name': 'Module B',
    'summary': 'Module B Summary',
    'version': '11.0.1',

    'author': 'Ruchet',
    'website': 'https://ermd.ru',
    'license': 'Other proprietary',
    'icon': '/base_ext/static/description/icon.png',

    'depends': [
        'module_c',
    ],

    'data': [
        'security/model_b_groups.xml',
        'security/model_b_access.xml',
        'security/model_b_rules.xml',

        'views/model_b.xml',
    ],
}
