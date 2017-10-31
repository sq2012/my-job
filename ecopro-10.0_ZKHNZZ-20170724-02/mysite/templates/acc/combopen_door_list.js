{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"name":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.name }}</a>{% else %}{{ item.name }}{% endif %}",
"door_no":"{{ item.door.door_no }}",
"door_name":"{{ item.door.door_name }}",
"device":"{{ item.device.Alias|default:'' }}",
"details":""}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
