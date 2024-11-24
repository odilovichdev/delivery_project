from sqlalchemy import create_engine

from sqlalchemy.orm import declarative_base, sessionmaker


engine = create_engine("postgresql+psycopg2://postgres:1@localhost/delivery",
                       echo=True)

Base = declarative_base()

session = sessionmaker()