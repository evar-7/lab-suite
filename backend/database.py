from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import get_settings


Base = declarative_base()


def normalize_database_url(raw_url: str) -> str:
    if raw_url.startswith("postgres://"):
        return "postgresql://" + raw_url[len("postgres://") :]
    return raw_url


def build_engine(database_url: str):
    normalized_url = normalize_database_url(database_url)
    is_sqlite = normalized_url.startswith("sqlite")
    return create_engine(
        normalized_url,
        connect_args={"check_same_thread": False} if is_sqlite else {},
        pool_pre_ping=True,
        future=True,
    )


def _build_session_local(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


settings = get_settings()
ENGINE = build_engine(settings.database_url)
SessionLocal = _build_session_local(ENGINE)


def configure_database(database_url: str) -> None:
    global ENGINE, SessionLocal
    ENGINE = build_engine(database_url)
    SessionLocal = _build_session_local(ENGINE)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_schema() -> None:
    Base.metadata.create_all(bind=ENGINE)

