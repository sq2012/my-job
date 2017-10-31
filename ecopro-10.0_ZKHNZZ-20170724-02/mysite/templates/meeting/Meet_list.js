{% load i18n %}
{% load iclock_tags %}
{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"MeetID":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>&nbsp;{{ item.MeetID }}&nbsp;</a>{% else %}{{ item.MeetID }}{% endif %}",
"conferenceTitle":"{{ item.conferenceTitle|trim }}",
"MeetContents":"{{ item.MeetContents|trim}}",
"LocationID":"{{ item.LocationID|trim}}",
"meet_detail":"{% if can_change%} <a href='#' onclick='Check_meet({{item.id}});'><img title='{%trans '管理所有应参会人员' %}' src='../media/img/users.png'/></a>{% endif %}&nbsp;&nbsp;<a  title='实际参会人员' onclick='getLog_Meet(\"{{ item.id }}\")'style='color:green;'>R</a>&nbsp;&nbsp;<a title='请假人员'style='color:green;' onclick='getLeaves(\"{{ item.id }}\")'>L</a>&nbsp;&nbsp;<a title='缺席人员' style='color:green;' onclick='getAbsent(\"{{ item.id }}\")'>Q</a>&nbsp;",
"Contact":"{{ item.Contact|trim}}",
"ContactPhone":"{{ item.ContactPhone|trim }}",
"Starttime":"{{ item.Starttime|shortTime0 }}",
"Endtime":"{{ item.Endtime|shortTime0 }}",
"lunchtimestr":"{{ item.lunchtimestr|shortTime0 }}",
"lunchtimeend":"{{ item.lunchtimeend|shortTime0 }}",
"Enrolmenttime":"{{ item.Enrolmenttime|shortTime0 }}",
"EnrolmentLocation":"{{ item.EnrolmentLocation|trim }}",
"LastEnrolmenttime":"{{ item.LastEnrolmenttime|shortTime0 }}",
"EarlySignOfftime":"{{ item.EarlySignOfftime|shortTime0 }}",
"LastSignOfftime":"{{ item.LastSignOfftime|shortTime0 }}",
"Sponsor":"{{ item.Sponsor|trim }}",
"Coorganizer":"{{ item.Coorganizer|trim }}",
"Should":"{{ item.ShouldEmp }}"



}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
