{% autoescape off %}
[
{% for item in latest_item_list %}
{"UserID":"{{ item.UserID }}",
"DeptName":"{{ item.employee.Dept.DeptName }}",
"PIN":"{{ item.employee.PIN }}",
"EName":"{{ item.employee.EName }}",
"AttDate":"{{ item.AttDate|shortDate4|default:""  }}",
"SchName":"{{ item.SchName }}",
"AttChkTime":"{{item.AttChkTime}}" ,
"AttAddChkTime":"{{item.AttAddChkTime }}",
"AttLeaveTime":"{{item.AttLeaveTime}}",
}{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
