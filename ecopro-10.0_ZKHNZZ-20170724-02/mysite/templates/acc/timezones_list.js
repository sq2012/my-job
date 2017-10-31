{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"tzid":"{{ item.id }}",
"Name":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.Name }}</a>{% else %}{{ item.Name }}{% endif %}",
"remark":"{{ item.remark|default:'' }}",
"details":""}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
