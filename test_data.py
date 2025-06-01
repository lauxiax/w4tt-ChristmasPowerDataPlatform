# test_data.py
# Este archivo contiene datos de muestra para probar la API de asignación de tareas

# Datos de tareas de Planner
TASKS_SAMPLE = [
    {
        "@odata.etag": "W/\"JzEtVGFzayAgQEBAQEBAQEBAQEBAQEBASCc=\"",
        "planId": "q9jw7nttcUavm52Yr8JaEpgAA_Sa",
        "title": "TASK1",
        "orderHint": "8584528240109821697P5",
        "assigneePriority": "8584528239509286797",
        "percentComplete": 0,
        "createdDateTime": "2025-06-01T13:02:14.5489132Z",
        "dueDateTime": "2025-06-05T10:00:00Z",
        "hasDescription": False,
        "previewType": "automatic",
        "referenceCount": 0,
        "checklistItemCount": 0,
        "activeChecklistItemCount": 0,
        "priority": 3,
        "id": "3gU3WcXciE-AvwOaAtQx2pgAKI9i",
        "createdBy": {
            "user": {
                "id": "fca475e9-5d73-4d31-b0b3-f2f13c051810"
            },
            "application": {
                "displayName": None,
                "id": "75f31797-37c9-498e-8dc9-53c16a36afca"
            }
        },
        "appliedCategories": {},
        "assignments": {
            "fca475e9-5d73-4d31-b0b3-f2f13c051810": {
                "@odata.type": "#microsoft.graph.plannerAssignment",
                "assignedDateTime": "2025-06-01T13:02:14.5488551Z",
                "orderHint": "8584528240109820510P<",
                "assignedBy": {
                    "user": {
                        "displayName": None,
                        "id": "fca475e9-5d73-4d31-b0b3-f2f13c051810"
                    },
                    "application": {
                        "displayName": None,
                        "id": "75f31797-37c9-498e-8dc9-53c16a36afca"
                    }
                }
            }
        }
    },
    {
        "@odata.etag": "W/\"JzEtVGFzayAgQEBAQEBAQEBAQEBAQEBARCc=\"",
        "planId": "q9jw7nttcUavm52Yr8JaEpgAA_Sa",
        "title": "TASK3",
        "orderHint": "8584528239852813753PI",
        "assigneePriority": "[,",
        "percentComplete": 0,
        "createdDateTime": "2025-06-01T13:02:40.2301284Z",
        "dueDateTime": "2025-06-16T10:00:00Z",
        "hasDescription": False,
        "previewType": "automatic",
        "referenceCount": 0,
        "checklistItemCount": 0,
        "activeChecklistItemCount": 0,
        "priority": 5,
        "id": "ZQxGGmxK0kyFzQ_QTIJ-EpgAI6sF",
        "createdBy": {
            "user": {
                "id": "fca475e9-5d73-4d31-b0b3-f2f13c051810"
            },
            "application": {
                "displayName": None,
                "id": "75f31797-37c9-498e-8dc9-53c16a36afca"
            }
        },
        "appliedCategories": {},
        "assignments": {
            "fca475e9-5d73-4d31-b0b3-f2f13c051810": {
                "@odata.type": "#microsoft.graph.plannerAssignment",
                "assignedDateTime": "2025-06-01T13:02:40.2300902Z",
                "orderHint": "8584528239852813008PT",
                "assignedBy": {
                    "user": {
                        "displayName": None,
                        "id": "fca475e9-5d73-4d31-b0b3-f2f13c051810"
                    },
                    "application": {
                        "displayName": None,
                        "id": "75f31797-37c9-498e-8dc9-53c16a36afca"
                    }
                }
            }
        }
    },
    {
        "@odata.etag": "W/\"JzEtVGFzayAgQEBAQEBAQEBAQEBAQEBASCc=\"",
        "planId": "q9jw7nttcUavm52Yr8JaEpgAA_Sa",
        "title": "TASK2",
        "orderHint": "8584528240000422909Pe",
        "assigneePriority": "[t",
        "percentComplete": 50,
        "createdDateTime": "2025-06-01T13:02:25.590458Z",
        "dueDateTime": "2025-06-02T10:00:00Z",
        "hasDescription": False,
        "previewType": "automatic",
        "referenceCount": 0,
        "checklistItemCount": 0,
        "activeChecklistItemCount": 0,
        "priority": 1,
        "id": "ml5lwAXzwkKez0ozrJg8JJgACZK9",
        "createdBy": {
            "user": {
                "id": "fca475e9-5d73-4d31-b0b3-f2f13c051810"
            },
            "application": {
                "displayName": None,
                "id": "75f31797-37c9-498e-8dc9-53c16a36afca"
            }
        },
        "appliedCategories": {},
        "assignments": {
            "fca475e9-5d73-4d31-b0b3-f2f13c051810": {
                "@odata.type": "#microsoft.graph.plannerAssignment",
                "assignedDateTime": "2025-06-01T13:02:25.5904118Z",
                "orderHint": "8584528240000422228P,",
                "assignedBy": {
                    "user": {
                        "displayName": None,
                        "id": "fca475e9-5d73-4d31-b0b3-f2f13c051810"
                    },
                    "application": {
                        "displayName": None,
                        "id": "75f31797-37c9-498e-8dc9-53c16a36afca"
                    }
                }
            }
        }
    }
]

