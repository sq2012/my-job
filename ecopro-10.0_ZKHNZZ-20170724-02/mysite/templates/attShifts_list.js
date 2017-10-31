{% autoescape off %}
[
{% for item in latest_item_list %}
{"UserID":"{{ item.UserID }}",
"DeptName":"{{ item.employee.Dept.DeptName }}",
"PIN":"{{ item.employee.PIN }}",
"EName":"{{ item.employee.EName }}",
"AttDate":"{{ item.AttDate|shortDate4|default:""  }}",
"SchId":"{{ item.SchId|default:"" }}",
"Late":"{{item.Late|default:""}}" ,
"Early":"{{item.Early|default:""}}",
"StartTime":"{{item.StartTime|isTrueOrFalse}}",
"EndTime":"{{ item.EndTime|isTrueOrFalse }}",
"Absent":"{{ item.Absent|isYesNo }}",
}{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
