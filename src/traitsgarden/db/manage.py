from traitsgarden.db.connect import Session, connect_db

def show_version(session):
    return session.execute("SELECT version()").all()

def backup_db(session, source, target, overwrite=False):
    session.connection().connection.set_isolation_level(0)
    if overwrite:
        terminate_connections(session, target)
        query = f"""DROP DATABASE IF EXISTS {target}
        """
        session.execute(query)
    terminate_connections(session, source)
    
    query = f"""CREATE DATABASE {target}
        WITH TEMPLATE {source}
        OWNER postgres
    """
    session.execute(query)
    session.connection().connection.set_isolation_level(1)

def terminate_connections(session, db):
    query = f"""SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{db}'
        AND pid <> pg_backend_pid();
    """
    session.execute(query)
