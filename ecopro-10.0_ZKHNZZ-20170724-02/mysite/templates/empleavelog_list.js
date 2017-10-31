{% autoescape off %}
{% load iclock_tags %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"PIN":"{{ item.employee.PIN }}",
"EName":"{{ item.employee.EName|trim }}",
"Workcode":"{{ item.employee.Workcode|default:"" }}",
"leavedate":"{{ item.leavedate|shortDate4}}" ,
"leavetype":"{{ item.get_leavetype_display|default:"" }}",
"reason":"{{ item.reason |default:""}}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
