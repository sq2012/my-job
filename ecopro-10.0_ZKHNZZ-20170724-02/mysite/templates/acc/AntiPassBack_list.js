{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"device":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.device }}</a>{% else %}{{ item.device }}{% endif %}",
"apb_rule":"{{ item|get_apb_rule_name }}" ,
"remark":""
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
