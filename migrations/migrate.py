import os

from alembic import command
from alembic.config import Config


def lambda_handler(event, context):
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), '..', 'alembic.ini'))
    alembic_cfg.set_main_option('sqlalchemy.url', os.getenv('DEV_DATABASE_URL'))

    # Generar las migraciones
    try:
        command.revision(alembic_cfg, message='auto migration', autogenerate=True)
        print('Migration script generated successfully')
    except Exception as e:
        print(f'Failed to generate migration: {e}')
        return {'statusCode': 500, 'body': f'Failed to generate migration: {e}'}

    # Aplicar las migraciones
    try:
        command.upgrade(alembic_cfg, 'head')
        print('Migration applied successfully')
    except Exception as e:
        print(f'Failed to apply migration: {e}')
        return {'statusCode': 500, 'body': f'Failed to apply migration: {e}'}

    return {'statusCode': 200, 'body': 'Migrations generated and applied successfully!'}
