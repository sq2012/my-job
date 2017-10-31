{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"code":"{{ item.code|trim }}",
"name":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.name|trim }}</a>{% else %}{{ item.name|trim }}{% endif %}",
"available":"{{ item.available|isYesNo }}",
"money":"{{ item.money|trim }}",
"starttime":"{{ item.starttime|onlyTime }}",
"endtime":"{{ item.endtime|onlyTime }}",
"remark":"{{ item.remark|trim}}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
