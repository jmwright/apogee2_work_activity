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

from functools import partial
from kivy.app import App
from kivy.clock import Clock
from kivy.modules import keybinding
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty, ListProperty
from kivy.garden.graph import Graph, MeshLinePlot


class ShepardClientGUI(Widget):
    thrust = NumericProperty(0)
    temp = NumericProperty(0)
    start_btn = ObjectProperty(None)
    armed_btn = ObjectProperty(None)
    thrust_lbl = ObjectProperty(None)
    status_lbl = ObjectProperty(None)


    def connect_to_server(self):
        reactor.connectTCP('localhost', 9999, MyClientFactory(self))

    def on_connection(self, connection):
        self.print_message("Connected to server")
        self.connection = connection

        self.start_btn.bind(on_press=self.btn_callback)
        self.set_armed(True)
        self.set_cont(True)

    def send_message(self, *args):
        if self.connection:
            self.connection.write('R')

            self.set_running(True)

    def print_message(self, msg):
        self.status_lbl.text = msg

    def handle_data(self, data):
        self.thrust = round(float(data.split(',')[1]), 1)

    def btn_callback(instance, value):
        instance.send_message()
        instance.button_color_green(instance.armed_btn)

    def button_color_green(self, button):
        button.background_color = [0, 204, 0, 255]

    def set_armed(instance, armed):
        """
        Set the armed button state
        :param OK: true or false
        :return: None
        """
        if armed is False:
            # Red
            instance.armed_btn.background_color = [255, 0, 0, 255]
        elif armed is True:
            # Green
            instance.armed_btn.background_color = [0, 204, 0, 255]
        else:
            # Invalid input
            pass

    def set_cont(instance, cont):
        """
        Set the continuity button state
        :param OK: true or false
        :return: None
        """
        if cont is False:
            # Red
            instance.cont_btn.background_color = [255, 0, 0, 255]
        elif cont is True:
            # Green
            instance.cont_btn.background_color = [0, 204, 0, 255]
        else:
            # Invalid input
            pass

    def set_running(instance, tgl):
        """
        Set the continuity button state
        :param OK: true or false
        :return: None
        """
        if tgl is False:
            # Red
            instance.tgl_btn.background_color = [255, 0, 0, 255]
        elif tgl is True:
            # Green
            instance.tgl_btn.background_color = [0, 204, 0, 255]
        else:
            # Invalid input
            pass

        Clock.schedule_once(instance.set_not_running, 1.9)

    def set_not_running(self, instance):
        # Red
        self.tgl_btn.background_color = [255, 0, 0, 255]


class ShepardClientApp(App):
    connection = None

    def build(self):
        gui = ShepardClientGUI()
        gui.connect_to_server()
        return gui

if __name__ == '__main__':
    ShepardClientApp().run()