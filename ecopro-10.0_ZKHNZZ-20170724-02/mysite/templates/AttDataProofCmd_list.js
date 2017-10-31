{% autoescape off %}
{% load iclock_tags %}

[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"Device":"{{ item.Device }}",
"OperateTime":"{{ item.OperateTime|isoTime }}",
"StartTime":"{{ item.StartTime|isoTime }}",
"EndTime":"{{ item.EndTime|isoTime }}",
"flag":"{{ item.flag|getFlag }}" ,
"DevCount":"{{ item.DevCount|default:"" }}",
"SerCount":"{{ item.SerCount|default:"" }}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}