{% for part_of_speech, values in entries.items %}{% for value in values %}
[{{ part_of_speech }}] {{ value }}
{% endfor %}{% endfor %}
