{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"PIN":"{{ item.UserID.PIN }}",
"EName":"{{ item.UserID.EName|trim }}",
"cardno":"{{ item.cardno|trim}}",
"sys_card_no":"{% if "POS_IC"|filter_config_option %}{{ item.sys_card_no|trim}}{% endif %}",
"itype":"{{ item.itype|trim}}",
"cardstatus":"{{ item.get_cardstatus_display|trim}}",
"Losetime":"{{ item.Losetime|stdTime}}",
"create_operator":"{{ item.create_operator|trim}}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
