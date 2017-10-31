{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"PIN":"{{ item.PIN }}",
"EName":"{{ item.EName|trim }}",
"DeptID":"{{ item.Dept.DeptNumber }}",
"DeptName":"{{  item.Dept.DeptName  }}",
"Gender":"{{ item.get_Gender_display|default:"" }}" ,
"Title":"{{ item.Title|showTitle|default:"" }}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}