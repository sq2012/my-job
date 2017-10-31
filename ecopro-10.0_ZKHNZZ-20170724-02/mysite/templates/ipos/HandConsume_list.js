{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"pin":"{{ item.pin|trim }}",
"name":"{{ item.name|trim }}",
"card":"{{ item.card|trim}}",
"sys_card_no":"{% if "POS_IC"|filter_config_option %}{{ item.sys_card_no|trim}}{% endif %}",
"card_serial_no":"{{ item.card_serial_no|trim}}",
"money":"{{ item.money|trim}}",
"blance":"{{ item.blance|trim}}",
"meal":"{{ item.meal.name|trim}}",
"posdevice":"{{ item.posdevice|trim}}",
"hand_date":"{{ item.hand_date|stdTime}}",
"create_operator":"{{ item.create_operator|trim}}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
