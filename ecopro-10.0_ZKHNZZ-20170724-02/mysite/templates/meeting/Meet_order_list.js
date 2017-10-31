{% load i18n %}
{% load iclock_tags %}
{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"MeetID":"{% if can_change and item.State is not 2 %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.MeetID }}</a>{% else %}{{ item.MeetID }}{% endif %}",
"conferenceTitle":"{{ item.conferenceTitle|trim }}",
"MeetContents":"{{ item.MeetContents|trim}}",
"LocationID":"{{ item.LocationID|trim}}",
"Contact":"{{ item.Contact|trim}}",
"ContactPhone":"{{ item.ContactPhone|trim }}",
"Starttime":"{{ item.Starttime|shortTime0 }}",
"Endtime":"{{ item.Endtime|shortTime0 }}",
"Enrolmenttime":"{{ item.Enrolmenttime|shortTime0 }}",
"EnrolmentLocation":"{{ item.EnrolmentLocation|trim }}",
"LastEnrolmenttime":"{{ item.LastEnrolmenttime|shortTime0 }}",
"EarlySignOfftime":"{{ item.EarlySignOfftime|shortTime0 }}",
"LastSignOfftime":"{{ item.LastSignOfftime|shortTime0 }}",
"lunchtimestr":"{{ item.lunchtimestr|shortTime0 }}",
"lunchtimeend":"{{ item.lunchtimeend|shortTime0 }}",
"Sponsor":"{{ item.Sponsor|trim }}",
"Coorganizer":"{{ item.Coorganizer|trim }}",
"ApplyDate":"{{ item.ApplyDate|default:'' }}",
"State":"{{ item.get_State_display|get_State_State }}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
