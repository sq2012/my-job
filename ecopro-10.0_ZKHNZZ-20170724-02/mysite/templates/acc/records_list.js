{% load iclock_tags %}
{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"pin":"{% ifnotequal item.pin '0' %}{{item.pin }} {{ item.name|default:"" }}{% else %}{% endifnotequal %} ",
"card_no":"{{ item|AccRecords:'card'|default:"" }}",
"TTime":"{{ item.TTime|stdTime }}",
"inorout":"{{ item.get_inorout_display }}",
"verify":"{{ item|AccRecords:'verify'|default:"" }}",
"event_no":"{{ item.get_event_no_display|default:"" }}",
"Device":"{{ item.Device|default:"" }}",
"dev_serial_num":"{{ item.dev_serial_num|default:"" }}",
"event_point":"{{ item|AccRecords:'point'|default:"" }}"

}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
