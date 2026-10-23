{
    'name': 'Module A',
    'summary': 'Module A Summary',
    'version': '11.0.1',

    'author': 'Odoo Russian Community',
    'website': 'https://example.com',
    'license': 'Other proprietary',

    'depends': [
        'module_b',
    ],

    'data': [
        'security/model_a_groups.xml',
        'security/model_a_access.xml',
        'security/model_a_rules.xml',

        'views/model_a.xml',
    ],
}
