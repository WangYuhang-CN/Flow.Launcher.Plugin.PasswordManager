# -*- coding: utf-8 -*-

import os
import sys
import json
import webbrowser
parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, 'libs'))
sys.path.append(os.path.join(parent_folder_path, 'plugin'))

import pyperclip
from flowlauncher2 import FlowLauncher
from core.core import PasswordQuery
from core.core import PasswordSet
from core.core import PasswordDelete
from db.passwords import Passwords
from core.base import log


class PasswordManager(FlowLauncher):
    ROUTES = {
        "pw": PasswordQuery,
        "pws": PasswordSet,
        "pwd": PasswordDelete,
    }

    def __init__(self):
        super().__init__()

        self.handle_obj = None
    
    def query(self, query: str):
        parts = query.strip().split()
        if parts and parts[0].lower() in self.ROUTES:
            obj = self.ROUTES[parts[0].lower()](parts[1:])
            self.handle_obj = obj.handle
            return self.handle_obj.result
        
        return [
            {
                "Title": f"Support for {', '.join(self.ROUTES.keys())}",
                "SubTitle": "",
                "IcoPath": "Images/pm_logo.png",
                "JsonRPCAction": {}
            }
        ]

    def open_url(self, url):
        webbrowser.open(url)
    
    def copy(self, value):
        pyperclip.copy(value)
    
    def _parse_js_info(self, js_info: str) -> dict:
        try:
            data = json.loads(js_info)
            return {
                "key": data.get("key"),
                "password": data.get("password"),
                "handle_key": data.get("handle_key", "pw")
            }
        except Exception:
            log("Invalid js_info JSON", level="ERROR")
            return {"key": None, "password": None, "handle_key": "pw"}
    
    def update_password_and_copy(self, js_info):
        log(f"Updating password for key: {js_info}")
        data = self._parse_js_info(js_info)
        key = data["key"]
        password = data["password"]
        handle_key = data.get("handle_key", "pws")
        with self.ROUTES[handle_key]().orm as orm:
            first: Passwords = orm.query(Passwords).filter(Passwords.key == key).first()
            if first:
                first.password = password
        
        self.copy(password)
    
    def create_and_copy(self, js_info):
        data = self._parse_js_info(js_info)
        key = data["key"]
        password = data["password"]
        handle_key = data.get("handle_key", "pws")

        with self.ROUTES[handle_key]().orm as orm:
            new_item = Passwords(key=key, password=password)
            orm.add(new_item)

        self.copy(password)

    def delete_password(self, js_info):
        data = self._parse_js_info(js_info)
        key = data["key"]
        handle_key = data.get("handle_key", "pwd")
        with self.ROUTES[handle_key]().orm as orm:
            first: Passwords = orm.query(Passwords).filter(Passwords.key == key).first()
            if first:
                orm.delete(first)


if __name__ == "__main__":
    PasswordManager()
