# main.py

from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
# from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
# from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem, ILeftBodyTouch
from kivy.properties import StringProperty
from kivymd.uix.chip import MDChip
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine



from kivy.uix.boxlayout import BoxLayout

from database import Database


database = Database()


#---------------------CUSTOM ELEMENTS-----------------------#

class CustomPill(IRightBodyTouch, MDChip):
    pass

class ListItemWithChip(OneLineAvatarIconListItem):
    '''Custom list item.'''

    icon = StringProperty("arm-flex")

    def __init__(self, **kwargs):
        super(ListItemWithChip, self).__init__(**kwargs)
        if self.text == 'Tasks':
            self.icon = StringProperty('arm-flex')
        elif self.text == 'Exercises':
            self.icon = StringProperty('arm-flex-outline')
        elif self.text == 'Streaks':
            self.icon = StringProperty('arm-flex')

    def get_icon(self):
        return self.icon

class InvalidLoginPopup(BoxLayout):
    """Opens dialog box when user enters invalid details when signing up or registering"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class UsernameAlreadyExists(BoxLayout):
    """Opens dialog box when the user enter username that already exists"""


class ListItemWithCheckbox(OneLineAvatarIconListItem):
    '''Custom list item'''

    def __init__(self, pk=None, userid=None, **kwargs):
        super().__init__(**kwargs)
        # self.ids.check.active = check
        self.pk = pk
        self.userid = userid


class LeftCheckbox(ILeftBodyTouch, MDCheckbox):
    '''Custom left container'''


class CustomExpansionPanel(MDBoxLayout):
    ''''''

#-------------------------------------------------------------#



#-------------------Screens-------------------------------#

class MainWindow(MDScreen):
    
    def on_pre_enter(self):
        self.panel =  MDExpansionPanel(
                content=CustomExpansionPanel(),
                panel_cls=MDExpansionPanelOneLine(text="Completed Tasks",),
                )
        self.ids.box.add_widget(self.panel)
        self.ids.box.add_widget(MDLabel())
        self.ids.emaillbl.text = database.get_logged_in_user_email()

        # get the list items from the database

        userid = database.get_logged_in_userid()[0]
        completed_tasks, uncomplete_tasks = database.get_tasks(userid)

        self.ids.taskspill.text = str(len(uncomplete_tasks))


        if uncomplete_tasks != []:
            for task in uncomplete_tasks:
                add_task = ListItemWithCheckbox(pk=task[0], userid=userid,text=task[1])
                self.ids.taskslist.add_widget(add_task)

        if completed_tasks != []:
            for task in completed_tasks:
                add_task = ListItemWithCheckbox(pk=task[0], userid=userid,text=task[1])
                add_task.ids.check.active = True
                self.panel.content.ids.donetasks.add_widget(add_task)


        


    def add_task(self, text):
        """Add task to list"""
        # get the user
        userid = database.get_logged_in_userid()[0]

        created_task = database.create_task(userid, text)

        task_text = created_task[1]
        taskid = created_task[0]


        self.ids.taskslist.add_widget(ListItemWithCheckbox(text=task_text, pk=taskid, userid=userid))
        self.ids.taskinput.text = ''
        self.ids.taskinput.focus = True
        self.update_tasks_pill()

    def update_tasks_pill(self):
        current_value = int(self.ids.taskspill.text)
        new_value = current_value + 1
        self.ids.taskspill.text = str(new_value)
    
    def subtract_from_pills(self):
        current_value = int(self.ids.taskspill.text)
        new_value = current_value - 1
        self.ids.taskspill.text = str(new_value)

    def logout(self):
        database.log_out_user()
        self.ids.taskslist.clear_widgets()
        self.ids.box.remove_widget(self.panel)
        # self.panel.content.ids.donetasks.clear_widgets()

    def delete_item(self, instance_check, widget):
        """Deletes the task from the data base"""

        if instance_check.active == True:
            self.panel.content.ids.donetasks.remove_widget(widget)
        else:
            self.ids.taskslist.remove_widget(widget)
            self.subtract_from_pills()


        database.delete_task(widget.userid, widget.pk)



        


    def mark(self, instance_check, widget):
        """Responds to checkbox being marked or unmarked"""
        if instance_check.active == True:
            # change values in the database
            database.mark_task_as_complete(widget.userid, widget.pk)

            # remove widget from the list
            self.ids.taskslist.remove_widget(widget)
            self.panel.content.ids.donetasks.add_widget(widget)
            self.subtract_from_pills()
        
        if instance_check.active == False:
            # change values in the database
            database.mark_task_as_uncomplete(widget.userid, widget.pk)

            self.panel.content.ids.donetasks.remove_widget(widget)
            self.ids.taskslist.add_widget(widget)
            self.update_tasks_pill()

        

class ExerciseWindow(MDScreen):
    pass

class LoginScreen(MDScreen):
    def login(self):
        email = self.ids.email.text
        password = self.ids.password.text
        if self.ids.keepmeloggedin.active == True:
            keep_me_logged = True
        else:
            keep_me_logged = False


        if email != '' and password != '':

            userid = database.get_user(email, password, keep_me_logged)

            # validate the user
            if userid == True:
                self.ids.email.text = ''
                self.ids.password.text=''
                return True
            elif userid == False:
                self.invalid_popup()
        
        else:
            self.invalid_popup()


    def invalid_popup(self):
        '''Pop up for invalid entries'''
        self.dialog = MDDialog(
                type="custom",
                content_cls= InvalidLoginPopup(),
                size_hint=(.4, .4),
                auto_dismiss=True,
            )

        self.dialog.open()



class SignupScreen(MDScreen):
    def create_user(self):
        email = self.ids.email.text
        password = self.ids.password.text

        if email != '' and password != '':
            if database.check_username(email) == False:
                database.create_user(email, password)
                self.ids.email.text = ''
                self.ids.password.text=''
                return True
            
            elif database.check_username(email) == True:
                self.username_exists_popup()
                return False


        else:
            self.invalid_popup()

            

    def invalid_popup(self):
        '''Pop up for invalid entries'''
        self.dialog = MDDialog(
                type="custom",
                content_cls= InvalidLoginPopup(),
                size_hint=(.4, .4),
                auto_dismiss=True,
            )

        self.dialog.open()


    def username_exists_popup(self):
        '''Pop up when username entered already exists'''
        self.username_dialog = MDDialog(
                type="custom",
                content_cls= UsernameAlreadyExists(),
                size_hint=(.4, .4),
                auto_dismiss=True,
            )

        self.username_dialog.open()

    def enable_signup_btn(self):
        self.ids.signupbtn.disabled = False


class ScreenManagement(ScreenManager):
    pass


#--------------------------------------------------------------------#



#-----------------------------MAIN APPLICATION------------------------#

class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = 'Green'
        # self.theme_cls.theme_style = "Dark" #or "Light"

    def on_start(self):
        if database.get_keep_logged_in() == True:
            self.root.current = 'mainwindow'
        else:
            self.root.current = 'login'

    def switch_window(self, window, boolean_val):
        if boolean_val == True:
            self.root.current = window
            self.root.transition.direction = "down"

        else:
            pass

    def on_stop(self):
        database.close_db_connection()



MainApp().run()