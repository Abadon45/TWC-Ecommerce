# your_project/email_backend.py

# from django.conf import setting
# from django.core.mail import EmailMultiAlternatives
# from allauth.account.adapter import DefaultAccountAdapter

# class MyAccountAdapter(DefaultAccountAdapter):
#     def send_mail(self, template_prefix, email, context):
#         subject = 'TWConline.store Password Reset'
#         text_body = 'Your plain text email content here'  # Customize this
#         html_body = '<p>Your HTML email content here</p>'  # Customize this

#         # Retrieve the actual email content from the context if available
#         if 'message' in context:
#             text_body = context['message']
#             html_body = context['message_html']

#         msg = EmailMultiAlternatives(subject, text_body, setting.EMAIL_HOST_USER, [email])
#         msg.attach_alternative(html_body, "text/html")
#         msg.send()