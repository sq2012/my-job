{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"DeptName":"{{ item.employee.Dept.DeptName }}",
"PIN":"{{ item.employee.PIN }}",
"EName":"{{ item.employee.EName|trim }}",
"Workcode":"{{ item.employee.Workcode|default:"" }}",
"Card":"{{ item.employee.Card|trim }}",
"bio_type":"{{item.bio_type_name}}",
"bio_name":"{{item.bio_name}}",
"bio_no":"{{item.bio_no}}",
"SN":"{{item.SN|default:''}}",
"UTime":"{{item.UTime|stdTime}}",

"AlgVer":"{{ item.majorver }}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
