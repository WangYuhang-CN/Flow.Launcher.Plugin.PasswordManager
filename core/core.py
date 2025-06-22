import json
from core.base import BaseHandle
from core.base import BasePasswordManager
from db.passwords import Passwords


class PasswordOperation(BaseHandle, BasePasswordManager):
    def __init__(self, parts=""):
        BaseHandle.__init__(self, parts)
        BasePasswordManager.__init__(self)

    def result(self):
        if self.is_ok:
            return self.handle_return
        return [{
            "Title": self.title,
            "SubTitle": self.sub_title or self.title,
            "IcoPath": self.error_logo,
        }]

    def validate_args(self, expected_len: int, usage: str) -> bool:
        if len(self.parts) != expected_len:
            self.is_ok = False
            self.title = f"Usage: {usage}"
            return False
        return True


class PasswordQuery(PasswordOperation):

    @property
    def handle(self):
        if not self.validate_args(1, "pw <key> / *"):
            return self
        
        key = self.parts[0]
        with self.orm as orm:
            
            if key == "*":
                results = orm.query(Passwords).all()
            else:
                results = orm.query(Passwords).filter(Passwords.key.like(f"%{key}%")).all()
            
            for r in results:
                key = r.key
                password = r.password
                self.handle_return.append({
                    "Title": f"Press Enter to Copy password by `{key}`",
                    "SubTitle": "",
                    "IcoPath": self.logo,
                    "JsonRPCAction": {
                        "method": "copy",
                        "parameters": [password]
                    }
                })
            
            if not self.handle_return:
                self.handle_return.append({
                    "Title": f"`{key}` Not found",
                    "SubTitle": "",
                    "IcoPath": self.logo,
                })
        
        return self
    
    @property
    def result(self):
        if self.is_ok:
            return self.handle_return
        else:
            return [
                {
                    "Title": self.title,
                    "SubTitle": self.sub_title,
                    "IcoPath": self.error_logo
                }
            ]


class PasswordSet(PasswordOperation):

    @property
    def handle(self):
        if not self.validate_args(2, "pws <key> <password>"):
            return self
        
        key = self.parts[0]
        password = self.parts[1]

        with self.orm as orm:
            first: Passwords = orm.query(Passwords).filter(Passwords.key == key).first()
            if first:
                self.handle_return.append({
                    "Title": f"Press Enter to Copy new password for `{key}`",
                    "SubTitle": "The selection will overwrite your old password",
                    "IcoPath": self.logo,
                    "JsonRPCAction": {
                        "method": "update_password_and_copy",
                        "parameters": [json.dumps({
                            "key": key,
                            "password": password,
                            "handle_key": "pws"
                        })]
                    }
                })

                self.handle_return.append({
                    "Title": f"Press Enter to Copy old password for `{key}`",
                    "SubTitle": f"this your old password",
                    "IcoPath": self.logo,
                    "JsonRPCAction": {
                        "method": "copy",
                        "parameters": [first.password]
                    }
                })
            
            else:   
                self.handle_return.append({
                    "Title": f"Press Enter to Copy password for `{key}`",
                    "SubTitle": self.sub_title,
                    "IcoPath": self.logo,
                    "JsonRPCAction": {
                        "method": "create_and_copy",
                        "parameters": [json.dumps({
                            "key": key,
                            "password": password,
                            "handle_key": "pws"
                        })]
                    }
                })
        
        return self
    
    @property
    def result(self):
        if self.is_ok:
            return self.handle_return
        else:
            return [
                {
                    "Title": self.title,
                    "SubTitle": self.title,
                    "IcoPath": self.error_logo
                }
            ]


class PasswordDelete(PasswordOperation):

    @property
    def handle(self):
        if not self.validate_args(1, "pwd <key>"):
            return self

        key = self.parts[0]
        with self.orm as orm:
            first: Passwords = orm.query(Passwords).filter(Passwords.key == key).first()
            if first:
                self.handle_return.append({
                    "Title": f"Press Enter to confirm deleting Key `{key}`",
                    "SubTitle": self.sub_title,
                    "IcoPath": self.logo,
                    "JsonRPCAction": {
                        "method": "delete_password",
                        "parameters": [json.dumps({
                            "key": key,
                            "handle_key": "pwd"
                        })]
                    }
                })
            else:
                self.handle_return.append({
                    "Title": f"`{key}` Not found",
                    "SubTitle": "",
                    "IcoPath": self.logo,
                })
        
        return self
    
    @property
    def result(self):
        if self.is_ok:
            return self.handle_return
        else:
            return [
                {
                    "Title": self.title,
                    "SubTitle": self.title,
                    "IcoPath": self.error_logo
                }
            ]
