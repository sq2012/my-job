{% autoescape off %}
{% load i18n %}
[
{% for item in latest_item_list %}
{"id":"{{item.id}}",
"level":"{{ item.level.name }}",
"PIN":"{{ item.UserID.PIN}}",
"EName":"{{ item.UserID.EName|default:''}}",
"DeptName":"{{ item.UserID.Dept.DeptName }}",
"level_detail":"{% if can_change%} <a href='#' onclick='del_level_emp({{item.id}});'><img title='{%trans '从该权限组删除' %}' src='../media/img/close1.png'/></a>{% endif %}"

}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}