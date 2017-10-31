{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"PIN":"{{ item.PIN }}",
"EName":"{{ item.EName|trim }}",
"DeptID":"{{ item.Dept.DeptNumber }}",
"DeptName":"{{  item.Dept.DeptName  }}",
"cardno":"{{ item.id|getEmpLostCard:'cardno'  }}",
"sys_card_no":"{{ item.id|getEmpLostCard:'sys_card_no'  }}",
"blance":"{{ item.id|getEmpLostCard:'blance' }}"

}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}