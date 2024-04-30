from datetime import datetime
import json
import os, os.path
from os import listdir
from os.path import isfile, join
import traceback, logging

class ScheduleAccessor:
  __user = None
  __schedule = dict(Monday=None, Tuesday=None, Wednesday=None, Thursday=None, Friday=None)
  __vacations = []

  def __init__(self, user):
    self.__user = user

  def get_booking_info(self, booking_date):
    result = dict()
    self.__load()

    day_of_week = booking_date.strftime('%A')
    should_book_day_of_week = self.__schedule[day_of_week]

    if should_book_day_of_week:
      vacation_day = True in (booking_date >= vacation[0] and booking_date <= vacation[1] for vacation in self.__vacations)
      
      if not vacation_day:
        result['should_book'] = True
        result['preferred_desk'] = should_book_day_of_week

    return result

  def add_vacation(self, form_data):
    self.__load()
    #convert to a date to validate that the input is a date. It will get converted back to a string when dumped
    start_date = datetime.strptime(form_data['StartDate'].strip(), '%Y-%m-%d')
    end_date   = datetime.strptime(form_data['EndDate'].strip(), '%Y-%m-%d')
    
    self.__vacations.append((start_date, end_date))

    self.__persist()

  def update_schedule(self, form_data):
    self.__load()
    self.__schedule['Monday']    = form_data.get('Monday',    None)
    self.__schedule['Tuesday']   = form_data.get('Tuesday',   None)
    self.__schedule['Wednesday'] = form_data.get('Wednesday', None)
    self.__schedule['Thursday']  = form_data.get('Thursday',  None)
    self.__schedule['Friday']    = form_data.get('Friday',    None)

    self.__persist()

  @staticmethod
  def get_all_users():
    persistance_dir = f'{os.path.dirname(os.path.realpath(__file__))}/schedules'
    return [f.replace('_schedule.txt', '') for f in listdir(persistance_dir) if isfile(join(persistance_dir, f))]

  def __persist(self):
    f = self.__getFile('w+')
    f.write(self.__serialize())
    f.close()

  def __load(self):
    f = self.__getFile()
    if not f:
      return

    schedule_info = f.read()
    f.close()

    try:
      schedule_json = json.loads(schedule_info)
      self.__schedule = schedule_json['schedule']
      self.__vacations = list(map(lambda date_tuple: (datetime.strptime(date_tuple[0], '%Y-%m-%d %H:%M:%S'), datetime.strptime(date_tuple[1], '%Y-%m-%d %H:%M:%S')), schedule_json['vacations']))
    
    except:
      return

  def __getFile(self, mode='r'):
    try:
      persistance_dir = f'{os.path.dirname(os.path.realpath(__file__))}/schedules'
      return open(f'{persistance_dir}/{self.__user}_schedule.txt', mode)
    
    except:
      logging.error(traceback.format_exc())
      return None

  def __serialize(self):
    persistance_obj = dict(schedule=self.__schedule, vacations=self.__vacations)
    return json.dumps(persistance_obj, default=str)  
