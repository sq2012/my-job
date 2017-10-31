{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"DeptNumber":"{{ item.id }}",
"DeptName":"{{ item.employee.Dept.DeptName }}",
"PIN":"{{ item.employee.PIN }}",
"EName":"{{ item.employee.EName }}",
"StartDate":"{{ item.StartDate }}",
"EndDate":"{{ item.EndDate }}",
"NUM_OF_RUN_ID":"{{ item.NUM_OF_RUN_ID.Name }}"
}{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
