{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"name":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.name }}</a>{% else %}{{ item.name }}{% endif %}",
"device":"{{ item.device|default:"" }}",
"cond":"{{ item.id|trigcon|default:"" }}",

"remark":"{{ item.remark|default:"" }}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
