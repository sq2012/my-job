{% autoescape off %}
{% load iclock_tags %}

[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"time":"{{ item.time|isoTime }}",
"User":"{{ item.User|default:"" }}",
"action":"{{ item.action|default:"" }}",
"model":"{{ item.model|killnone|default:"" }}",
"object":"{{ item.object|objj}}",
"count":"{{ item.count|default:"" }}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}

