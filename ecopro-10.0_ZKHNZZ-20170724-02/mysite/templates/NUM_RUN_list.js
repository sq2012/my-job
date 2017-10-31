{% autoescape off %}

{% load i18n %}
[
{% for item in latest_item_list %}
{"id":"{{ item.Num_runID }}",
"Num_runID":"{{ item.Num_runID }}",
"Name":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.Num_runID}});'>{{ item.Name }}</a>{% else %}{{ item.Name }}{% endif %}",
"StartDate":"{{ item.StartDate|shortDate4 }}",
"EndDate":"{{ item.EndDate|shortDate4 }}",
"Cycle":"{{ item.Cycle }}",
"Units":"{{ item.get_Units_display }}",
"h_unit":"{{ item.Units }}",
"Num_RunOfDept":"{{ item.Dept }}",
"shift_detail":"{% if can_change%} <a class='can_edit' href='#' onclick='createDlgShift1({{item.Num_runID}});'>添加时段</a>{% endif %}"
}{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
