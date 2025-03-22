class ConnectionManager:
    def __init__(self, tree):
        self.tree = tree
        self.icons = {
            "valid": tk.PhotoImage(file="valid.png"),
            "invalid": tk.PhotoImage(file="invalid.png")
        }
        
    def add_connection(self, db_type, conn_name, config):
        # 添加到数据库和树形结构
        node = self.tree.insert(db_type, "end", text=conn_name)
        self.update_connection_status(node, config)
    
    def test_connection(self, config):
        # 测试数据库连接
        try:
            # 根据类型创建连接
            if config['type'] == 'mysql':
                conn = pymysql.connect(
                    host=config['host'],
                    user=config['user'],
                    password=config['password'],
                    database=config['schema']
                )
                conn.close()
                return True
            # 其他数据库类型...
        except Exception as e:
            return False
    
    def update_connection_status(self, node, config):
        if self.test_connection(config):
            self.tree.item(node, image=self.icons['valid'])
        else:
            self.tree.item(node, image=self.icons['invalid'])