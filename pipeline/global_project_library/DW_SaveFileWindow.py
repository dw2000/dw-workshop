import getpass

from PySide2.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QComboBox, QPushButton, QLabel, QMessageBox, QMainWindow, QLineEdit, QFrame, QSizePolicy 
)
from PySide2.QtGui import QRegExpValidator
from PySide2.QtCore import Slot, Signal, QObject, Qt, QRegExp


class SaveFileDialog(QDialog):

    def __init__(self, job_data, file_ext, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save File")
        self.setMinimumWidth(450)
        #self.setMinimumHeight(600)

        self.job_data = job_data

        self.depth = self._get_dict_depth(self.job_data.folders_dict)    

        self.directory_combo_list = []
        self.menuInitChoice = "Pick one..."
        self.menuAddChoice = "Add a new one..."
        self.menuMissingChoice = "Nothing found."

        # Custom user role to tag menu items to ignore.
        self.ignoreMe = Qt.UserRole

        self.output_dictionary = {} # this will hold all the output data needed to save and log the file
        self.output_dictionary["file_ext"] = file_ext   

        self._create_layouts()
        self._connect_signals()



    def _get_dict_depth(self, d):
        # Calculates the maximum recursive depth of a dictionary of dictionaries.
        if not isinstance(d, dict) or not d:
            return -1

        max_depth = 0
        for value in d.values():
            if isinstance(value, dict):
                max_depth = max(max_depth, self._get_dict_depth(value))

        return max_depth + 1
            



    def _create_layouts(self):

        main_layout = QVBoxLayout(self)

        #################
        # Directory selection layout
        dir_layout = QVBoxLayout()

        self.directory_label = QLabel("Choose Save Location:")
        self.directory_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        dir_layout.addWidget(self.directory_label)


        # The number of directory combos is adaptive to the depth of the folders_dict, so we are storing them in a list.
        for i in range(self.depth):
            directory_combo = QComboBox(self)
            directory_combo.setProperty("menu_index", i)
            directory_combo.hide()
            directory_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            directory_combo.setMinimumWidth(300)
            dir_layout.addWidget(directory_combo)
            self.directory_combo_list.append(directory_combo)

        # Initialize the first menu
        directories = next(iter(self.job_data.folders_dict.values()))
        self.directory_combo_list[0].addItem(self.menuInitChoice)  
        self.directory_combo_list[0].setItemData(0, True, self.ignoreMe)

        for name in directories.keys():
            self.directory_combo_list[0].addItem(name)  

        self.directory_combo_list[0].show()  
    
        main_layout.addLayout(dir_layout)

        ##################

        #################
        # step selection layout
        step_layout = QVBoxLayout()

        self.step_label = QLabel("Step/Department:")
        self.step_label.hide()
        self.step_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)        
        step_layout.addWidget(self.step_label)

        self.step_combo = QComboBox(self)
        self.step_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.step_combo.setMinimumWidth(300)
        self.step_combo.hide()
        step_layout.addWidget(self.step_combo)

        self.step_combo.addItem(self.menuInitChoice) 
        self.step_combo.setItemData(0, True, self.ignoreMe)

        for name in self.job_data.step_list:
            self.step_combo.addItem(name)

    
        main_layout.addLayout(step_layout)

        ##################

        #################
        # Task selection layout
        task_layout = QVBoxLayout()

        self.task_label = QLabel("Task/Element:")
        self.task_label.hide()
        self.task_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)             
        task_layout.addWidget(self.task_label)

        self.task_combo = QComboBox(self)
        self.task_combo.hide()
        self.task_combo.setEnabled(False)
        self.task_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.task_combo.setMinimumWidth(300)
        task_layout.addWidget(self.task_combo)

        #self.task_combo.addItem(self.menuAddChoice)
        self.task_combo.setItemData(self.task_combo.findText(self.menuAddChoice), True, self.ignoreMe)  

        main_layout.addLayout(task_layout)

        ##################


        #################
        # Text notes edit
        notes_layout = QVBoxLayout()

        self.notes_edit = QLineEdit(self)
        self.notes_edit.setPlaceholderText("Enter any notes here.")
        self.notes_edit.setMaxLength(100)        
        self.notes_edit.hide()
        #self.notes_edit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)        

        regex_letters = QRegExp(r"[^'\"\\#|;\x00-\x1F]*")   # Dissallow some troublesome characters.
        input_validator = QRegExpValidator(regex_letters, self.notes_edit)
        self.notes_edit.setValidator(input_validator)

        task_layout.addWidget(self.notes_edit)
    
        main_layout.addLayout(notes_layout)

        ##################


        #################
        # Output path preview

        output_preview_layout = QVBoxLayout()

        self.horizontal_divider_0 = QFrame(self)
        self.horizontal_divider_0.setFrameShape(QFrame.HLine) 
        self.horizontal_divider_0.setFrameShadow(QFrame.Sunken) 
        output_preview_layout.addWidget(self.horizontal_divider_0)

        self.output_preview = QLineEdit(self)
        self.output_preview.setPlaceholderText("Your output path will appear here.")
        self.output_preview.setEnabled(False)
        #self.output_preview.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)          
        output_preview_layout.addWidget(self.output_preview)
    
        main_layout.addLayout(output_preview_layout)

        ##################


        ##################
        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.addStretch() # Pushes buttons to the right

        self.save_button = QPushButton("Save", self)
        self.cancel_button = QPushButton("Cancel", self)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

        #################

        self.setLayout(main_layout)


    def updateTaskMenu(self, add_item=None):   # The task menu queries external data in order to dynamically change context-wise.
        self.task_combo.clear()
        task_list = self.job_data.updateTaskList(search_dir=self.output_dictionary["output_dir"])

        if add_item is not None:
            task_list = self.job_data.updateTaskList(add_item=add_item)

        for name in task_list:
            self.task_combo.addItem(name)
        self.task_combo.addItem(self.menuAddChoice)



    def _connect_signals(self):
        #Connect the main directory combo box's selection change to update the subfolder combo box
        
        for each in self.directory_combo_list:    
            menu_index = each.property("menu_index")
            each.currentIndexChanged.connect(lambda state, val=menu_index: self._update_subfolders(val))
            each.currentIndexChanged.connect(self._update_output_path)           


        self.step_combo.currentIndexChanged.connect(self._update_output_path)
        self.step_combo.currentIndexChanged.connect(self._update_steps)


        self.task_combo.currentIndexChanged.connect(self._update_tasks)
        self.task_combo.currentIndexChanged.connect(self._update_output_path)
        
        self.save_button.clicked.connect(self._on_save_clicked)
        self.save_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.reject) # QDialog built-in slot to close with reject code
        


    @Slot()
    def _update_subfolders(self, menu_index):

        # Clears and repopulates the subfolder combo box based on the current selection.

        current_combo = self.directory_combo_list[menu_index]
        current_selection = current_combo.currentText()


        if current_combo.itemText(0) == self.menuInitChoice:
            current_combo.blockSignals(True)
            current_combo.removeItem(0)
            current_combo.blockSignals(False)

        directories = next(iter(self.job_data.folders_dict.values()))


        # This cycles through as many layers as needed to get to the current part of the dictionairy
        for i in range(menu_index):
            prev_selection = self.directory_combo_list[i].currentText()
            directories = directories[prev_selection]


        if isinstance(directories, dict):    # If we've come to a list we are at the end.

            # Make sure the next two steps are disabled.
            self.step_combo.setEnabled(False)
            self.task_combo.setEnabled(False)

            next_combo = self.directory_combo_list[menu_index + 1]

            next_choices = directories[current_selection]
            
            if isinstance(next_choices, dict):
                subfolders = list(next_choices.keys())
            elif isinstance(next_choices, list):
                subfolders = next_choices          

            next_combo.blockSignals(True) 
            next_combo.clear() # Clear existing items     
            next_combo.addItem(self.menuInitChoice)    
            next_combo.setItemData(0, True, self.ignoreMe)                
            next_combo.show()
            next_combo.blockSignals(False)   


            if subfolders:   
                next_combo.addItems(subfolders)

            else:
                next_combo.addItem(self.menuMissingChoice)
                next_combo.setItemData(1, True, self.ignoreMe)

            menu_index +=1

        else: # We've gone as deep as we are going and have just selected something from a list, so make sure the next two steps are enabled now.
            self.step_label.show()
            self.step_combo.show()
            self.step_combo.setEnabled(True)            

            self.task_label.show()
            self.task_combo.show()
            if self.step_combo.itemData(self.step_combo.currentIndex(), self.ignoreMe) is None:
                self.updateTaskMenu()
                self.task_combo.setEnabled(True)   # Only enabling this if a valid choice had been made on step_combo


        # Hide remaining menus down the list
        for i in range(menu_index + 1, len(self.directory_combo_list)):
            another_combo = self.directory_combo_list[i]
            another_combo.hide()



    @Slot()
    def _update_steps(self):

        #current_selection = self.step_combo.currentText()
        if self.step_combo.itemText(0) == self.menuInitChoice:
            self.step_combo.blockSignals(True)
            self.step_combo.removeItem(0)
            self.step_combo.blockSignals(False)

        self.task_combo.setEnabled(True)

        self.updateTaskMenu()

        self.notes_edit.show()  



    @Slot()
    def _update_tasks(self):
        if self.task_combo.currentText() == self.menuAddChoice:   # Has the user selected the "add a new one" item on the list?
            dialog = TaskAddDialog(parent=self, title="Task Name Input", label_text="Please enter the task to add:")

            #dialog.text_entered.connect(lambda text: print(f"Signal emitted: '{text}'"))

            # Show the dialog and wait for it to close
            result = dialog.exec_() 

            if result == 1:
                entered_string = dialog.get_text()

                self.task_combo.clear()
                task_list = self.updateTaskMenu(add_item=entered_string)
                self.task_combo.addItem(self.menuAddChoice)
                self.task_combo.setCurrentText(entered_string)
            else:
                self.task_combo.setCurrentIndex(0)                


    @Slot()
    def _update_output_path(self):  # Just regenerating it from scratch every time.
        self.save_button.setEnabled(False)
        # Start with the project file path:
        self.output_dictionary["output_dir"] = list(self.job_data.folders_dict.keys())[0]

        self.output_dictionary["output_file"] = ""  # We'll build the file name in parellel with the dir, then combine them.

        keep_going = True

        current_text = ""

        for each in self.directory_combo_list:   
            if each.isVisible() is True:   
                if each.itemData(each.currentIndex(), self.ignoreMe) is None:
                    current_text = each.currentText()
                    self.output_dictionary["output_dir"] += "/" + current_text
                else:
                    keep_going = False



        if keep_going:
            self.output_dictionary["output_file"] += current_text
            if self.step_combo.isVisible() is True:
                if self.step_combo.itemData(self.step_combo.currentIndex(), self.ignoreMe) is None:
                    self.output_dictionary["output_dir"] += "/" + self.job_data.work_dir
                    current_text = self.step_combo.currentText()
                    self.output_dictionary["output_dir"] += "/" + current_text
                else:
                    keep_going = False

        if keep_going:
            self.output_dictionary["output_file"] += "_" + current_text
            if self.task_combo.isVisible() is True:
                if self.task_combo.itemData(self.task_combo.currentIndex(), self.ignoreMe) is None:
                    current_text = self.task_combo.currentText()
                    self.output_dictionary["output_dir"] += "/" + current_text
                    self.output_dictionary["output_file"] += "_" + current_text   
                    self.output_dictionary["base_name"] = self.output_dictionary["output_file"]

                    latest_version = self.job_data.getLatestVersion(self.output_dictionary["output_dir"] + "/" + self.output_dictionary["output_file"] + "_v000" + "." + self.output_dictionary["file_ext"])
                    self.output_dictionary["output_file"] += "_v" + str(latest_version + 1).rjust(3, "0") + "." + self.output_dictionary["file_ext"]  
                    self.output_dictionary["version"] = latest_version + 1
                    
            # We only form the full file path and turn on the Save button if we were able to get this far and actually have a full file path.
            self.output_preview.setText(self.output_dictionary["output_dir"] + "/" + self.output_dictionary["output_file"] + "    ")
            self.save_button.setEnabled(True)

        else:
            self.output_preview.setText(self.output_dictionary["output_dir"] + "    ")



    @Slot()
    def _on_save_clicked(self):

        self.output_dictionary["user"] = getpass.getuser()      
        self.output_dictionary["notes"] = self.notes_edit.text()

        self.accept() # QDialog built-in slot to close with accept code





