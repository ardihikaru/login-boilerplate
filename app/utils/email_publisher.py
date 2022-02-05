from app.core.config import smtp as smtp_conf
from app.core.config.application import settings
from jinja2 import Environment, FileSystemLoader
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import asyncio
import smtplib
import logging
from pathlib import Path

L = logging.getLogger("uvicorn.error")


class EmailPublisher(object):
	"""
	An asynchronous class to validate a given password with multiple scenarios
	"""

	DEFAULT_PROJECT_DIR = Path(__file__).parent.parent
	DEFAULT_APP_NAME = settings.APP_NAME
	DEFAULT_APP_DESC = settings.APP_DESC
	DEFAULT_APP_WEBSITE = settings.APP_WEBSITE
	DEFAULT_SMTP_TEMPLATE_PATH = smtp_conf.SMTP_TEMPLATE_PATH

	def __init__(self, folder_path: str = DEFAULT_SMTP_TEMPLATE_PATH,
				 project_dir: str = DEFAULT_PROJECT_DIR,
				 app_name: str = DEFAULT_APP_NAME,
				 app_desc: str = DEFAULT_APP_DESC,
				 app_website: str = DEFAULT_APP_WEBSITE):
		self.project_dir = project_dir
		self.folder_path = folder_path
		self.app_name = app_name
		self.app_desc = app_desc
		self.app_website = app_website

		print(" >>> project_dir:", project_dir)
		print(" >>> folder_path:", folder_path)
		print(" >>> app_name:", app_name)
		print(" >>> app_desc:", app_desc)
		print(" >>> app_website:", app_website)
		print(" >>> DEFAULT_PROJECT_DIR:", self.DEFAULT_PROJECT_DIR)

	def __await__(self):
		async def closure():
			return self

		return closure().__await__()

	async def __aenter__(self):
		return self

	async def __aexit__(self, *args):
		pass

	async def compose_and_wait(self, email_obj):
		# re-build the subject email
		subject_email = f"[{self.app_name}] {email_obj['subject_email']}"

		# Send email!
		try:
			await self.send_email_and_wait(
				email_obj["email"],
				subject_email,
				await self.generate_html(email_obj["meta"]),
			)
		except Exception as e:
			L.error("Can't send mail. Reason={}".format(e))
			return False

		return True

	async def get_smtp_server(self):

		if smtp_conf.SMTP_SSL:
			server = smtplib.SMTP_SSL(
				smtp_conf.SMTP_SERVER,
				smtp_conf.SMTP_PORT
			)
		else:
			server = smtplib.SMTP(
				smtp_conf.SMTP_SERVER,
				smtp_conf.SMTP_PORT
			)
		if len(smtp_conf.SMTP_USERNAME) > 0:
			server.login(
				smtp_conf.SMTP_USERNAME,
				smtp_conf.SMTP_PASSWORD
			)
		return server

	async def send_email_and_wait(self, to_email, subject_email, html):
		message = MIMEMultipart()
		message['To'] = to_email
		message['Subject'] = subject_email

		message.attach(MIMEText(html, "html"))

		message['From'] = smtp_conf.SMTP_SENDER

		smtp_server = await self.get_smtp_server()
		smtp_server.set_debuglevel(True)
		smtp_server.sendmail(
			smtp_conf.SMTP_SENDER,
			to_email,
			message.as_string()
		)
		smtp_server.quit()

	async def generate_html(self, meta):
		template_loader = FileSystemLoader(f"{self.project_dir}/{self.folder_path}")
		env = Environment(loader=template_loader)
		env.trim_blocks = True
		env.lstrip_blocks = True
		template = env.get_template("email_verification.html")

		html = template.render(
			meta=meta,
			app_name=self.app_name,
			app_desc=self.app_desc,
			app_website=self.app_website,
		)
		return html


# """
# How to use:

async def main():
	sample_payload = {
		"email": "ardihikaru3@gmail.com",
		"subject_email": "Action required: Activate your account now",
		"meta" : {
			"full_name": "Ardi",
			"verify_email_link" : "http://shielded-lowlands-46380.herokuapp.com?l=bkbfskfsfsjnfds",
		}
	}

	epublisher = EmailPublisher()
	await epublisher.compose_and_wait(sample_payload)

	exit()  # Exit


if __name__ == '__main__':
	try:
		asyncio.get_event_loop().run_until_complete(main())
		asyncio.get_event_loop().run_forever()
	except Exception as err:
		print("Got error in the middle of execution ({})".format(err))
	except KeyboardInterrupt as err:
		print("Interrupted by keyboard")
	finally:
		print("Exiting App")

# """

epub = EmailPublisher()
