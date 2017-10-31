{% autoescape off %}
{% load i18n %}
[
{% for item in latest_item_list %}
{"id":"{{item.id}}",
"tplID":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.id }}</a>{% else %}{{ item.id }}{% endif %}",
"Name":"{{ item.Name}}",
"empCount":"{{ item.empCount }}",
"participants_detail":"&nbsp;&nbsp;<a href='#' onclick='Check_participants({{item.id}});'><img title='{%trans '显示所有参会人员' %}' src='../media/img/qu.png'/></a>&nbsp;&nbsp{% if can_change%} <a href='#' onclick='createDlgparticipants1({{item.id}});'><img title='{%trans '添加参会人员' %}' src='../media/img/add.png'/></a>{% endif %}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}