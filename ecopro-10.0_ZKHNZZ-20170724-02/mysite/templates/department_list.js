{% load i18n %}
{% load iclock_tags %}
{% autoescape off %}
[
{% for item in latest_item_list %}
{"DeptID":"{{ item.DeptID }}",
"DeptNumber":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.DeptID}});'>&nbsp;{{ item.DeptNumber }}&nbsp;</a>{% else %}{{ item.DeptNumber }}{% endif %}",
"DeptName":"{{ item.DeptName|trim }}",
"Parent":"{{ item.Parent|trim }}",
"DeptAddr":"{{ item.DeptAddr|trim}}",
"DeptPerson":"{{ item.DeptPerson|trim}}",
"DeptPhone":"{{ item.DeptPhone|trim}}",
"empCount":"{{ item.empCount }}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
