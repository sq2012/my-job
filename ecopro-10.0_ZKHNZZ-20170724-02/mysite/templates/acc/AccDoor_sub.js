{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"door_no":"{{ item.door_no }}",
"door_name":"<a class='can_edit'  href='#' onclick='javascript:editclick(\"{{item.id}}\",\"/acc/data/AccDoor/\");'>{{ item.door_name }}</a>",
"device":"{{ item.device.Alias|default:'' }}",
"lock_active":"{%if item.lock_active %}{{ item.lock_active.Name|isDelete:item.lock_active.DelTag }}{% else %}{% endif %}",
"opendoor_type":"{{ item.get_opendoor_type_display|default:'' }}",
"firstOpenCount":"{{ item.firstOpenCount }}",
"combOpenCount":"{{ item.combOpenCount }}",
"details":""}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
