{% autoescape off %}
{% load i18n %}
[
{% for item in latest_item_list %}
{"id":"{{item.id}}",
"name":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.name }}</a>{% else %}{{ item.name}}{% endif %}",
"remark":"{{ item.remark|default:''}}",
"empCount":"{{ item.empCount }}",
"detail":"&nbsp;&nbsp{% if can_change%} <a class='can_edit' href='#' onclick='createDlg1({{item.id}});'>{%trans '添加人员' %}</a>{% endif %}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}