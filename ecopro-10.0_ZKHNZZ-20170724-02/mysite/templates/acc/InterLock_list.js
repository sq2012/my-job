{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"device":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.device }}</a>{% else %}{{ item.device }}{% endif %}",
"interlock_rule":"{{ item|get_interlock_rule_name }}" ,
"remark":"{{ item.remark|default:"" }}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
