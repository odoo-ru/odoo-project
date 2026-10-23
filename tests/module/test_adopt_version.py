from odoo_project.module import adapt_version


def test_adopt_version():
    assert adapt_version('1.2', '20.0') == '20.0.1.2'
    assert adapt_version('1.2.3', '20.0') == '20.0.1.2.3'
    assert adapt_version('1.2.3.4', '20.0') == '1.2.3.4'
    assert adapt_version('1.2.3.4.5', '20.0') == '1.2.3.4.5'
    assert adapt_version('20.0', '20.0') == '20.0'
    assert adapt_version('20.0.1', '20.0') == '20.0.1'
