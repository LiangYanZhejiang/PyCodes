import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QTextEdit, QPushButton, QSplitter, QAction, QMenu
from PyQt5.QtCore import Qt

class DataImportTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("数据导入工具")
        self.setGeometry(100, 100, 1200, 800)

        splitter = QSplitter(Qt.Horizontal)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("配置项")
        self.tree.itemClicked.connect(self.on_item_clicked)
        splitter.addWidget(self.tree)

        self.right_panel = QTextEdit()
        splitter.addWidget(self.right_panel)

        self.init_tree()

        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(splitter)

        execute_button = QPushButton("执行")
        execute_button.clicked.connect(self.execute_selection)
        layout.addWidget(execute_button)

        container.setLayout(layout)
        self.setCentralWidget(container)

    def init_tree(self):
        self.connections_node = QTreeWidgetItem(self.tree, ["Connections"])

        self.selection_node = QTreeWidgetItem(self.tree, ["Selection"])

        self.class_node = QTreeWidgetItem(self.tree, ["Class"])

        self.import_node = QTreeWidgetItem(self.tree, ["Import"])

        # 示例数据库类型
        mysql_node = QTreeWidgetItem(self.connections_node, ["MySQL"])
        mysql_conn = QTreeWidgetItem(mysql_node, ["Test MySQL Connection"])

        selection_example = QTreeWidgetItem(self.selection_node, ["User Selection"])
        QTreeWidgetItem(selection_example, ["Test MySQL Connection"])

        class_example = QTreeWidgetItem(self.class_node, ["User Class"])

        import_example = QTreeWidgetItem(self.import_node, ["User Import"])

    def on_item_clicked(self, item, column):
        self.right_panel.setText(f"选中: {item.text(column)}")

    def execute_selection(self):
        self.right_panel.append("执行 selection...")

    def contextMenuEvent(self, event):
        item = self.tree.currentItem()
        if not item:
            return

        menu = QMenu(self)

        if item == self.connections_node:
            add_action = QAction("添加连接", self)
            add_action.triggered.connect(self.add_connection)
            menu.addAction(add_action)

        elif item.parent() == self.connections_node:
            delete_action = QAction("删除连接", self)
            delete_action.triggered.connect(lambda: self.delete_node(item))
            menu.addAction(delete_action)

        menu.exec_(event.globalPos())

    def add_connection(self):
        new_conn = QTreeWidgetItem(self.connections_node, ["New Connection"])

    def delete_node(self, item):
        parent = item.parent()
        if parent:
            parent.removeChild(item)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DataImportTool()
    window.show()
    sys.exit(app.exec_())
