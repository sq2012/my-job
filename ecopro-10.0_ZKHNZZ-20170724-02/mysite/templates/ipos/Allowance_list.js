{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"PIN":"{% if can_change %}{% ifequal item.is_pass 0 %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.UserID.PIN }}</a>{% else %}{{ item.UserID.PIN }}{%endifequal%}{% else %}{{ item.UserID.PIN }}{% endif %}",
"EName":"{{ item.UserID.EName|default:"" }}",
"DeptName":"{{ item.UserID.Dept.DeptName }}",
"cardno":"{{ item.UserID.Card|default:""}}",
"sys_card_no":"{% if "POS_IC"|filter_config_option %}{{ item.sys_card_no|default:'' }}{% endif %}",
"money":"{{ item.money|trim }}",
"receive_money":"{{ item.receive_money|trim }}",
"clear_money":"{{ item.sys_card_no|getclearmoney:item.batch|default:'0.00' }}",
"batch":"{{ item.batch|trim }}",
"is_ok":"{{ item.get_is_ok_display|trim}}",
"is_pass":"{{ item.get_is_pass_display|trim}}",
"pass_name":"{{ item.pass_name|trim }}",
"receive_date":"{{ item.receive_date|stdTime }}",
"valid_date":"{{ item.valid_date|stdTime }}",
"allow_date":"{{ item.allow_date|stdTime }}",
"remark":"{{ item.remark|trim}}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
