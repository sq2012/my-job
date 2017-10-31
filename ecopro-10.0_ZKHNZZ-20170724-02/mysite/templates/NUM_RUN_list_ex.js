{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.Num_runID }}",
"Name":"{{ item.Name }}",
"StartDate":"{{ item.StartDate }}",
"EndDate":"{{ item.EndDate }}",
"Cycle":"{{ item.Cycle }}",
"Units":"{{ item.get_Units_display }}",
"h_unit":"{{ item.Units }}",
"Num_RunOfDept":"{{ item.Dept }}",
"shift_detail":""}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
