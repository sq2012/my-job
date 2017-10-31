{% load i18n %}
{% load iclock_tags %}
{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.SchclassID }}",
"SchID":"{{ item.SchclassID }}",
"SchName":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.SchclassID}});'>{{ item.SchName }}</a>{% else %}{{ item.SchName }}{% endif %}",
"Data":"&nbsp;<a href='#' title='正在使用此时段的班次' onclick='getNumrun(\"{{ item.SchclassID  }}\")'style='color:green'>B</a>&nbsp;",
"StartTime":"{{ item.StartTime|onlyTime }}",
"EndTime":"{{ item.EndTime|onlyTime }}",
"LateMinutes":"{{ item.LateMinutes|defaultEx }}",
"EarlyMinutes":"{{ item.EarlyMinutes|defaultEx }}" ,
"CheckIn":"{{ item.get_CheckIn_display|defaultEx }}",
"CheckOut":"{{ item.get_CheckOut_display|defaultEx }}",
"CheckInMins1":"{{ item.CheckInMins1|defaultEx }}",
"CheckInMins2":"{{ item.CheckInMins2|defaultEx }}",
"CheckOutMins1":"{{ item.CheckOutMins1|defaultEx }}",
"CheckOutMins2":"{{ item.CheckOutMins2|defaultEx }}",
"IsCalcOverTime":"{{ item.IsCalcOverTime|isYesNo }}",
"IsCalcComeOverTime":"{{ item.IsCalcComeOverTime|isYesNo }}",
"Holiday":"{{ item.Holiday|isYesNo }}",
"Color":"{{ item.Color|colorShowStr }}",
"AutoBind":"{{ item.get_AutoBind_display }}",
"IsCalcRest":"{{ item.IsCalcRest|isYesNo }}",
"StartRestTime":"{{ item.StartRestTime|onlyTime }}",
"EndRestTime":"{{ item.EndRestTime|onlyTime }}",
"StartRestTime1":"{{ item.StartRestTime1|onlyTime }}",
"EndRestTime1":"{{ item.EndRestTime1|onlyTime }}",
"TimeZoneType":"{{ item.TimeZoneType|isYesNo }}",
"TimeZoneOfDept":"{{ item.Dept }}",
"TimeZoneMins":"{{ item.GetTimeZoneMins }}",
"WorkDay":"{{ item.WorkDay }}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
