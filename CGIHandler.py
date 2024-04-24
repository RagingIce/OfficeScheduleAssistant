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
    handler = ScheduleRequestHandler(self, self.__request, self.__response)
    handler.handle()

class CGIRequest:
  method = None
  content_type = None
  content_length = None
  path = None
  body = None
  query_string = None

  def __init__(self):
    self._parse()

  def _parse(self):
    self.method         = os.environ['REQUEST_METHOD']
    self.content_type   = os.environ['CONTENT_TYPE']
    self.content_length = os.environ['CONTENT_LENGTH']
    self.path           = os.environ['PATH_INFO']
    self.query_string   = os.environ['QUERY_STRING']
    self.body           = sys.stdin.read()

class CGIResponse:
  response_headers = dict()
  response_content = ""

  def send(self):
    (print (f'{k}: {v}') for k, v in self.response_headers)
    print ()
    print (self.response_content)

  def set_status(self, code=200):
    status_enum = HTTPStatus(status_code)
    set_header('Status', f'{status_enum.value} {status_enum.phrase}')

  def set_header(self, name, value):
    self.response_headers[name] = value

  def write(self, content):
    self.response_content = self.response_content + content + '\n'

try:
  if __name__ == "__main__":
    CGIHandler().handle_request()
except:
  sys.stderr.write("exception!!\n")