from st2reactor.sensor.base import Sensor

import BaseHTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler

import urllib
import json
import traceback

class AlertmanagerSensor(Sensor):
  def __init__(self, sensor_service, config):
    super(AlertmanagerSensor, self).__init__(sensor_service=sensor_service, config=config)
    self._logger = self.sensor_service.get_logger(name=self.__class__.__name__)
    self._host = '0.0.0.0'
    self._port = 12345

  def _create_handler_class(sensor):
    class AlertmanagerHandler(BaseHTTPRequestHandler):
      def __init__(self, *args, **kwargs):
        self._sensor = sensor
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

      def do_POST(self):
        length = int(self.headers.getheader('content-length', 0))
        s = self.rfile.read(length)
        try:
          d = json.loads(s)
          for alert in d['alerts']:
            labels = alerts['labels']
            trigger = 'prometheus.alert'
            payload = {
              'alert_name': labels['alertname'],
              'host': labels['instance']
            }
            self._sensor.sensor_service.dispatch(trigger=trigger, payload=payload)

          self.send_response(200)
          self.send_header("Content-type", "application/json")
          self.end_headers()
        except Exception as e:
          self._sensor._logger.error(e)
          self._sensor._logger.error(traceback.format_exc())
          self.send_response(400)
    return AlertmanagerHandler

  def setup(self):
    handler_class = self._create_handler_class()
    self._http_server = BaseHTTPServer.HTTPServer((self._host, self._port), handler_class)

  def run(self):
    self._http_server.serve_forever()

  def cleanup(self):
    self._http_server.server_close()

  def add_trigger(self, trigger):
    pass

  def update_trigger(self, trigger):
    pass

  def remove_trigger(self, trigger):
    pass
