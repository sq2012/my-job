{% autoescape off %}
[
{% for item in latest_item_list %}
{"UserID":"{{ item.UserID }}",
"DeptName":"{{ item.employee.Dept.DeptName }}",
"PIN":"{{ item.employee.PIN }}",
"EName":"{{ item.employee.EName }}",
"AttDate":"{{ item.AttDate|shortDate4|default:""  }}",
"SchId":"{{ item.SchId|default:"" }}",
"exception":"{{item.exception|default:""}}" ,
"times":"{{item.times|default:""}}",
"memo":"{{item.memo}}",
}{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
