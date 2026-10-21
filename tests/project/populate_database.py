from odoo_commands import DataGenerator


class DatabaseGenerator(DataGenerator):
    def populate(self, env, russian, main_company):
        self.create_user(
            env,
            {
                'name': 'Name',
                'login': 'name',
                'company_id': main_company.id,
            },
        )
