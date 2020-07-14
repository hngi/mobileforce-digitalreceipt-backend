import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart


class Gmail(object):
    def __init__(self, fromEmail, password):
        self.smtp_connect(fromEmail, password)

    def send_message(self, subject, body, toEmail):
        try:
            headers = [
                "From: " + self.fromEmail,
                "Subject: " + subject,
                "To: " + toEmail,
                "MIME-Version: 1.0",
                "Content-Type: text/html"]
            headers = "\r\n".join(headers)
            self.session.sendmail(
                self.fromEmail,
                toEmail,
                headers + "\r\n\r\n" + body)
            self.session.close()
        except Exception as error:
            self.smtp_connect(self.fromEmail, self.password)
            self.send_message(subject, body, toEmail)

    def send_pdf_message(self, subject, toEmail,uploaded_file):
        try:
            # Craft message (obj)
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = self.fromEmail
            msg['To'] = toEmail
            attach = MIMEApplication(uploaded_file.read(), _subtype="pdf")
            attach.add_header('Content-Disposition', 'attachment', filename=str(uploaded_file.name))
            msg.attach(attach)
            self.session.send_message(msg)
            self.session.close()
        except Exception as error:
            self.smtp_connect(self.fromEmail, self.password)
            self.send_pdf_message(subject, toEmail,uploaded_file)

    def smtp_connect(self, fromEmail, password):
        self.fromEmail = fromEmail
        self.password = password
        self.server = 'smtp.gmail.com'
        self.port = 587
        session = smtplib.SMTP(self.server, self.port)
        session.ehlo()
        session.starttls()
        session.ehlo
        session.login(self.fromEmail, self.password)
        self.session = session
