import os
basedir=os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED=True
SECRET_KEY="yo bappa"

# SQLALCHEMY_DATABASE_URI='sqlite:///'+os.path.join (basedir , 'app.db')
SQLALCHEMY_DATABASE_URI='sqlite:///'+'/var/lib/mysql/app.db'
SQLALCHEMY_MIGRATE_REPO=os.path.join(basedir, 'db_repository')

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://karan:krishna@localhost/app'