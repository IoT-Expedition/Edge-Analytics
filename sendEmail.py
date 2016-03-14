import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
 
def sendemail(knockeremail, displayText):	 
	fromaddr = "cmuiotexpedition@gmail.com"
	toaddr = knockeremail
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = "Door Knock Message"
	 
	body = displayText
	msg.attach(MIMEText(body, 'plain'))
	 
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, "cmuiot15")
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()
