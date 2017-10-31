{% autoescape off %}
{% load i18n %}
[
{% for item in latest_item_list %}
{"id":"{{item.id}}",
"MeetID":"{{ item.MeetID.MeetID }}",
"PIN":"{{ item.UserID.PIN}}",
"EName":"{{ item.UserID.EName|default:''}}",
"DeptName":"{{ item.UserID.DeptID.DeptName }}",
"meet_detail":"{% if can_change%} <a href='#' onclick='del_meet({{item.id}});'><img title='{%trans '删除参会人员' %}' src='../media/img/close1.png'/></a>{% endif %}"





}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}