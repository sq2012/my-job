{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"PIN":"{{ item.PIN }}",
"pri":"{{ item.get_pri_display|default:'' }}",
"EName":"{{ item.employee.EName|trim }}",
"DeptID":"{{ item.employee.Dept.DeptNumber }}",
"DeptName":"{{ item.employee.Dept.DeptName }}",
"Card":"{{ item.employee.Card|default:""}}",
"Title":"{{ item.employee.Title|showTitle|default:"" }}",
"SN":"{{ item.SN }}",
"Alias":"{{ item.Device.Alias|default:'' }}"
}

{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}

