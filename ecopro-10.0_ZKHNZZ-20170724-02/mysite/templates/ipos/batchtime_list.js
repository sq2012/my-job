{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"name":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.name|trim }}</a>{% else %}{{ item.name|trim }}{% endif %}",
"isvalid":"{{ item.isvalid|isYesNo }}",
"starttime":"{{ item.starttime|onlyTime }}",
"endtime":"{{ item.endtime|onlyTime }}",
"remarks":"{{ item.remarks|trim}}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
