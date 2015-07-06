from kivy.support import install_twisted_reactor
install_twisted_reactor()

from twisted.internet import reactor, protocol


class MyClient(protocol.Protocol):
    def connectionMade(self):
        self.factory.app.on_connection(self.transport)

    def dataReceived(self, data):
        #self.factory.app.print_message(data)
        self.factory.app.handle_data(data)


class MyClientFactory(protocol.ClientFactory):
    protocol = MyClient

    def __init__(self, app):
        self.app = app

    def clientConnectionLost(self, conn, reason):
        self.app.print_message("Connection Lost")

    def clientConnectionFailed(self, conn, reason):
        self.app.print_message("Connection Failed")

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout


class ShepardClientApp(App):
    connection = None

    def build(self):
        root = self.setup_gui()
        self.connect_to_server()
        return root

    def setup_gui(self):
        self.label = Label(text='Connecting...\n', size_hint_y=0.1)
        self.thrust_lbl = Label(text='N/A', size_hint_x=0.333)
        self.button = Button(text='Start', font_size=14)
        self.button.bind(on_press=self.btn_callback)
        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(self.thrust_lbl)
        self.layout.add_widget(self.button)
        self.layout.add_widget(self.label)
        return self.layout

    def connect_to_server(self):
        reactor.connectTCP('localhost', 9999, MyClientFactory(self))

    def on_connection(self, connection):
        self.print_message("Connected succesfully!")
        self.connection = connection

    def send_message(self, *args):
        if self.connection:
            self.connection.write('R')

    def print_message(self, msg):
        self.label.text += msg + '\n'

    def handle_data(self, data):
        self.thrust_lbl.text = "Thrust: " + str(round(float(data.split(',')[1]), 3))

    def btn_callback(instance, value):
        instance.send_message()

if __name__ == '__main__':
    ShepardClientApp().run()