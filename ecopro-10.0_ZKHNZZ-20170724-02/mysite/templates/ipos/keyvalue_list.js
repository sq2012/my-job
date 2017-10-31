{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"code":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>&nbsp;{{ item.code }}&nbsp;</a>{% else %}{{ item.code }}{% endif %}",
"money":"{{ item.money|trim}}",
"keyvaluemechine":"{{ item.useiclock }}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
