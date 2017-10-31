{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"Title":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editDefineclick({{item.id}});'>{{ item.Title }}</a>{% else %}{{ item.Title }}{% endif %}",
"PIN":"{{ item.PIN }}",
"Author":"{{ item.Author }}",
"Pubdate":"{{ item.Pubdate }}",
"Channel":"{{ item.Channel }}",
"admin":"{{ item.admin}}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
