import datetime
from random import randint
from math import ceil
from requests import Session, Response
from uuid import uuid4
from typing import List
ROOT_URL = "https://frontdoor.spa.gla.ac.uk/timetable"


class InvalidLoginException(Exception):
    def __init__(self, guid: str, variable_name: str, response: Response):
        self.guid = guid
        self.variable_name = variable_name
        self.response = response

    def _push_log(self):
        with open(f"error_logs/FAILED_LOGIN_{self.guid}_{str(uuid4())[0:7]}", "w") as failed_login_log_file:
            failed_login_log_file.writelines([
                f"Failed login for GUID: {self.guid}; Pass stored in {self.variable_name}\n",
                f"Status Code: {self.response.status_code}\n",
                f"Raw Response: {self.response.content}"
            ])


class FailedRequestException(Exception):
    def __init__(self, guid: str, variable_name: str, response: Response):
        self.guid = guid
        self.variable_name = variable_name
        self.response = response

    def _push_log(self):
        with open(f"error_logs/FAILED_REQUEST_{self.guid}_{str(uuid4())[0:7]}", "w") as failed_login_log_file:
            failed_login_log_file.writelines([
                f"Failed request for GUID: {self.guid}; Pass stored in {self.variable_name}\n",
                f"URL: {self.response.url}\n",
                f"Status Code: {self.response.status_code}\n",
                f"Raw Response: {self.response.content}"
            ])


class RoomNotBookableException(Exception):
    pass


def format_date(date: datetime.datetime) -> str:
    return date.strftime("%Y-%m-%d %H:%M")


def generate_date_string(start: datetime.datetime, length: datetime.timedelta) -> List[str]:
    return [
        format_date(date)
        for date in [
            start+datetime.timedelta(minutes=mins)
            for mins in [
                30*i
                for i in range(0, ceil((length.seconds//60) / 30))
            ]
        ]
    ]

class RoomClient:
    def __init__(self):
        self._authorized = False
        self.username = None
        self.session = Session()

    def _authorize(self, username: str, password: str):
        self.username = username
        resp = self.session.post(
            url=f"{ROOT_URL}/login",
            json={
                'guid': username,
                'password': password,
                'rememberMe': True
            }
        )
        if resp.status_code != 200:
            raise InvalidLoginException(username, f"FOO_VAR", resp)  # TODO: Fix this.
        else:
            self._authorized = True

    def get_rooms(self):
        resp = self.session.get(f'{ROOT_URL}/booking/locations')
        if resp.status_code != 200:
            if self._authorized:
                raise FailedRequestException(self.username, f"FOO_VAR", resp)
            else:
                print("You aren't _authorized! This shouldn't happen! PANIC!")
                exit()
        else:
            return {
                room_id: room_name
                for room_id, room_name in resp.json()
            }

    def attempt_book_room(self, room_id, start: datetime.datetime, length: datetime.timedelta):
        resp = self.session.post(
            f"{ROOT_URL}/bookingv2",
            json={
                "attendees": randint(0, 6),  # <- Cloaking to make requests less repeated.
                "dates": generate_date_string(start, length),
                "locationId": room_id
            }
        )
        if resp.status_code != 200:
            try:
                data = resp.json()
            except:
                if not self._authorized:
                    print("You aren't _authorized! This shouldn't happen! PANIC!")
                    exit()

                raise FailedRequestException(self.username, f"FOO_VAR", resp)
            print(resp.content)
            if data.get("error") is not None:
                raise RoomNotBookableException

    def get_bookings(self):
        resp = self.session.get(
            f"{ROOT_URL}/bookingv2/bookings"
        )
        if resp.status_code != 200:
            raise FailedRequestException(self.username, f"FOO-VAR", resp)
        else:
            return resp.json()

    def delete_booking(self, booking_id: int):
        resp = self.session.delete(
            f"{ROOT_URL}/booking",
            params={
                "bookingId": booking_id
            }
        )
        if resp.status_code != 200:
            raise FailedRequestException(self.username, f"FOO-VAR", resp)