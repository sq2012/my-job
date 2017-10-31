{% autoescape off %}
{% load iclock_tags %}
[
{% for item in latest_item_list %}
{"id":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.id }}&nbsp;&nbsp;&nbsp;</a>{% else %}{{ item.id }}{% endif %}",
"name":"{{ item.name }}",
"Creator":"{{ item|getGroupCreator }}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
