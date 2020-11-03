
def send_mail(recipient, subject, message):

    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    username = 'epqtimeclock@gmail.com'
    password = 'Fall_2020'

    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(message,'html'))
    
    print('sending mail to ' + recipient + ' on ' + subject)

    mailServer = smtplib.SMTP('smtp.gmail.com', 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(username, password)
    mailServer.sendmail(username, recipient, msg.as_string())
    mailServer.close()

