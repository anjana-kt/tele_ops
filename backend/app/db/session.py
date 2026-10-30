from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

"""
    engine = create_engine(dialect+driver://username:password@host:port/database_name)
    dialect - dbms name (postgresql)
    driver - library to connect to db or DB API (psycopg)
    host - host of db (localhost/127.0.0.1)
    port - port where db can be accessed from host (5432)
    db_name - database name (telemetryops)
"""
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass