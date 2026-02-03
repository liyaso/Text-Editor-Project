"""
This file is used for execution and has the basic build of the GUI
"""

import os
import sys
from pathlib import Path

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyQt5.Qsci import *

from editor import Editor
from fuzzy_searcher import SearchItem, SearchWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        # add before init
        self.side_bar_clr = "#282c34"

        self.init_ui()

        self.current_file = None
        self.current_side_bar = None
  
    # deals with anything related to the user interface (UI)
    def init_ui(self):
        self.setWindowTitle("Liya Sojan's Text Editor")             # title of the pop up window
        self.resize(1300, 900)                                      # resize the popup window

        self.setStyleSheet(open("./src/css/style.qss", "r").read()) # used to design the text editor

        self.window_font = QFont("Arial")
        self.window_font.setPointSize(12)
        self.setFont(self.window_font)                              # set the font and the font size for the text editor

        self.set_up_menu()                                          # will be used to create a menu bar in the text editor
        self.set_up_body()                                          # will be used to set up the body of the text editor
        self.statusBar().showMessage("Hello")

        self.show()

    def set_up_menu(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("File")

        new_file = file_menu.addAction("New")                       # Create a new file
        new_file.setShortcut("Ctrl+N")
        new_file.triggered.connect(self.new_file)

        open_file = file_menu.addAction("Open File")                # Open a file
        open_file.setShortcut("Ctrl+O")
        open_file.triggered.connect(self.open_file)
        
        open_folder = file_menu.addAction("Open Folder")            # Open Folder
        open_folder.setShortcut("Ctrl+K")
        open_folder.triggered.connect(self.open_folder)

        file_menu.addSeparator()

        save_file = file_menu.addAction("Save")                     # Save the current file
        save_file.setShortcut("Ctrl+S")
        save_file.triggered.connect(self.save_file)

        save_as = file_menu.addAction("Save As")                    # Save a file
        save_as.setShortcut("Ctrl+Shift+S")
        save_as.triggered.connect(self.save_as)

        # Edit Menu
        edit_menu = menu_bar.addMenu("Edit")

        copy_action = edit_menu.addAction("Copy")                   # Used to copy something
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy)
    
    def get_editor(self, path: Path = None, is_python_file=True) -> QsciScintilla:                 # function will be used to get an editor instnace to add it to a tab
        # creating an instance of the editor class and returning it
        editor = Editor(self, path=path, is_python_file=is_python_file)
        return editor

    # function to check if the file is binary or not
    # ex. image file, exe, and zi file that can't be opened using text editors   
    def is_binary(self, path):
        with open(path, 'rb') as f:
            return b'\0' in f.read(1024)

    def set_new_tab(self, path: Path, is_new_file=False):
        # adding extentions that may be conidered as python files
        editor = self.get_editor(path, path.suffix in {".py", ".pyw"})

        if is_new_file:
            self.tab_view.addTab(editor, "untitled")
            self.setWindowTitle("untitled")
            self.statusBar().showMessage("Opened untitled")
            self.tab_view.setCurrentIndex(self.tab_view.count() - 1)
            self.current_file = None
            return

        if not path.is_file():
            return
        if self.is_binary(path):
            self.statusBar().showMessage("Cannot Open Binary File", 2000)
            return

        # check if file already open
        for i in range(self.tab_view.count()):
            if self.tab_view.tabText(i) == path.name:
                self.tab_view.setCurrentIndex(i)
                self.current_file = path
                return

        # create new tab 
        self.tab_view.addTab(editor, path.name)
        editor.setText(path.read_text())
        self.setWindowTitle(path.name)
        self.current_file = path
        self.tab_view.setCurrentIndex(self.tab_view.count() - 1)
        self.statusBar().showMessage(f"Opened {path.name}", 2000)

    def set_cursor_pointer(self, e):
        self.setCursor(Qt.PointingHandCursor)

    def set_cursor_arrow(self, e):
        self.setCursor(Qt.ArrowCursor)

    def get_side_bar_label(self, path, name):
        label = QLabel()
        label.setPixmap(QPixmap(path).scaled(QSize(30, 30)))
        label.setAlignment(Qt.AlignmentFlag.AlignTop)
        label.setFont(QFont("Arial", 12))
        label.mousePressEvent = lambda e: self.show_hide_tab(e, name)
        # Chaning Cursor on hover
        label.enterEvent = self.set_cursor_pointer
        label.leaveEvent = self.set_cursor_arrow
        return label
    
    def get_frame(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.NoFrame)
        frame.setFrameShadow(QFrame.Plain)
        frame.setContentsMargins(0, 0, 0, 0)
        frame.setStyleSheet('''
            QFrame {
                background-color: #21252b;
                border-radius: 5px;
                border: none;
                padding: 5px;
                color: #D3D3D3;
            }
            QFrame:hover {
                color: white;
            }
        ''')
        return frame

    def set_up_body(self):
        # Body
        body_frame = QFrame()
        body_frame.setFrameShape(QFrame.NoFrame)
        body_frame.setFrameShadow(QFrame.Plain)
        body_frame.setLineWidth(0)
        body_frame.setMidLineWidth(0)
        body_frame.setContentsMargins(0, 0, 0, 0)
        body_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body_frame.setLayout(body)

        ###### Side Bar ##########
        self.side_bar = QFrame()
        self.side_bar.setFrameShape(QFrame.StyledPanel)
        self.side_bar.setFrameShadow(QFrame.Plain)
        self.side_bar.setStyleSheet(f'''
            background-color: {self.side_bar_clr};
        ''')
        side_bar_layout = QVBoxLayout()
        side_bar_layout.setContentsMargins(5, 10, 5, 0)
        side_bar_layout.setSpacing(0)
        side_bar_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        # setup labels
        folder_label = self.get_side_bar_label( "./src/icons/folder-icon.svg", "folder-icon")
        side_bar_layout.addWidget(folder_label)

        search_label = self.get_side_bar_label("./src/icons/search-icon", "search-icon")
        side_bar_layout.addWidget(search_label)

        self.side_bar.setLayout(side_bar_layout)  

        # split view
        self.hsplit = QSplitter(Qt.Horizontal)

        ###### FILE MANAGER ##########
        # frame & layout to hold tree view (file manager)
        self.file_manager_frame = self.get_frame()
        self.file_manager_frame.setMaximumWidth(400)
        self.file_manager_frame.setMinimumWidth(200)
        tree_frame_layout = QVBoxLayout()
        tree_frame_layout.setContentsMargins(0, 0, 0, 0)
        tree_frame_layout.setSpacing(0)

        # Create file system model to show in tree view
        """Root path is the starting path for the file manager you can add whatever directory necessary"""
        self.model = QFileSystemModel()
        self.model.setRootPath(os.getcwd())

        # File system Filters
        self.model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)

        ###### Tree View/File Viewer  ##########
        self.tree_view = QTreeView()
        self.tree_view.setFont(QFont("Arial, 13"))
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(os.getcwd()))
        self.tree_view.setSelectionMode(QTreeView.SingleSelection)
        self.tree_view.setSelectionBehavior(QTreeView.SelectRows)
        self.tree_view.setEditTriggers(QTreeView.NoEditTriggers)

        # add custom context menu
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.tree_view_context_menu)

        # handling clicks
        self.tree_view.clicked.connect(self.tree_view_clicked)
        self.tree_view.setIndentation(10)
        self.tree_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        """ Hide header and hide the other columns excet for name
            removing header & others such as file size, and date from FileSystem model"""
        self.tree_view.setHeaderHidden(True) # hiding header
        self.tree_view.setColumnHidden(1, True)
        self.tree_view.setColumnHidden(2, True)
        self.tree_view.setColumnHidden(3, True)

        ###### SEARCH VIEW ##########
        self.search_frame = self.get_frame()
        self.search_frame.setMaximumWidth(400)
        self.search_frame.setMinimumWidth(200)
        
        search_layout = QVBoxLayout()
        search_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        search_layout.setContentsMargins(0, 10, 0, 0)
        search_layout.setSpacing(0)

        search_input = QLineEdit()
        search_input.setPlaceholderText("Search")
        search_input.setFont(self.window_font)
        search_input.setAlignment(Qt.AlignmentFlag.AlignTop)

        ############# CHECKBOX ################
        self.search_checkbox = QCheckBox("Search in modules")
        self.search_checkbox.setFont(self.window_font)
        self.search_checkbox.setStyleSheet("color: white; margin-bottom: 10px;")
         
        self.search_worker = SearchWorker()
        self.search_worker.finished.connect(self.search_finshed)

        search_input.textChanged.connect(
            lambda text: self.search_worker.update(
                text,
                self.model.rootDirectory().absolutePath(),
                self.search_checkbox.isChecked()
            )
        )

        ###### SEARCH ListView ##########
        self.search_list_view = QListWidget()
        self.search_list_view.setFont(QFont("Arial", 13))
        self.search_list_view.setStyleSheet("""
        QListWidget {
            background-color: #21252b;
            border-radius: 5px;
            border: 1px solid #D3D3D3;
            padding: 5px;
            color: #D3D3D3;
        }
        """)

        self.search_list_view.itemClicked.connect(self.search_list_view_clicked)

        search_layout.addWidget(self.search_checkbox)
        search_layout.addWidget(search_input)
        search_layout.addSpacerItem(QSpacerItem(5, 5, QSizePolicy.Minimum, QSizePolicy.Minimum))
        search_layout.addWidget(self.search_list_view)

        self.search_frame.setLayout(search_layout)
        
        # setup layout
        tree_frame_layout.addWidget(self.tree_view)
        self.file_manager_frame.setLayout(tree_frame_layout)
        
        ###### Tab VIEW ##########

        # Tab Widget to add editor to
        self.tab_view = QTabWidget()
        self.tab_view.setContentsMargins(0, 0, 0, 0)
        self.tab_view.setTabsClosable(True)
        self.tab_view.setMovable(True)
        self.tab_view.setDocumentMode(True)
        self.tab_view.tabCloseRequested.connect(self.close_tab)

        ###### Setup Widgets ##########
        # add tree_view to tree_frame_layout & set tree_frame's layout as that 
        # add tree view and tab view
        self.hsplit.addWidget(self.file_manager_frame)
        self.hsplit.addWidget(self.tab_view)

        body.addWidget(self.side_bar)
        body.addWidget(self.hsplit)
        body_frame.setLayout(body)

        self.setCentralWidget(body_frame)

    def search_finshed(self, items):
        self.search_list_view.clear()
        for i in items:
            self.search_list_view.addItem(i)
    
    def search_list_view_clicked(self, item):
        self.set_new_tab(Path(item.full_path))
        editor: Editor = self.tab_view.currentWidget()
        editor.setCursorPosition(item.lineno, item.end)
        editor.setFocus()   

    def close_tab(self, index):
        self.tab_view.removeTab(index)
    # this function will change the sidebar contents (frame) depending on which icon is clicked
    def show_hide_tab(self, e, type_):
        if type_ == "folder-icon":
            if not (self.file_manager_frame in self.hsplit.children()):
                self.hsplit.replaceWidget(0, self.file_manager_frame)
        elif type_ == "search-icon":
            if not (self.search_frame in self.hsplit.children()):
                self.hsplit.replaceWidget(0, self.search_frame)

        if self.current_side_bar == type_:
            frame = self.hsplit.children()[0]
            if frame.isHidden():
                frame.show()
            else:
                frame.hide()
        
        self.current_side_bar = type_

    def tree_view_context_menu(self, pos):
        pass
    
    def tree_view_clicked(self, index: QModelIndex):
        path = self.model.filePath(index)
        p = Path(path)
        self.set_new_tab(p)

    def new_file(self):
        self.set_new_tab(None, is_new_file=True)
        # None is passed as path as the function wont use it because its a new empty file
    
    def save_file(self):
        if self.current_file is None and self.tab_view.count() > 0:
            self.save_as()

        editor = self.tab_view.currentWidget()
        self.current_file.write_text(editor.text())
        self.statusBar().showMessage(f"Saved {self.current_file.name}", 2000)
    
    def save_as(self):
        # save as
        editor = self.tab_view.currentWidget()
        if editor is None:
            return
        
        file_path = QFileDialog.getSaveFileName(self, "Save as", os.getcwd())[0]
        if file_path == '':
            self.statusBar().showMessage("Cancelled", 2000)
            return
        path = Path(file_path)
        path.write_text(editor.text())
        self.tab_view.setTabText(self.tab_view.currentIndex(), path.name)
        self.statusBar().showMessage(f"Saved {path.name}", 2000)
        self.current_file = path

    def open_file(self):
        # open file
        ops = QFileDialog.Options()
        ops |= QFileDialog.DontUseNativeDialog
        # will add support for opening multiple files later, for now it only opens one at a time
        new_file, _ = QFileDialog.getOpenFileName(self,
                    "Pick A File", "", "All Files [*];;Python Files [*.py]",
                    options=ops)
        if new_file == '':
            self.statusBar().showMessage("Cancelled", 2000)
            return
        f = Path(new_file)
        self.set_new_tab(f)
  
    def open_folder(self):
        # open folder
        ops = QFileDialog.Options()
        ops |= QFileDialog.DontUseNativeDialog

        new_folder = QFileDialog.getExistingDirectory(self, "Pick A Folder", "", options=ops)
        if new_folder:
            self.model.setRootPath(new_folder)
            self.tree_view.setRootIndex(self.model.index(new_folder))
            self.statusBar().showMessage(f"Opened {new_folder}", 2000)

    def copy(self):
        editor = self.tab_view.currentWidget()
        if editor is not None:
            editor.copy()

# The below code allows for the text editor window to pop up
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())