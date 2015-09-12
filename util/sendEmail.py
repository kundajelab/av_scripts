#!/usr/bin/env python
# Import smtplib for the actual sending function
import smtplib

def sendEmail(theSubject, theTo, theFrom="av-mail-sender@stanford.edu", theContents=""):
    from email.mime.text import MIMEText
    msg = MIMEText(theContents)

    msg['Subject'] = theSubject
    msg['From'] = theFrom
    msg['To'] = ",".join(theTo)

    s = smtplib.SMTP('smtp.stanford.edu')
    s.starttls();
    s.sendmail(theFrom, theTo, msg.as_string())
    s.quit()

if __name__ == "__main__":
    import argparse;
    parser = argparse.ArgumentParser("Script for email sending");
    parser.add_argument("--to", nargs="+",required=True);
    parser.add_argument("--sender",default="av-mail-sender@stanford.edu");
    parser.add_argument("--subject",required=True);
    parser.add_argument("--contents", default="");
    options = parser.parse_args();
    sendEmail(options.subject, options.to, options.sender, options.contents);


