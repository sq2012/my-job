{% autoescape off %}
[
{% for item in latest_item_list %}
{"UserID":"{{ item.UserID }}",
"DeptName":"{{ item.employee.Dept.DeptName }}",
"PIN":"{{ item.employee.PIN|default:"" }}",
"Workcode":"{{ item.employee.Workcode|default:"" }}",
"EName":"{{ item.employee.EName|default:'' }}",
"TTime":"{{ item.TTime }}",
"Verify":"{{ item.getComVerifys|default:""  }}",
"State":"{{item.State|getRecordState}}",
"NewType":"{{item.NewType|getRecordState}}",
"AbNormiteID":"{{item.AbNormiteID|AbnormiteName}}",
"Device":"{{ item.Device|default:"" }}"
}{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
