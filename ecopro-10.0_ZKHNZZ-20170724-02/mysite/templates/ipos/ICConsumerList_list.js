{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"user_pin":"{{ item.user_pin|trim }}",
"user_name":"{{ item.user_name|trim }}",
"dept":"{{ item.dept.DeptName|trim}}",
"card":"{{ item.card|trim}}",
"sys_card_no":"{% if "POS_IC"|filter_config_option %}{{ item.sys_card_no|trim}}{% endif %}",
"type_name":"{{ item.get_type_name_display|trim}}",
"money":"{{ item.money|trim}}",
"balance":"{{ item.balance|trim}}",
"pos_model":"{{ item.get_pos_model_display|trim}}",
"dining":"{{ item.dining.name|trim}}",
"meal":"{{ item.meal.name|trim|default:""}}",
"dev_sn":"{{ item.dev_sn|trim}}",
"dev_serial_num":"{{ item.dev_serial_num|trim}}",
"card_serial_num":"{{ item.card_serial_num|trim}}",
"pos_time":"{{ item.pos_time|stdTime}}",
"convey_time":"{{ item.convey_time|stdTime}}",
"log_flag":"{{ item.get_log_flag_display|trim}}",
"create_operator":"{{ item.create_operator|trim}}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
