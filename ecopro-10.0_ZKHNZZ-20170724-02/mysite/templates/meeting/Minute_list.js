{% load i18n %}
{% load iclock_tags %}
{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{item.FileNumber}}",
"FileNumber":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.FileNumber}});'>{{ item.FileNumber }}</a>{% else %}{{ item.FileNumber }}{% endif %}",
"FileName":"{{ item.FileName|trim }}",
"MeetID":"{{ item.MeetID.MeetID}}",
"conferenceTitle":"{{item.MeetID.conferenceTitle}}",
"SubmitUser":"{{ item.SubmitUser|trim}}",
"SubTime":"{{ item.SubTime|default:"" }}",
"Appendixes":"{{ item.Appendixes}}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
