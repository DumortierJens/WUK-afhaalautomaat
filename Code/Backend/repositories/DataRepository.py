from .Database import Database
import datetime


class DataRepository:
    

    # Static methods
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    @staticmethod
    def default_serializer(obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        else:
            return obj


    # Get user
    def get_user(username):
        sql = "select username, password, salt "
        sql += "from user "
        sql += "where username = %s "
        params = [username]
        return Database.get_one_row(sql, params)

    
    # History
    def add_history_action(device_name, action, value=None):
        sql = "insert into history (deviceid, actionid, value) "
        sql += "values ((select id from device where name = %s), (select id from action where description = %s), %s)"
        params = [device_name, action, value]
        return Database.execute_sql(sql, params)

    def get_history_temperature(limit=100):
        sql = 'select timestamp, value '
        sql += 'from history as h '
        sql += 'join device as d on h.deviceid = d.id '
        sql += "where d.name = 'Temperature Sensor' "
        sql += 'order by timestamp desc '
        sql += 'limit %s'
        params = [limit]
        return Database.get_rows(sql, params)

    def get_history_detection(limit=100):
        sql = "select timestamp, (case a.description when 'Detection Stopped' then 0 when 'Detection' then 1 end) as status "
        sql += 'from history as h '
        sql += 'join device as d on h.deviceid = d.id '
        sql += 'join action as a on h.actionid = a.id '
        sql += "where d.name = 'Detector' "
        sql += 'order by timestamp desc '
        sql += 'limit %s'
        params = [limit]
        return Database.get_rows(sql, params)

    def get_history_locks(limit=100):
        sql = "select d.name, timestamp, (case a.description when 'Lock Closed' then 0 when 'Lock Opened' then 1 end) as status "
        sql += "from history as h "
        sql += 'join device as d on h.deviceid = d.id '
        sql += 'join action as a on h.actionid = a.id '
        sql += 'join devicetype as dt on d.DeviceTypeid = dt.id '
        sql += "where dt.description = 'Lock' "
        sql += 'order by timestamp desc '
        sql += 'limit %s'
        params = [limit]
        return Database.get_rows(sql, params)

    def get_last_detection():
        sql = "select timestamp, (case a.description when 'Detection Stopped' then 0 when 'Detection' then 1 end) as status "
        sql += "from history as h "
        sql += 'join device as d on h.deviceid = d.id '
        sql += 'join action as a on h.actionid = a.id '
        sql += "where d.name = 'Detector' "
        sql += "order by timestamp desc "
        sql += "limit 1"
        return Database.get_one_row(sql)

    def get_locker_statuses():
        sql = "select id, description from lockerstatus "
        return Database.get_rows(sql)


    # Locker    
    def get_lockers():
        sql = "select l.id, l.name, l.deviceid, ls.description as status "
        sql += "from locker as l "
        sql += "join lockerstatus as ls on l.Lockerstatusid = ls.id "
        sql += "order by l.id "
        return Database.get_rows(sql)

    def get_locker_details(id):
        sql = "select l.id, l.name, l.deviceid, ls.description as status "
        sql += "from locker as l "
        sql += "join lockerstatus as ls on l.Lockerstatusid = ls.id "
        sql += "where l.id = %s "
        params = [id]
        return Database.get_one_row(sql, params)

    def get_locker_status(id):
        sql = "select lockerstatusid "
        sql += "from locker as l "
        sql += "where l.id = %s "
        params = [id]
        return Database.get_one_row(sql, params)
    
    def get_locker_order(id):
        sql = "select orderid, o.name, email, tel, description "
        sql += "from locker as l "
        sql += "left join `order` as o on l.orderid = o.id "
        sql += "where l.id = %s "
        params = [id]
        return Database.get_one_row(sql, params)

    def get_locker_credentials(id):
        sql = "select id, orderid, code "
        sql += "from locker as l "
        sql += "where l.id = %s "
        params = [id]
        return Database.get_one_row(sql, params)

    def get_locker_lock_status(id):
        sql = "select l.deviceid, timestamp, (case a.description when 'Lock Closed' then 0 when 'Lock Opened' then 1 end) as status "
        sql += 'from history as h '
        sql += 'join device as d on h.deviceid = d.id '
        sql += 'join action as a on h.actionid = a.id '
        sql += 'join locker as l on d.id = l.deviceid '
        sql += 'where l.id = %s '
        sql += 'order by timestamp desc '
        sql += 'limit 1'
        params = [id]
        return Database.get_one_row(sql, params)

    def update_locker_code(id, code):
        sql = "update locker "
        sql += "set code = %s "
        sql += "where id = %s "
        params = [code, id]
        return Database.execute_sql(sql, params)

    def update_locker_status(id, statusid):
        sql = "update locker "
        sql += "set lockerstatusid = %s "
        sql += "where id = %s "
        params = [statusid, id]
        return Database.execute_sql(sql, params)

    def update_locker_order(id, orderid, statusid):
        sql = "update locker set orderid=%s, lockerstatusid=%s where id=%s; "
        params = [orderid, statusid, id]
        return Database.execute_sql(sql, params)

    def update_or_insert_order(orderid, name, email, tel, description):
        sql = "insert into `order` (id, name, email, tel, description) "
        sql += "values(%s, %s, %s, %s, %s) "
        sql += "on duplicate key update name=%s, email=%s, tel=%s, description=%s "
        params = [orderid, name, email, tel, description, name, email, tel, description]
        return Database.execute_sql(sql, params)

    def delete_locker_order(id):
        sql = "update locker set orderid=NULL, lockerstatusid=1 where id=%s; "
        params = [id]
        return Database.execute_sql(sql, params)
    
    def get_order(orderid):
        sql = "select id as orderid, name, email, tel, description from `order` as o where o.id = %s "
        sql += "union select %s as orderid, null as name, null as email, null as tel, null as description "
        sql += "limit 1 "
        params = [orderid, orderid]
        return Database.get_one_row(sql, params)

    