# Datos de slots de agenda de Outlook
SLOTS_SAMPLE = [
    {
        "subject": "xxzcxzcxzcxzc",
        "start": "2025-06-02T10:30:00.0000000",
        "end": "2025-06-02T11:00:00.0000000",
        "startWithTimeZone": "2025-06-02T10:30:00+00:00",
        "endWithTimeZone": "2025-06-02T11:00:00+00:00",
        "body": "",
        "isHtml": True,
        "responseType": "organizer",
        "responseTime": "0001-01-01T00:00:00+00:00",
        "id": "AAMkADZhNTIzNzJjLTNjNWEtNDExMy1iNmZhLWFlYzkyZmUxYmZhYgBGAAAAAAA9y4rVoTitQ41KBi-XzhbJBwB3-TbRDAeLQLdR49f04FklAAAAAAENAAB3-TbRDAeLQLdR49f04FklAABxalCKAAA=",
        "createdDateTime": "2025-06-01T13:06:38.6773467+00:00",
        "lastModifiedDateTime": "2025-06-01T13:06:39.7204514+00:00",
        "organizer": "lauritxi@powerbicio.onmicrosoft.com",
        "timeZone": "UTC",
        "iCalUId": "040000008200E00074C5B7101A82E00800000000A9C1B302F6D2DB01000000000000000010000000B14841EB57F94749890587F82CB2CB11",
        "categories": [],
        "webLink": "https://outlook.office365.com/owa/?itemid=AAMkADZhNTIzNzJjLTNjNWEtNDExMy1iNmZhLWFlYzkyZmUxYmZhYgBGAAAAAAA9y4rVoTitQ41KBi%2FXzhbJBwB3%2FTbRDAeLQLdR49f04FklAAAAAAENAAB3%2FTbRDAeLQLdR49f04FklAABxalCKAAA%3D&exvsurl=1&path=/calendar/item",
        "requiredAttendees": "",
        "optionalAttendees": "",
        "resourceAttendees": "",
        "location": "",
        "importance": "normal",
        "isAllDay": False,
        "recurrence": "none",
        "reminderMinutesBeforeStart": 15,
        "isReminderOn": True,
        "showAs": "busy",
        "responseRequested": True,
        "sensitivity": "normal"
    },
    {
        "subject": "xzczxc",
        "start": "2025-06-02T13:00:00.0000000",
        "end": "2025-06-02T13:30:00.0000000",
        "startWithTimeZone": "2025-06-02T13:00:00+00:00",
        "endWithTimeZone": "2025-06-02T13:30:00+00:00",
        "body": "",
        "isHtml": True,
        "responseType": "organizer",
        "responseTime": "0001-01-01T00:00:00+00:00",
        "id": "AAMkADZhNTIzNzJjLTNjNWEtNDExMy1iNmZhLWFlYzkyZmUxYmZhYgBGAAAAAAA9y4rVoTitQ41KBi-XzhbJBwB3-TbRDAeLQLdR49f04FklAAAAAAENAAB3-TbRDAeLQLdR49f04FklAABxalCOAAA=",
        "createdDateTime": "2025-06-01T13:06:58.8078431+00:00",
        "lastModifiedDateTime": "2025-06-01T13:06:59.0338598+00:00",
        "organizer": "lauritxi@powerbicio.onmicrosoft.com",
        "timeZone": "UTC",
        "iCalUId": "040000008200E00074C5B7101A82E008000000005FC6B20EF6D2DB0100000000000000001000000061DBAB69602D5D44BE36710CC80DCCF1",
        "categories": [],
        "webLink": "https://outlook.office365.com/owa/?itemid=AAMkADZhNTIzNzJjLTNjNWEtNDExMy1iNmZhLWFlYzkyZmUxYmZhYgBGAAAAAAA9y4rVoTitQ41KBi%2FXzhbJBwB3%2FTbRDAeLQLdR49f04FklAAAAAAENAAB3%2FTbRDAeLQLdR49f04FklAABxalCOAAA%3D&exvsurl=1&path=/calendar/item",
        "requiredAttendees": "",
        "optionalAttendees": "",
        "resourceAttendees": "",
        "location": "",
        "importance": "normal",
        "isAllDay": False,
        "recurrence": "none",
        "reminderMinutesBeforeStart": 15,
        "isReminderOn": True,
        "showAs": "busy",
        "responseRequested": True,
        "sensitivity": "normal"
    },
    {
        "subject": "dczczcxxzcxzcxzc",
        "start": "2025-06-02T16:00:00.0000000",
        "end": "2025-06-02T16:30:00.0000000",
        "startWithTimeZone": "2025-06-02T16:00:00+00:00",
        "endWithTimeZone": "2025-06-02T16:30:00+00:00",
        "body": "",
        "isHtml": True,
        "responseType": "organizer",
        "responseTime": "0001-01-01T00:00:00+00:00",
        "id": "AAMkADZhNTIzNzJjLTNjNWEtNDExMy1iNmZhLWFlYzkyZmUxYmZhYgBGAAAAAAA9y4rVoTitQ41KBi-XzhbJBwB3-TbRDAeLQLdR49f04FklAAAAAAENAAB3-TbRDAeLQLdR49f04FklAABxalCPAAA=",
        "createdDateTime": "2025-06-01T13:07:02.709483+00:00",
        "lastModifiedDateTime": "2025-06-01T13:07:03.4080054+00:00",
        "organizer": "lauritxi@powerbicio.onmicrosoft.com",
        "timeZone": "UTC",
        "iCalUId": "040000008200E00074C5B7101A82E0080000000095DB0611F6D2DB01000000000000000010000000EE8BCC4EF3D9D64B81BC808083DFD3A6",
        "categories": [],
        "webLink": "https://outlook.office365.com/owa/?itemid=AAMkADZhNTIzNzJjLTNjNWEtNDExMy1iNmZhLWFlYzkyZmUxYmZhYgBGAAAAAAA9y4rVoTitQ41KBi%2FXzhbJBwB3%2FTbRDAeLQLdR49f04FklAAAAAAENAAB3%2FTbRDAeLQLdR49f04FklAABxalCPAAA%3D&exvsurl=1&path=/calendar/item",
        "requiredAttendees": "",
        "optionalAttendees": "",
        "resourceAttendees": "",
        "location": "",
        "importance": "normal",
        "isAllDay": False,
        "recurrence": "none",
        "reminderMinutesBeforeStart": 15,
        "isReminderOn": True,
        "showAs": "busy",
        "responseRequested": True,
        "sensitivity": "normal"
    },
    {
        "subject": "x",
        "start": "2025-06-03T11:30:00.0000000",
        "end": "2025-06-03T13:30:00.0000000",
        "startWithTimeZone": "2025-06-03T11:30:00+00:00",
        "endWithTimeZone": "2025-06-03T13:30:00+00:00",
        "body": "",
        "isHtml": True,
        "responseType": "organizer",
        "responseTime": "0001-01-01T00:00:00+00:00",
        "id": "AAMkADZhNTIzNzJjLTNjNWEtNDExMy1iNmZhLWFlYzkyZmUxYmZhYgBGAAAAAAA9y4rVoTitQ41KBi-XzhbJBwB3-TbRDAeLQLdR49f04FklAAAAAAENAAB3-TbRDAeLQLdR49f04FklAABxalCLAAA=",
        "createdDateTime": "2025-06-01T13:06:45.288281+00:00",
        "lastModifiedDateTime": "2025-06-01T13:06:46.073114+00:00",
        "organizer": "lauritxi@powerbicio.onmicrosoft.com",
        "timeZone": "UTC",
        "iCalUId": "040000008200E00074C5B7101A82E008000000001154A406F6D2DB01000000000000000010000000C2E523447940134B9615F539837D59DF",
        "categories": [],
        "webLink": "https://outlook.office365.com/owa/?itemid=AAMkADZhNTIzNzJjLTNjNWEtNDExMy1iNmZhLWFlYzkyZmUxYmZhYgBGAAAAAAA9y4rVoTitQ41KBi%2FXzhbJBwB3%2FTbRDAeLQLdR49f04FklAAAAAAENAAB3%2FTbRDAeLQLdR49f04FklAABxalCLAAA%3D&exvsurl=1&path=/calendar/item",
        "requiredAttendees": "",
        "optionalAttendees": "",
        "resourceAttendees": "",
        "location": "",
        "importance": "normal",
        "isAllDay": False,
        "recurrence": "none",
        "reminderMinutesBeforeStart": 15,
        "isReminderOn": True,
        "showAs": "busy",
        "responseRequested": True,
        "sensitivity": "normal"
    },
    {
        "subject": "xccccc",
        "start": "2025-06-04T08:30:00.0000000",
        "end": "2025-06-04T09:00:00.0000000",
        "startWithTimeZone": "2025-06-04T08:30:00+00:00",
        "endWithTimeZone": "2025-06-04T09:00:00+00:00",
        "body": "",
        "isHtml": True,
        "responseType": "organizer",
        "responseTime": "0001-01-01T00:00:00+00:00",
        "id": "AAMkADZhNTIzNzJjLTNjNWEtNDExMy1iNmZhLWFlYzkyZmUxYmZhYgBGAAAAAAA9y4rVoTitQ41KBi-XzhbJBwB3-TbRDAeLQLdR49f04FklAAAAAAENAAB3-TbRDAeLQLdR49f04FklAABxalCMAAA=",
        "createdDateTime": "2025-06-01T13:06:50.0051141+00:00",
        "lastModifiedDateTime": "2025-06-01T13:06:50.3767994+00:00",
        "organizer": "lauritxi@powerbicio.onmicrosoft.com",
        "timeZone": "UTC",
        "iCalUId": "040000008200E00074C5B7101A82E008000000007E657409F6D2DB0100000000000000001000000062B6E1E2DF50B84DACB93FF636DCB82B",
        "categories": [],
        "webLink": "https://outlook.office365.com/owa/?itemid=AAMkADZhNTIzNzJjLTNjNWEtNDExMy1iNmZhLWFlYzkyZmUxYmZhYgBGAAAAAAA9y4rVoTitQ41KBi%2FXzhbJBwB3%2FTbRDAeLQLdR49f04FklAAAAAAENAAB3%2FTbRDAeLQLdR49f04FklAABxalCMAAA%3D&exvsurl=1&path=/calendar/item",
        "requiredAttendees": "",
        "optionalAttendees": "",
        "resourceAttendees": "",
        "location": "",
        "importance": "normal",
        "isAllDay": False,
        "recurrence": "none",
        "reminderMinutesBeforeStart": 15,
        "isReminderOn": True,
        "showAs": "busy",
        "responseRequested": True,
        "sensitivity": "normal"
    },
    {
        "subject": "cccc",
        "start": "2025-06-04T10:00:00.0000000",
        "end": "2025-06-04T12:00:00.0000000",
        "startWithTimeZone": "2025-06-04T10:00:00+00:00",
        "endWithTimeZone": "2025-06-04T12:00:00+00:00",
        "body": "",
        "isHtml": True,
        "responseType": "organizer",
        "responseTime": "0001-01-01T00:00:00+00:00",
        "id": "AAMkADZhNTIzNzJjLTNjNWEtNDExMy1iNmZhLWFlYzkyZmUxYmZhYgBGAAAAAAA9y4rVoTitQ41KBi-XzhbJBwB3-TbRDAeLQLdR49f04FklAAAAAAENAAB3-TbRDAeLQLdR49f04FklAABxalCNAAA=",
        "createdDateTime": "2025-06-01T13:06:55.205622+00:00",
        "lastModifiedDateTime": "2025-06-01T13:06:55.7420329+00:00",
        "organizer": "lauritxi@powerbicio.onmicrosoft.com",
        "timeZone": "UTC",
        "iCalUId": "040000008200E00074C5B7101A82E0080000000020618E0CF6D2DB01000000000000000010000000B3B4AC0267F35440A33925787634B097",
        "categories": [],
        "webLink": "https://outlook.office365.com/owa/?itemid=AAMkADZhNTIzNzJjLTNjNWEtNDExMy1iNmZhLWFlYzkyZmUxYmZhYgBGAAAAAAA9y4rVoTitQ41KBi%2FXzhbJBwB3%2FTbRDAeLQLdR49f04FklAAAAAAENAAB3%2FTbRDAeLQLdR49f04FklAABxalCNAAA%3D&exvsurl=1&path=/calendar/item",
        "requiredAttendees": "",
        "optionalAttendees": "",
        "resourceAttendees": "",
        "location": "",
        "importance": "normal",
        "isAllDay": False,
        "recurrence": "none",
        "reminderMinutesBeforeStart": 15,
        "isReminderOn": True,
        "showAs": "busy",
        "responseRequested": True,
        "sensitivity": "normal"
    }
]

# Función para crear el JSON para enviar a la API
def get_request_payload():
    import json
    payload = {
        "tasks": TASKS_SAMPLE,
        "slots": SLOTS_SAMPLE
    }
    return json.dumps(payload, indent=4)

# Ejemplo de cómo ejecutar una solicitud a la API con estos datos
def example_api_call():
    import requests
    import json
    
    url = "https://web-production-15ac8.up.railway.app/assign-tasks"
    payload = {
        "tasks": TASKS_SAMPLE,
        "slots": SLOTS_SAMPLE
    }
    
    response = requests.post(url, json=payload)
    print("Status Code:", response.status_code)
    print("Response:")
    print(json.dumps(response.json(), indent=4))
    return response.json()

if __name__ == "__main__":
    # Si se ejecuta este archivo, muestra el payload de ejemplo
    print(get_request_payload())
    print("\nPara probar la API, ejecuta example_api_call()")
