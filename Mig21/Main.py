import tkinter as tk
from tkinter import ttk

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("数据导入配置工具")
        
        # 主界面分割
        self.paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=1)
        
        # 左侧树形结构
        self.tree_frame = tk.Frame(self.paned_window, width=200)
        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(fill=tk.BOTH, expand=1)
        
        # 右侧区域
        self.right_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.tree_frame)
        self.paned_window.add(self.right_frame)
        
        # 初始化树结构
        self.init_tree()
        
        # 绑定事件
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Button-3>", self.show_context_menu)

    def init_tree(self):
        # 创建根节点
        self.tree.insert("", "end", "connections", text="Connections")
        self.tree.insert("", "end", "selection", text="Selection")
        self.tree.insert("", "end", "class", text="Class")
        self.tree.insert("", "end", "import", text="Import")
        
        # 添加示例数据
        self.tree.insert("connections", "end", "mysql", text="MySQL")
        self.tree.insert("mysql", "end", "conn1", text="Local DB")

    def show_context_menu(self, event):
        # 右键菜单实现
        pass

    def on_tree_select(self, event):
        # 处理节点选择事件
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()