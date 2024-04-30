#!/usr/bin/env python3
import sys, os
from http import HTTPStatus
from ScheduleRequestHandler import ScheduleRequestHandler

class CGIHandler:
  __request = None
  __response = None

  def __init__(self):
    self.__request = CGIRequest()
    self.__response = CGIResponse()

  def handle_request(self):
    handler = ScheduleRequestHandler(self.__request, self.__response)
    handler.handle()
    self.__response.send()

class CGIRequest:
  method = None
  content_length = None
  path = None
  body = None
  query_string = None

  def __init__(self):
    self._parse()

  def _parse(self):
    self.method         = os.environ.get('REQUEST_METHOD')
    self.content_length = int(os.environ.get('CONTENT_LENGTH', '0'))
    self.path           = os.environ.get('REQUEST_URI')
    self.query_string   = os.environ.get('QUERY_STRING', '')
    self.api_key        = os.environ.get('HTTP_X_API_KEY', '').strip()

    if(self.content_length > 0):
      self.body         = sys.stdin.read(self.content_length)

class CGIResponse:
  response_headers = dict()
  response_content = ""

  def send(self):
    for k, v in self.response_headers.items():
      print(f'{k}: {v}')

    print ()
    print (self.response_content)

  def set_status(self, code=200):
    status_enum = HTTPStatus(code)
    self.set_header('Status', f'{status_enum.value} {status_enum.phrase}')

  def set_header(self, name, value):
    self.response_headers[name] = value

  def write(self, content):
    self.response_content = self.response_content + content + '\n'

if __name__ == "__main__":
  CGIHandler().handle_request()