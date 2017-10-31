{% autoescape off %}
{% load iclock_tags %}

[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"Device":"{{ item.Device }}",
"CmdContent":"{{ item.CmdContent|cmdShowStr }}",
"CmdCommitTime":"{{ item.CmdCommitTime|isoTime }}",
"CmdTransTime":"{{ item.CmdTransTime|isoTime }}",
"CmdOverTime":"{{ item.CmdOverTime|isoTime }}" ,
"CmdReturn":"{{ item.CmdReturn|trim }}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}