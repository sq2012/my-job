{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"HolidayID":"{{ item.HolidayID.HolidayID }}",
"HolidayName":"{{ item.HolidayID.HolidayName }}",
"StartTime":"{{ item.HolidayID.StartTime }}",
"EndTime":"{{ item.EndTime }}",
"TimeZoneID":"{{ item.TimeZoneID.TimeZoneID}}",
"Name":"{{ item.TimeZoneID.Name }}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
