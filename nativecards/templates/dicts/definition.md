{% for part_of_speach, values in entries.items %}{% for value in values %}
[{{ part_of_speach }}] {{ value }}
{% endfor %}{% endfor %}
