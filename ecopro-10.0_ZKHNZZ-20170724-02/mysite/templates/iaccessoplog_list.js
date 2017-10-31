[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"SN":"{{ item.SN }}",
"ObjName":"{{ item.Object}}",
"OPTime":"{{ item.OPTime }}",
"OpName":"{{ item.OpName|default:"" }}",
"Message":"{{ item.ObjName|default:"" }}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
