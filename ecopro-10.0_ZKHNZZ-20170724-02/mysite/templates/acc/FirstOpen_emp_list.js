{% autoescape off %}
{% load i18n %}
[
{% for item in latest_item_list %}
{"id":"{{item.id}}",
"door":"{{ item.firstopen }}",
"device":"{{ item.firstopen.door.device }}",
"Card":"{{ item.UserID.Card|default:''}}",

"PIN":"{{ item.UserID.PIN}}",
"EName":"{{ item.UserID.EName|default:''}}",
"DeptName":"{{ item.UserID.Dept.DeptName }}",
"firstopen_details":"{% if can_change%} <a href='#' onclick='del_firstopen_emp({{item.id}});'><img title='{%trans '从该门删除' %}' src='../media/img/close1.png'/></a>{% endif %}"

}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}