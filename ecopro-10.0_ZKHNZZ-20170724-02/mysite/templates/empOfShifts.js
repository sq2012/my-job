{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"DeptNumber":"{{ item.employee.Dept.DeptNumber }}",
"DeptName":"{{ item.employee.Dept.DeptName }}",
"PIN":"{{ item.employee.PIN }}",
"Workcode":"{{ item.employee.Workcode }}",
"EName":"{{ item.employee.EName|default:''  }}",
"StartDate":"{{ item.StartDate|shortDate4 }}",
"EndDate":"{{ item.EndDate|shortDate4 }}",
"NUM_OF_RUN_ID":"{{ item.NUM_OF_RUN_ID }}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
