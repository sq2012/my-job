{% autoescape off %}
{% load i18n %}
[
{% for item in latest_item_list %}
{"id":"{{item.id}}",
"tplID":"{{ item.participants_tplID_id }}",
"PIN":"{{ item.UserID.PIN|isDelete:item.UserID.DelTag}}",
"EName":"{{ item.UserID.EName|default:''}}",
"DeptName":"{{ item.UserID.DeptID.DeptName }}",
"participants_detail":"{% if can_change%} <a href='#' onclick='del_participants({{item.id}});'><img title='{%trans '删除参会人员' %}' src='../media/img/close1.png'/></a>{% endif %}"

}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}