class TaskAddDialog(QDialog):

    def __init__(self, parent=None, title="", label_text=""):

        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)  # Make the dialog modal (blocks parent window)

        self.init_ui(label_text)

    def init_ui(self, label_text):

        # Main vertical layout for the dialog content
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20) # Add some padding
        main_layout.setSpacing(15) # Spacing between widgets

        # Label for the input field
        self.label = QLabel(label_text)
        self.label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.label)

        # Text entry field
        self.text_input = QLineEdit(self)
        self.text_input.setMaxLength(15)
        self.text_input.setPlaceholderText("Type here...")

        regex_letters = QRegExp(r"[a-zA-Z0-9_\s]*")  # Only allow the user to type letters, numbers, underscores and spaces.
        input_validator = QRegExpValidator(regex_letters, self.text_input)
        self.text_input.setValidator(input_validator)

        self.text_input.textChanged.connect(self.convert_spaces_to_underscores)

        main_layout.addWidget(self.text_input)

        # Horizontal layout for buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10) # Spacing between buttons

        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject) # QDialog's reject() closes with QDialog.Rejected
        button_layout.addWidget(self.cancel_button)

        # OK button
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self._on_ok_clicked) # Connect to custom handler for validation/emission
        button_layout.addWidget(self.ok_button)

        # Add button layout to the main layout
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Set initial focus to the text input field
        self.text_input.setFocus()


    def convert_spaces_to_underscores(self, current_text):

        # Store the current cursor position before text modification
        cursor_pos = self.text_input.cursorPosition()

        new_text = current_text.replace(' ', '_')

        # Only update the text if it actually changed to avoid infinite loop.
        # setText also emits textChanged, so we need to prevent re-calling this slot.
        if new_text != current_text:
            self.text_input.setText(new_text)

            # Restore cursor position. 
            self.text_input.setCursorPosition(cursor_pos)


    def _on_ok_clicked(self):

        # Emits the text and accepts the dialog.
        
        entered_text = self.text_input.text()
        if not entered_text.strip(): # Basic validation: check if text is empty or just whitespace
            QMessageBox.warning(self, "Input Error", "Please enter some text.")
            return

        self.accept() #Closes with QDialog.Accepted


    def get_text(self):
        # Returns the text currently in the input field. This can be called after the dialog has been accepted.
        return self.text_input.text()



def open_save_dialog(job_data, file_ext):
    dialog = SaveFileDialog(job_data, file_ext)
    dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
    # Show the dialog modally (blocks interaction with parent window)
    result = dialog.exec_()

    if result == QDialog.Accepted:
        print("Saving...")
        return dialog.output_dictionary
    elif result == QDialog.Rejected:
        print("Save operation cancelled.")
        return None



