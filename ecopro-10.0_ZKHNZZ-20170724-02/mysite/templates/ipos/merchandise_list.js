{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"code":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>&nbsp;{{ item.code }}&nbsp;</a>{% else %}{{ item.code }}{% endif %}",
"name":"{{ item.name|trim }}",
"barcode":"{{ item.barcode|trim}}",
"money":"{{ item.money|trim}}",
"rebate":"{{ item.rebate|trim}}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
