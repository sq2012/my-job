{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"code":"{{ item.code|trim }}",
"name":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>{{ item.name|trim }}</a>{% else %}{{ item.name|trim }}{% endif %}",
"discount":"{{ item.discount }}",
"pos_time":"{{ item.get_pos_time_display|trim}}",
"date_max_money":"{{ item.date_max_money }}",
"date_max_count":"{{ item.date_max_count }}",
"per_max_money":"{{ item.per_max_money }}",
"meal_max_money":"{{item.meal_max_money}}",
"meal_max_count":"{{ item.meal_max_count }}",
"less_money":"{{ item.less_money }}",
"max_money":"{{ item.max_money }}",
"use_date":"{{ item.use_date }}",
"remark":"{{ item.remark|trim}}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
