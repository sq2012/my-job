{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"UserID":"{{ item.UserID.PIN }}",
"UserID__EName":"{{ item.UserID.EName|trim }}",
"dept":"{{ item.dept.DeptName|trim}}",
"card":"{{ item.card|trim}}",
"sys_card_no":"{% if "POS_IC"|filter_config_option %}{{ item.sys_card_no|trim}}{% endif %}",
"cardserial":"{{ item.cardserial|trim}}",
"hide_column":"{{ item.get_hide_column_display|trim}}",
"CashType":"{{ item.CashType.get_itype_display|trim}}",
"allow_type":"{{ item.get_allow_type_display|trim}}",
"money":"{{ item.money|trim}}",
"blance":"{{ item.blance|trim}}",
"convey_time":"{{ item.convey_time|trim}}",
"checktime":"{{ item.checktime|trim}}",
"sn":"{{ item.sn|trim}}",
"serialnum":"{{ item.serialnum|trim}}",
"log_flag":"{{ item.get_log_flag_display|trim}}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
