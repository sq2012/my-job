{% load i18n %}
{% load iclock_tags %}
{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.SchclassID }}",
"SchID":"{{ item.SchclassID }}",
"SchName":"{{ item.SchName }}",
"StartTime":"{{ item.StartTime|onlyTime }}",
"EndTime":"{{ item.EndTime|onlyTime }}",
"TimeZoneOfDept":"{{ item.Dept }}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
