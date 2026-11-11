from flask_smorest import Api
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

api = Api()
Base = declarative_base()


class Database:
    """Lightweight SQLAlchemy database wrapper for Flask."""

    def __init__(self):
        self.engine = None
        self.session_factory = None
        self._session = None

    def init_app(self, app):
        database_url = app.config.get("SQLALCHEMY_DATABASE_URI", "sqlite:///product_api.db")
        is_testing = app.config.get("TESTING", False)

        # For sqlite in-memory in tests, maintain single thread connection if needed
        connect_args = {}
        if database_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}

        self.engine = create_engine(
            database_url,
            connect_args=connect_args,
            echo=False,
        )
        self.session_factory = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
        self._session = scoped_session(self.session_factory)

        @app.teardown_appcontext
        def remove_session(exception=None):
            self._session.remove()

    @property
    def session(self):
        return self._session

    def create_all(self):
        Base.metadata.create_all(bind=self.engine)

    def drop_all(self):
        Base.metadata.drop_all(bind=self.engine)


db = Database()

