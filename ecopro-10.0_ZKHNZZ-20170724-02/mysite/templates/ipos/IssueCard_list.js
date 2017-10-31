{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"PIN":"{{ item.UserID.PIN }}",
"EName":"{{ item.UserID.EName|default:'' }}",
"sys_card_no":"{% if "POS_IC"|filter_config_option %}{{ item.sys_card_no|default:'' }}{% endif %}",
"issuedate":"{{ item.issuedate|stdTime|slice:":10"}}",
"DeptName":"{{ item.UserID.Dept.DeptName }}",
"card_privage":"{{ item.get_card_privage_display }}",
"cardstatus":"{{ item.get_cardstatus_display|default:'' }}",
"blance":"{{ item.blance|default:'0.00'}}",
"itype":"{{ item.itype|default:'' }}",

"cardno":"{{ item.cardno|trim}}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
