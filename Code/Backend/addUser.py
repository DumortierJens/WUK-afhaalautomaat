from repositories.Database import Database
import hashlib, os

username = '' # New username
password = '' # New password

salt = os.urandom(32)
key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

sql = "insert into user (username, password, salt) "
sql += "values (%s, %s, %s)"
params = [username, key, salt]
res = Database.execute_sql(sql, params)
print(res)