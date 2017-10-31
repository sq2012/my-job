{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"door_no":"{{ item.door_no }}",
"door_name":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick(\"{{item.id}}\",\"/acc/data/AccDoor/\");'>{{ item.door.name }}</a>{% else %}{{ item.door_name }}{% endif %}",
"details":""}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
