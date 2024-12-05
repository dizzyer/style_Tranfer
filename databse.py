import sqlite3
import hashlib
import re
from typing import Tuple, Optional
from datetime import datetime

class UserRegistrationSystem:
    def __init__(self, db_file = "users.db"):
        self.db_file = db_file
        self._init_database()

    #dbinit
    def _init_database(self) -> None:
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            #user表 id username password_hash created_at
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    #密文存
    def _hash_password(self, password: str) -> str:
        return hashlib.sha512(password.encode()).hexdigest()

    def _validate_username(self, username: str) -> bool:
        #大小写字母，数字，下划线，长度3-20
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return bool(re.match(pattern, username))

    def _validate_password(self, password: str) -> bool:
        #密码强度验证
        #长度大于8，大小写字母和数字
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        return True

    def _check_username_exists(self, username: str) -> bool:
        #用户查重
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM users WHERE username = ?', (username,))
            return cursor.fetchone() is not None
    #删除所有行
    def clear(self):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='users';")
            return 


    #注册接口
    def register(self, username: str, password: str) -> Tuple[bool, str]:
        #可行性
        if not all([username, password]):
            return False, "所有字段都不能为空"
        if not self._validate_username(username):
            return False, "用户名格式无效（需要3-20个字符，只允许字母、数字和下划线）"
        if not self._validate_password(password):
            return False, "密码强度不足（最少8个字符，至少包含大小写字母和数字）"
        #唯一性
        if self._check_username_exists(username):
            return False, "用户名已存在"

        #写数据
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, password_hash)
                    VALUES (?, ?)
                ''', (username, self._hash_password(password)))
                conn.commit()
                return True, "注册成功"
        except sqlite3.Error as e:
            return False, f"数据库错误: {str(e)}"

    #登录验证接口
    def verify_login(self, username: str, password: str) -> Tuple[bool, str]:
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT password_hash FROM users WHERE username = ?',
                (username,)
            )
            result = cursor.fetchone()
            if not result:
                return False, "用户名不存在"
            stored_hash = result[0]
            if self._hash_password(password) == stored_hash:
                return True, "登录成功"
            return False, "密码错误"