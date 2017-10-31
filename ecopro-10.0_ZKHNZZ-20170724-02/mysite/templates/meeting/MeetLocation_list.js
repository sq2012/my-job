{% load i18n %}
{% load iclock_tags %}
{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"roomNo":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.roomNo }}</a>{% else %}{{ item.roomNo }}{% endif %}",
"roomName":"{{ item.roomName|trim }}",
"Address":"{{ item.Address|trim}}",
"admin":"{{ item.admin|trim}}",
"Phone":"{{ item.Phone|trim}}",
"State":"{{ item.getState|default:'' }}",
"photo":"{{ item|thumbnailUrl }}",
"latestState":"<a href='#' onclick=showMeetState({{item.id}},'{{item.roomName}}');><img title='{%trans '显示近期会议' %}'  src='../media/img/Calendar.png' /></a>",
"devices":"{{ item.get_devices }}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
