{% autoescape off %}
{% load i18n %}
[
{% for item in latest_item_list %}
{"id":"{{item.id}}",
"door":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.door }}</a>{% else %}{{ item.door }}{% endif %}",
"device":"{{ item.door.device}}",
"timeseg":"{{ item.timeseg}}",

"empCount":"{{ item.empCount }}",
"firstopen_detail":"&nbsp;&nbsp;<a href='#' onclick='Check_firstopen({{item.id}});'><img title='{%trans '显示所有人员' %}' src='../media/img/qu.png'/></a>&nbsp;&nbsp;{% if can_change%} <a href='#' onclick='createDlgFirstOpen1({{item.id}});'><img title='{%trans '添加人员' %}' src='../media/img/add.png'/></a>{% endif %}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}