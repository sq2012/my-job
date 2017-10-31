{% autoescape off %}
[
{% for item in latest_item_list %}
{"UnlockCombID":"{{ item.UnlockCombID }}",
"Name":"{{ item.Name }}",
"Group01":"{{ item.Group01|default:0 }}",
"Group02":"{{ item.Group02|default:0 }}",
"Group03":"{{ item.Group03|default:0 }}",
"Group04":"{{ item.Group04|default:0 }}",
"Group05":"{{ item.Group05|default:0 }}"}
{%if not forloop.last%},{%endif%}
{% endfor %}
]
{% endautoescape %}
