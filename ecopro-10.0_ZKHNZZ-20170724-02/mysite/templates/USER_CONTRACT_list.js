{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"PIN":"{{ item.employee.PIN }}",
"UserID":"{{ item.UserID.id }}",
"DeptID":"{{ item.employee.Dept.DeptNumber }}",
"DeptName":"{{ item.employee.Dept.DeptName }}",
"EName":"{{ item.employee.EName|trim }}",
"StartContractDay":"{{ item.StartContractDay|shortDate }}" ,
"EndContractDay":"{{ item.EndContractDay|shortDate }}",
"Notes":"{{ item.Notes }}",
"ApplyDate":"{{ item.ApplyDate }}",
"State":"{{ item.get_State_display }}",
"Type":"{{ item.get_Type_display }}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
