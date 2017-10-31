{% autoescape off %}
[
{% for item in latest_item_list %}
{"UserID":"{{ item.UserID}}",
"DeptName":"{{ item.employee.Dept.DeptName }}",
"PIN":"{{ item.employee.PIN }}",
"Workcode":"{{ item.employee.Workcode }}",
"EName":"{{ item.employee.EName|default:'' }}",
"AttDate":"{{ item.AttDate|shortDate4|default:"" }}",
"StartTime":"{{ item.StartTime|onlyTime }}",
"EndTime":"{{item.EndTime|onlyTime}}" ,
"ExceptionID":"{{item.ExceptionID|ExceptionStr}}",
"TimeLong":"{{item.TimeLong|default:""}}",
"InScopeTime":"{{ item.InScopeTime|default:"" }}"
}{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
