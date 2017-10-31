{% autoescape off %}
{% load i18n %}
[
{% for item in latest_item_list %}
{"id":"{{item.id}}",
"LocationID":"{{ item.LocationID }}",
"SN":"{{ item.SN}}",
"device_detail":"{% if can_change%} <a href='#' onclick='del_meet_devices({{item.id}});'><img title='{%trans '删除参会设备' %}' src='../media/img/close1.png'/></a>{% endif %}"

}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}