{% autoescape off %}
{% load iclock_tags %}

[
{% for item in latest_item_list %}
{"id":"{{ item.HolidayID }}",
"HolidayName":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.HolidayID}});'>{{ item.HolidayName }}</a>{% else %}{{ item.HolidayName }}{% endif %}",
"StartTime":"{{ item.StartTime|shortDate4 }}" ,
"Duration":"{{ item.Duration }}",
"HolidayType":"{{ item.get_HolidayType_display|default:"" }}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
