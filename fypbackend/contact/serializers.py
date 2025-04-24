from rest_framework import serializers

class ContactFormSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone_no = serializers.CharField(max_length=15)
    email = serializers.EmailField()
    message = serializers.CharField(style={'base_template': 'textarea.html'})
    subject = serializers.ChoiceField(choices=[
        ('general_inquiry', 'General Inquiry'),
        ('technical_support', 'Technical Support'),
        ('website_feedback', 'Website Feedback'),
    ])
