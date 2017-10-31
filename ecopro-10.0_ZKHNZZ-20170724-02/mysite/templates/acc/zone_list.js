{% load i18n %}
{% load iclock_tags %}
{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{ item.id }}",
"code":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}},undefined,\"{{ item.parentname|trim }}\");'>&nbsp;{{ item.code }}&nbsp;</a>{% else %}{{ item.code }}{% endif %}",
"name":"{{ item.name|trim }}",
"parent":"{{ item.parentname|trim }}",
"remark":"{{ item.remark|trim}}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
