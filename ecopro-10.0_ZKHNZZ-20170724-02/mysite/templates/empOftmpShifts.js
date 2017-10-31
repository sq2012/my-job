{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"DeptName":"{{ item.employee.Dept.DeptName }}",
"PIN":"{{ item.employee.PIN }}",
"Workcode":"{{ item.employee.Workcode }}",
"EName":"{{ item.employee.EName|trim }}",
"ComeTime":"{{ item.ComeTime }}",
"LeaveTime":"{{ item.LeaveTime }}",
"SchclassID":"{{ item.SchclassID|schName }}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
