{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"DeptNumber":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.department.DeptNumber }}</a>{% else %}{{ item.department.DeptNumber }}{% endif %}",
"DeptName":"{{ item.department.DeptName }}",
"PIN":"{{ item.employee.PIN }}",
"Workcode":"{{ item.employee.Workcode }}",
"EName":"{{ item.employee.EName|trim }}",
"FromDate":"{{ item.FromDate|shortDate4 }}" ,
"ToDate":"{{ item.ToDate|shortDate4 }}",
"ApplyDate":"{{ item.ApplyDate }}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
