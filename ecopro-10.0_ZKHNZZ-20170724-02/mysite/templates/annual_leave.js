{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"DeptID":"{{ item.Dept.DeptNumber }}",
"DeptName":"{{ item.Dept.DeptName }}",
"PIN":"{{ item.PIN }}",
"Workcode":"{{ item.Workcode }}",
"EName":"{{ item.EName|trim }}",
"Birthday":"{{ item.Birthday|shortDate4 }}",
"Hiredday":"{{ item.Hiredday|shortDate4 }}",
"WorkAge":"{{ item.id|getWorkAge:request }}",
"annual_std":"{{ item.id|getannual_fading:request }}",
"annual_ent":"{{ item.id|getannual_gongsi:request }}"

}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
