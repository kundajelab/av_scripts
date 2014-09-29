# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

msg = MIMEText("Howdy")

me = 'avanti@stanford.edu';
you = 'avanti@stanford.edu';
msg['Subject'] = 'The contents of oink'
msg['From'] = 'yourmom@stanford.edu'
msg['To'] = 'avanti@stanford.edu'

s = smtplib.SMTP('smtp.stanford.edu')
s.starttls();
s.sendmail(me, [you], msg.as_string())
s.quit()
