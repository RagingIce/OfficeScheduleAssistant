#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
from datetime import datetime
from ScheduleAccessor import ScheduleAccessor
import re
import json
import logging
import traceback
import ssl

class SchedulerRequesetHandler(BaseHTTPRequestHandler):
  def _set_headers(self, response_code=200, content_type='text/html'):
    self.send_response(response_code)
    self.send_header('Content-type', content_type)
    self.end_headers()

    if response_code >= 300:
      self.wfile.write(bytes(f"HTTP Response {response_code}","utf-8"))

  def _get_form_data(self):
    length = int(self.headers.get('content-length'))
    content = self.rfile.read(length)
    return dict(parse.parse_qsl(str(content,'UTF-8')))

  def do_GET(self):
    try:
      pathMatch = re.fullmatch('\\/schedule\\/([a-zA-Z]+)\\/(\\d{4}-\\d{2}-\\d{2})', self.path)
      if pathMatch:
        user = pathMatch.group(1)
        date = datetime.strptime(pathMatch.group(2), '%Y-%m-%d')
        
        sched = ScheduleAccessor(user)
        booking_data = sched.get_booking_info(date)

        self._set_headers(200, 'application/json');  
        self.wfile.write(json.dumps(booking_data).encode(encoding='utf_8'))
      else:
        self._set_headers(404)
    except Exception as e:
      logging.error(traceback.format_exc())
      self._set_headers(500)

  def do_POST(self):
    try:
      schedulePathMatch = re.fullmatch('\\/schedule', self.path)
      vacationPathMatch = re.fullmatch('\\/vacation', self.path)
      
      if schedulePathMatch or vacationPathMatch:
        form_data = self._get_form_data()

        if "user" in form_data:
          sched = ScheduleAccessor(form_data['user'])

          if schedulePathMatch:
            sched.update_schedule(form_data)

          elif vacationPathMatch:
            sched.add_vacation(form_data)  

          self._set_headers(200)

        else:
          self._set_headers(400)


      else:
        self._set_headers(404)
    except Exception as e:
      logging.error(traceback.format_exc())
      self._set_headers(500)

def run(server_class=HTTPServer, handler_class=SchedulerRequesetHandler, port=8080, host='localhost', cert_path='./server.pem', key_path='./key.pem'):
  server_address = (host, port)
  httpd = server_class(server_address, handler_class)
  if port == 4443:
    context = ssl.create_default_context()
    httpd.socket = context.wrap_socket(httpd.socket, keyfile=key_path, certfile=cert_path, server_side=True)
  
  print('Starting httpd...')
  httpd.serve_forever()

if __name__ == "__main__":
  from sys import argv

  if len(argv) == 5:
    run(port=int(argv[1]), host=argv[2], cert_path=argv[3], key_path=argv[4])
  else:
    run()