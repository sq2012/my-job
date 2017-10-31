{% autoescape off %}
{% load i18n %}

[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"PIN":"{{ item.PIN }}",
"EName":"{{ item.EName|trim }}",
"DeptID":"{{ item.Dept.DeptID }}",
"Card":"{{ item.Card|default:""}}",
"DeptName":"{{  item.Dept.DeptName  }}",
"level_detail":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:addLevel({{item.id}});'>添加所属权限组</a>{% else %}添加所属权限组{% endif %}"

}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}