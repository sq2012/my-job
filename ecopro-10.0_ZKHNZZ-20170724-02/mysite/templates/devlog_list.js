{% autoescape off %}
{% load iclock_tags %}

[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"Device":"{{ item.Device.SN }}({{item.Device.Alias}})",
"OpTime":"{{ item.OpTime|isoTime }}",
"OP":"{{ item.OP|dataShowStr }}",
"Object":"{{ item.Object|lescape }}",
"Cnt":"{{ item.Cnt }}" ,
"ECnt":"{{ item.ECnt }}",
"DeviceSN":"{{ item.Device.SN }}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}