import datetime
import itertools
import src
import json
from discord import Embed, Webhook, RequestsWebhookAdapter
import os.path
from os import environ

# CONFIG:
sessions = [
    (datetime.time(hour=9, minute=0), datetime.timedelta(hours=3)),
    (datetime.time(hour=12, minute=0), datetime.timedelta(hours=3)),
    (datetime.time(hour=15, minute=0), datetime.timedelta(hours=3)),
]
webhook_url = "https://discord.com/api/webhooks/910583855545733120/GRPETupsGBYJyx4XOsYXebbZuIw062vOGZwWoKlY5S5bbYfDHI7jn0lkNMQ_Ib-uNf8q"



credential_pool = [(os.environ.get("CRED_1_GUID"), os.environ.get("CRED_1_PASS")), (os.environ.get("CRED_2_GUID"), os.environ.get("CRED_2_PASS"))]

client_pool = list()
count = 1
for guid, password in credential_pool:
    try:
        new_client = src.RoomClient()
        new_client._authorize(guid, password)
        client_pool.append(new_client)
    except src.InvalidLoginException as e:
        print(f"{e.guid} login failed!")
        e.variable_name = f"CRED_{count}_*"
        e._push_log()
    count += 1

if len(client_pool) == 0:
    print("No valid clients available!")
    print("PANIC!")
    exit()

    # bookings = client_pool[0].get_bookings()
    # print(bookings)
    # for booking in bookings:
    #     client_pool[0].delete_booking(booking[0])
    #
    # bookings = client_pool[1].get_bookings()
    # print(bookings)
    # for booking in bookings:
    #     client_pool[1].delete_booking(booking[0])
    #
    # exit()

with open("room_priorities.txt", "r") as room_priorities_file:
    priorities = [val.strip() for val in room_priorities_file.readlines()]

with open("blacklist.txt", "r") as blacklist_file:
    blacklist = [val.strip() for val in blacklist_file.readlines()]


bookable_rooms = client_pool[0].get_rooms()
final_priorities = list()

for room_id in priorities:
    if room_id in bookable_rooms.keys():
        if room_id not in blacklist:
            final_priorities.append(room_id)

for room_id in bookable_rooms.keys():
    if room_id not in final_priorities:
        if room_id not in blacklist:
            final_priorities.append(room_id)

booked = list()
round_robin = itertools.cycle(client_pool)
last = None
for session, session_length in sessions:
    new_client: src.RoomClient = next(round_robin)
    start = datetime.datetime.combine((datetime.date.today()+datetime.timedelta(days=7)), session)
    _booked = False
    _priority_track = 0
    while not _booked:
        if not (_priority_track >= len(final_priorities)):
            try:
                if last is None:
                    room_id = final_priorities[_priority_track]
                else:
                    room_id = last
                new_client.attempt_book_room(
                    room_id=room_id,
                    start=start,
                    length=session_length
                )
                _booked = True
                print(f"Booked room: {bookable_rooms[room_id]}")
                print(f"session: {session}")
                last = room_id
                booked.append(room_id)
            except src.RoomNotBookableException:
                print(f"Couldn't book room: {bookable_rooms[room_id]}")
                print(f"session: {session}")
                if last is not None:
                    last = None
                _priority_track += 1
                _booked = False
            except src.FailedRequestException as e:
                e._push_log()
        else:
            booked.append(None)
            _booked = True

data = list()

for index, room_id in enumerate(booked):
    if room_id is None:
        data.append({
            "room_id": None,
            "room_name": None,
            "session_start": datetime.datetime.combine((datetime.date.today()+datetime.timedelta(days=7)),(sessions[index][0])),
            "session_end":  datetime.datetime.combine((datetime.date.today()+datetime.timedelta(days=7)), (sessions[index][0]))+sessions[index][1]
        })
    else:
        data.append({
            "room_id": room_id,
            "room_name": bookable_rooms[room_id],
            "session_start": datetime.datetime.combine((datetime.date.today()+datetime.timedelta(days=7)),(sessions[index][0])).strftime("%H:%M"),
            "session_end":  (datetime.datetime.combine((datetime.date.today()+datetime.timedelta(days=7)), (sessions[index][0]))+sessions[index][1]).strftime("%H:%M")
        })

today_int = datetime.date.today().weekday()
if not os.path.isfile(f"dat/rooms_{today_int}.json"):
    open(f"dat/rooms_{today_int}.json", "w").close()
with open(f"dat/rooms_{today_int}.json", "r+") as file:
    try:
        todays_data = json.loads(file.read())["data"]
        e = Embed(title='Room Bookings for Today')
        for booking in todays_data:
            e.add_field(
                name=f"{booking.get('session_start')} - {booking.get('session_end')}",
                value=booking.get('room_name'),
                inline=False
            )
    except json.decoder.JSONDecodeError:
        e = Embed(title='No bookings for today!')

    webhook = Webhook.from_url(webhook_url, adapter=RequestsWebhookAdapter())
    webhook.send(embed=e)

    file.seek(0)
    file.write(json.dumps({"data":data}, default=str))
    file.truncate()