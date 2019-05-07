from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
import os
import socket_client 
import sys
from kivy.clock import Clock


# connect page
class ConnectPage(GridLayout): # inharite from GridLayout Class
    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # to use GridLayout class
        self.cols = 2

        # to auto file with last login
        if os.path.isfile("Logs.txt"):  # check is the is exist or not
            with open('Logs.txt', 'r') as f:  # if exist then open read mode
                d = f.read().split(',')  # as we separated logs with ','
                # storing previous ip,port and name
                prev_ip = d[0]
                prev_port = d[1]
                prev_name = d[2]
        # if there is no previous login details then set it to empty
        else:  
            prev_ip = ''
            prev_port = ''
            prev_name = ''

        # for first row IP field
        self.add_widget(Label(text='IP: '))
        self.ip = TextInput(text=prev_ip, multiline=False)  # text = prev_ip put the previous value
        self.add_widget(self.ip)

        # for first row port field
        self.add_widget(Label(text='PORT: '))
        self.port = TextInput(text = prev_port, multiline=False)
        self.add_widget(self.port)

        # for first row Name field
        self.add_widget(Label(text='Name: '))
        self.name = TextInput(text = prev_name, multiline=False)
        self.add_widget(self.name)

        # add buttom
        self.btn = Button(text = "Enter")
        self.btn.bind(on_press = self.enter_button)
        self.add_widget(Label())
        self.add_widget(self.btn)

    # when Enter button is pressed then save the login details
    def enter_button(self,instance):
        port = self.port.text
        ip = self.ip.text
        name = self.name.text
        with open("Logs.txt", 'w') as f: # Open the file in write mode
            f.write(f'{ip},{port},{name}') # write the values

        # for display the login details in InFoPage
        info = f"Try to connect with ip: {ip} , port: {port} and name: {name}" 
        chat_app.info_page.update_info(info) # pass the login details
        chat_app.screen_manager.current = "Info" # set screen manager to the InFo page
        Clock.schedule_once(self.connect, 1) # Display the info page for one second

    # connect client with server 
    def connect(self,_):
        ip = self.ip.text
        port = int(self.port.text)
        name = self.name.text

        # if Unable to connect the retrun the errors
        if not socket_client.connect(ip, port, name, show_error):
            return
        # if successfully connected the go to the Chat Page
        chat_app.create_chat_page()
        chat_app.screen_manager.current = "Chat"


# Info Page class
class InfoPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.message = Label(halign = "center",valign = "middle", font_size = 30)
        self.message.bind(width = self.update_text_width)
        self.add_widget(self.message)

    # to update the message
    def update_info(self, message):
        self.message.text = message

    # resize the message
    def update_text_width(self, *_):
        self.message.text_size = (self.message.width*0.9, None)

# Design
# ================================================================================== #
# |------------------------|           row = 2
# |Chat History Here       |           col = 1
# |                        |
# |                        |
# |                        |
# |------------------------|
# |Type msg    |   Send msg|  
# |            |           |
# |------------------------|

class ChatPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.rows = 2

        # for chat history Window (row = 1)
        
        self.history = ScrollableLabel(height = Window.size[1]*0.9,size_hint_y = None)
        self.add_widget(self.history)

        # for type message window (row = 2,col = 1)
        self.new_message = TextInput(width = Window.size[0]*0.8,size_hint_x=None,multiline=False)

        # for send button (row = 2, col = 2)
        self.send = Button(text = "Send")
        self.send.bind(on_press = self.send_message) # bind send_message function with the button

        bottom_line = GridLayout(cols = 2)
        bottom_line.add_widget(self.new_message) # (row = 2,col = 1)
        bottom_line.add_widget(self.send) # (row = 2, col = 2)
        self.add_widget(bottom_line)

        Window.bind(on_key_down = self.on_key_down)

        Clock.schedule_once(self.focus_text_input,1)
        socket_client.start_listening(self.incoming_message,show_error)
        self.bind(size=self.adjust_fields)

        # Updates page layout
    def adjust_fields(self, *_):

        # Chat history height - 90%, but at least 50px for bottom new message/send button part
        if Window.size[1] * 0.1 < 50:
            new_height = Window.size[1] - 50
        else:
            new_height = Window.size[1] * 0.9
        self.history.height = new_height

        # New message input width - 80%, but at least 160px for send button
        if Window.size[0] * 0.2 < 160:
            new_width = Window.size[0] - 160
        else:
            new_width = Window.size[0] * 0.8
        self.new_message.width = new_width

        # Update chat history layout
        #self.history.update_chat_history_layout()
        Clock.schedule_once(self.history.update_chat_history_layout, 0.01)

    def on_key_down(self,instance,keyboard,keycode,text,modifiers):
        if keycode == 40:
            self.send_message(None)

    def send_message(self, _):
        message = self.new_message.text
        self.new_message.text =  ""
        if message:
            self.history.update_chat_history(f"[color=dd2020]{chat_app.connect_page.name.text}[/color] > {message}")
            socket_client.send(message)
        Clock.schedule_once(self.focus_text_input,0.1) 

    def focus_text_input(self,_):
        self.new_message.focus = True

    def incoming_message(self,username,message):
        self.history.update_chat_history(f"[color=dd20202]{name}[/color] > {message}")

# scrool the chat history layout
class ScrollableLabel(ScrollView):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.layout = GridLayout(cols = 1, size_hint_y = None) # Screen Layout
        self.add_widget(self.layout)

        self.chat_history = Label(size_hint_y = None,markup = True) # markup for different color
        self.scroll_to_point = Label() # from a certain point the screen will scrool 

        self.layout.add_widget(self.chat_history)
        self.layout.add_widget(self.scroll_to_point)

    # 
    def update_chat_history(self,message):
        self.chat_history.text += '\n' + message
        self.layout.height = self.chat_history.texture_size[1] + 15
        self.chat_history.height = self.chat_history.texture_size[1]
        self.chat_history.text_size = (self.chat_history.width*0.98,None)
        self.scroll_to(self.scroll_to_point)

    def update_chat_history_layout(self, _=None):
        # Set layout height to whatever height of chat history text is + 15 pixels
        # (adds a bit of space at the bottom)
        # Set chat history label to whatever height of chat history text is
        # Set width of chat history text to 98 of the label width (adds small margins)
        self.layout.height = self.chat_history.texture_size[1] + 15
        self.chat_history.height = self.chat_history.texture_size[1]
        self.chat_history.text_size = (self.chat_history.width * 0.98, None)



# Main App class
class MainApp(App):
    def build(self):
        # first page for connection
        self.screen_manager = ScreenManager()
        self.connect_page = ConnectPage()
        screen = Screen(name = "Connect")  # create the screen
        screen.add_widget(self.connect_page)
        self.screen_manager.add_widget(screen)

        # Next Info Page
        self.info_page = InfoPage()
        screen = Screen(name = 'Info')
        screen.add_widget(self.info_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

    # Chat Page in a function so that when client is connected with the server then 
    # this function will call and show the page 
    def create_chat_page(self):
        self.chat_page = ChatPage()
        screen = Screen(name = "Chat")
        screen.add_widget(self.chat_page)
        self.screen_manager.add_widget(screen)

# To show the erros in InfoPgae and stay for 10 second then exit 
def show_error(message):
    chat_app.info_page.update_info(message)
    chat_app.screen_manager.current="Info"
    Clock.schedule_once(sys.exit, 10)


if __name__ == "__main__":
    chat_app = MainApp()
    chat_app.run()