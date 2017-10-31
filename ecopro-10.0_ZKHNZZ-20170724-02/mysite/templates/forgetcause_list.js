{% autoescape off %}
[
{% for item in latest_item_list %}
{
"id":"{{item.id}}",
"cause_Name":"{{ item.cause_Name }}"
}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
