{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{item.id}}",
"roleid":"{% if can_change %}<a class='can_edit'  href='#' onclick='javascript:editclick({{item.id}});'>&nbsp;{{ item.roleid }}&nbsp;</a>{% else %}{{ item.roleid }}{% endif %}",
"roleName":"{{ item.roleName }}",
"roleLevel":"{{ item.roleLevel|default:""}}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
