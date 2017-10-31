[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"SN":"{{ item.SN }}",
"admin":"{{ item.admin }}",
"OpName":"{{ item.OpName|default:"" }}",
"OPTime":"{{ item.OPTime }}",
"ObjName":"{{ item.ObjName|default:"" }}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
