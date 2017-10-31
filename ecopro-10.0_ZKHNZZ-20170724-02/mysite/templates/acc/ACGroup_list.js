{% autoescape off %}
[
{% for item in latest_item_list %}
{"GroupID":"{{ item.GroupID }}",
"Name":"{{ item.Name }}",
"TimeZone1":"{{ item.TimeZone1|default:0 }}",
"TimeZone2":"{{ item.TimeZone2|default:0 }}",
"TimeZone3":"{{ item.TimeZone3|default:0 }}",
"VerifyType":"{{ item.get_VerifyType_display|default:'' }}",
"HolidayValid":"{{ item.get_HolidayValid_display|default:'' }}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
