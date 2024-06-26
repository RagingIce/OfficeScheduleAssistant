from urllib import parse
from datetime import datetime
from ScheduleAccessor import ScheduleAccessor
import re
import json
import logging
import traceback
import os, os.path

class ScheduleRequestHandler:
  __request = None
  __response = None

  def __init__(self, request, response):
    self.__request = request
    self.__response = response

  def handle(self):
    expected_api_key = self.__get_api_key_from_file()
    if expected_api_key != None and self.__request.api_key != expected_api_key:
      self._set_headers(401)
      return

    if self.__request.method == 'GET':
      self.do_GET()
    elif self.__request.method == 'POST':
      self.do_POST()
    else:
      self._set_headers(405)

  def _set_headers(self, response_code=200, content_type='text/html'):
    self.__response.set_status(response_code)
    self.__response.set_header('Content-Type', content_type)
    
    if(response_code >= 300):
      self.__response.write(f"HTTP Response {response_code}")

  def _get_form_data(self):
    content = self.__request.body
    return dict(parse.parse_qsl(content))

  def do_GET(self):
    try:
      pathMatch = re.fullmatch('\\/schedule\\/([a-zA-Z]+)\\/(\\d{4}-\\d{2}-\\d{2})', self.__request.path)

      if pathMatch:
        user = pathMatch.group(1)
        date = datetime.strptime(pathMatch.group(2), '%Y-%m-%d')
        booking_data = dict()
        
        if user == 'all':
          sched_users = ScheduleAccessor.get_all_users()
          for sched_user in sched_users:
            sched = ScheduleAccessor(sched_user)
            booking_data[sched_user] = sched.get_booking_info(date)

        else:
          sched = ScheduleAccessor(user)
          booking_data = sched.get_booking_info(date)

        self._set_headers(200, 'application/json');  
        self.__response.write(json.dumps(booking_data))
      else:
        self._set_headers(404)
    except Exception as e:
      logging.error(traceback.format_exc())
      self._set_headers(500)

  def do_POST(self):
    try:
      schedulePathMatch = re.fullmatch('\\/schedule', self.__request.path)
      vacationPathMatch = re.fullmatch('\\/vacation', self.__request.path)
      
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
  
  def __get_api_key_from_file(self):
    try:
      api_key_file_name = f'{os.path.dirname(os.path.realpath(__file__))}/apikey.txt'
      api_key_file = open(api_key_file_name, 'r')
      return api_key_file.read().strip()

    except:
      return None