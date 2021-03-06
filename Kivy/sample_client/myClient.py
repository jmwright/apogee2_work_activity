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
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty
from kivy.garden.graph import Graph, MeshLinePlot


class ShepardClientGUI(Widget):
    thrust = NumericProperty(0)
    start_btn = ObjectProperty(None)
    thrust_lbl = ObjectProperty(None)
    status_lbl = ObjectProperty(None)

    def connect_to_server(self):
        reactor.connectTCP('localhost', 9999, MyClientFactory(self))

    def on_connection(self, connection):
        self.print_message("Connected to server")
        self.connection = connection

        self.start_btn.bind(on_press=self.btn_callback)

    def send_message(self, *args):
        if self.connection:
            self.connection.write('R')

    def print_message(self, msg):
        self.status_lbl.text = msg

    def handle_data(self, data):
        self.thrust = round(float(data.split(',')[1]), 3)

    def btn_callback(instance, value):
        instance.send_message()

class ShepardClientApp(App):
    connection = None

    def build(self):
        gui = ShepardClientGUI()
        gui.connect_to_server()
        return gui

if __name__ == '__main__':
    ShepardClientApp().run()