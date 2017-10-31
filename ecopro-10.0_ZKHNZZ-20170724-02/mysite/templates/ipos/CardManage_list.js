{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"card_no":"{{ item.card_no|trim }}",
"sys_card_no":"{% if "POS_IC"|filter_config_option %}{{ item.sys_card_no|trim}}{% endif %}",
"dining":"{{ item.dining|trim}}",
"card_privage":"{{ item.get_card_privage_display|trim}}",
"cardstatus":"{{ item.get_cardstatus_display|trim}}",
"time":"{{ item.time|stdTime}}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
