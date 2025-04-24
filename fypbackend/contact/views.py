from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ContactFormSerializer

class ContactFormView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ContactFormSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            # Prepare email content
            subject = f"Contact Form Submission: {data['subject']}"
            message = (
                f"First Name: {data['first_name']}\n"
                f"Last Name: {data['last_name']}\n"
                f"Phone Number: {data['phone_no']}\n"
                f"Email: {data['email']}\n"
                f"Message: {data['message']}\n"
            )
            sender_email = "techtitans121526@gmail.com"  # Replace with your Gmail address
            recipient_email = "techtitans121526@gmail.com"  # Replace with the recipient's email address

            try:
                # Send email using Gmail
                send_mail(subject, message, sender_email, [recipient_email] ,  data['email'])

                return Response({"message": "Message sent successfully!"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
