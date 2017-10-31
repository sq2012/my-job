{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"LTime":"{{ item.LTime|isoTime }}",
"PIN":"{{ item.PIN}}",
"Name":"{{ item.Name|default:"" }}",
"DeptName":"{{ item.Dept.DeptName|default:"" }}",
"loginIP":"{{ item.loginIP|default:"" }}",
"action":"{{ item.action|default:"" }}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}

