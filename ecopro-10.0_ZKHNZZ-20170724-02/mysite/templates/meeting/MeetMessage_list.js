{% load i18n %}
{% load iclock_tags %}
{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"MessageID":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>&nbsp;{{ item.MessageID }}&nbsp;</a>{% else %}{{ item.MessageID }}{% endif %}",
"MessageNotice":"{{ item.MessageNotice|trim }}",
"Meet_ID":"{{ item.Meet_ID.conferenceTitle}}",
"Emails":"{{ item.Emails|trim}}",
"CopyForEmail":"{{ item.CopyForEmail|trim}}",
"SendTime":"{{ item.SendTime|default:''}}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
