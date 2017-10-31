{% autoescape off %}
{% load iclock_tags %}
{% load i18n %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"name":"<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.name }}</a>",
"TimeZone":"{{ item.timeseg.Name|isDelete:item.timeseg.DelTag}}",
"doors":"{{ item.doorCount|default:'' }}",
"emps":"{{ item.empCount|default:'' }}",
"action":"&nbsp;&nbsp;<a href='#' onclick='Check_level_emp({{item.id}});'><img title='{%trans '显示该权限组人员' %}' src='../media/img/qu.png'/></a> &nbsp; {% if can_change%} <a href='#' onclick='createDlglevel_emp({{item.id}});'><img title='{%trans '添加人员' %}' src='../media/img/add.png'/></a>{% endif %}"

}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
