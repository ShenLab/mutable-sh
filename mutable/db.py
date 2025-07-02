import sqlite3
import click

from flask import current_app, g


def get_user_db():
    if 'user_db' not in g:
        g.user_db = sqlite3.connect(
            current_app.config["USER_DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.user_db.row_factory = sqlite3.Row

    return g.user_db

def close_user_db(e=None):
    user_db = g.pop('user_db', None)

    if user_db is not None:
        user_db.close()

def init_user_db():
    user_db = get_user_db()

    with current_app.open_resource('user_schema.sql') as f:
        user_db.executescript(f.read().decode('utf8'))

def get_dnv_db():
    if 'dnv_db' not in g:
        g.dnv_db = sqlite3.connect(
            current_app.config["DNV_DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.dnv_db.row_factory = sqlite3.Row

    return g.dnv_db

def close_dnv_db(e=None):
    dnv_db = g.pop('dnv_db', None)

    if dnv_db is not None:
        dnv_db.close()

def get_sample_db():
    if 'sample_db' not in g:
        g.sample_db = sqlite3.connect(
            current_app.config["SAMPLE_DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.sample_db.row_factory = sqlite3.Row

    return g.sample_db

def close_sample_db(e=None):
    sample_db = g.pop('sample_db', None)

    if sample_db is not None:
        sample_db.close()

def get_sample_public_db():
    if 'sample_public_db' not in g:
        g.sample_public_db = sqlite3.connect(
            current_app.config["SAMPLE_PUBLIC_DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.sample_public_db.row_factory = sqlite3.Row

    return g.sample_public_db

def close_sample_public_db(e=None):
    sample_public_db = g.pop('sample_public_db', None)

    if sample_public_db is not None:
        sample_public_db.close()

def get_gene_db():
    if 'gene_db' not in g:
        g.gene_db = sqlite3.connect(
            current_app.config["GENE_DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.gene_db.row_factory = sqlite3.Row

    return g.gene_db

def close_gene_db(e=None):
    gene_db = g.pop('gene_db', None)

    if gene_db is not None:
        gene_db.close()

def get_distance_db():
    if 'distance_db' not in g:
        g.distance_db = sqlite3.connect(
            current_app.config["DISTANCE_DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.distance_db.row_factory = sqlite3.Row

    return g.distance_db

def close_distance_db(e=None):
    distance_db = g.pop('distance_db', None)

    if distance_db is not None:
        distance_db.close()

def get_constraint_db():
    if 'constraint_db' not in g:
        g.constraint_db = sqlite3.connect(
            current_app.config["CONSTRAINT_DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.constraint_db.row_factory = sqlite3.Row

    return g.constraint_db

def close_constraint_db(e=None):
    constraint_db = g.pop('constraint_db', None)

    if constraint_db is not None:
        constraint_db.close()

def get_plddt_db():
    if 'plddt_db' not in g:
        g.plddt_db = sqlite3.connect(
            current_app.config["PLDDT_DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.plddt_db.row_factory = sqlite3.Row

    return g.plddt_db

def close_plddt_db(e=None):
    plddt_db = g.pop('plddt_db', None)

    if plddt_db is not None:
        plddt_db.close()

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_user_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_user_db)
    app.teardown_appcontext(close_dnv_db)
    app.teardown_appcontext(close_distance_db)
    app.cli.add_command(init_db_command)
