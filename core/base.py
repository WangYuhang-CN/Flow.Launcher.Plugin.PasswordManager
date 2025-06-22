import json
import sqlite3

from abc import ABC
from abc import abstractmethod

from pathlib import Path
from typing import List, Tuple, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.base import Base
from sqlalchemy.orm import Session
from db.passwords import Passwords


class BaseHandle(ABC):
    def __init__(self, parts=""):
        self.parts = parts
        self.is_ok = True
        self.title = ""
        self.sub_title = ""
        self.handle_return = []
        self.logo = "Images/pm_logo.png"
        self.error_logo = "Images/pm_logo.png"
    
    @property
    @abstractmethod
    def handle(self):
        return self

    @property
    @abstractmethod
    def result(self):
        return []


class SQLiteHelper:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=True)
        Base.metadata.create_all(self.engine)
        self.session_local = sessionmaker(bind=self.engine)

        self.conn = None
        self.cursor = None

    def __enter__(self) -> Session:
        self.session = self.session_local()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.session.commit()
        else:
            self.session.rollback()
        self.session.close()


class BasePasswordManager:
    def __init__(self) -> None:
        self.db_filename = "fl_password.db"
        self.base_path = Path(__file__).parent.parent
        with open(self.base_path / "plugin.json", "r", encoding="utf-8") as f:
            self.plugin_info: dict = json.load(f)
        
        self.db_base_path = self.plugin_info.get("db_path")
        try:
            setting_db_base_path = Path(self.db_base_path)
        except:  # NOQA
            # If an error occurs, the default address should be used
            setting_db_base_path = None
        
        if not isinstance(setting_db_base_path, Path) or not setting_db_base_path.exists():
            setting_db_base_path = self.base_path
        
        setting_db_full_path: Path = setting_db_base_path / self.db_filename
        is_init_db = not setting_db_full_path.exists()
        # if is_init_db:
        #     self.init_db(setting_db_full_path)

        self.orm = SQLiteHelper(setting_db_full_path)
    
    def init_db(self, db_full_path: Path):
        conn = sqlite3.connect(db_full_path)
        cursor = conn.cursor()

        self.init_db_table(cursor)

        conn.commit()
        conn.close()

    @staticmethod
    def init_db_table(cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                password TEXT NOT NULL
            );
        """)


def log(message: str, level: str = "INFO"):
    """
    Simple logging function to print messages with a level.
    """
    with open(Path(__file__).parent.parent / "plugin.log", "a", encoding="utf-8") as log_file:
        log_file.write(f"[{level}] {message}\n")
