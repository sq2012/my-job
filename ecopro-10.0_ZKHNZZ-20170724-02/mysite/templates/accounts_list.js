{% autoescape off %}
[
{% for item in latest_item_list %}
{"id":"{{ item.id }}",
"StartTime":"{{ item.StartTime }}",
"EndTime":"{{ item.EndTime }}",
"Type":"{{ item.get_Type_display }}",
"Status":"{{ item.get_Status_display }}",
"Reserved":"{{ item.Reserved }}",
"User":"{{ item.User }}"}{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
