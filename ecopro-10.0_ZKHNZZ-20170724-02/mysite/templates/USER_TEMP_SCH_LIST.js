{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"DeptName":"{{ item.UserID.DeptID.DeptName }}",
"PIN":"{{ item.UserID.PIN }}",
"EName":"{{ item.UserID.EName }}",
"ComeTime":"{{ item.ComeTime }}",
"LeaveTime":"{{ item.LeaveTime }}",
"SchclassID":"{{ item.SchclassID|schName }}"

}{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
