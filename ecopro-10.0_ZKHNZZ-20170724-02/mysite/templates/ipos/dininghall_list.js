{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"code":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.code }}&nbsp;&nbsp;</a>{% else %}{{ item.code }}{% endif %}",
"name":"{{ item.name|trim }}",
"dedn":"{{ item|devdn}}",
"remark":"{{ item.remark|trim}}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
