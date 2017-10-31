{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"door_no":"{{ item.door_no }}",
"door_name":"{{ item.door_name }}",
"device":"{{ item.device.Alias|default:'' }}",
"details":""}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
