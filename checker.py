from requests import get
from exceptions import IncorrectEmailException, DisposableEmailException
from os.path import getmtime
from datetime import datetime
import re

URL = 'https://gist.githubusercontent.com/michenriksen/8710649/raw/e09ee253960ec1ff0add4f92b62616ebbe24ab87/disposable-email-provider-domains'
res = get(URL).content


def is_actual(file: object) -> bool:
	"""Check file's last time update. Function will return True if date is actual else False"""
	return True if str(datetime.fromtimestamp(getmtime(file)).date()) == str(
		datetime.today().strftime('%Y-%m-%d')) else False


def update_db(url: str) -> None:
	"""Update disposable email domains database. Will update one a day"""
	if not is_actual('resource.txt'):

		res = get(URL).text

		with open('resource.txt', 'w') as f:
			for i in res.split(r'\n'):
				f.write(i)


def quick_check(email: str) -> bool:
	"""Email fast check using regexp (available patterns)"""
	update_db(URL)
	pattern = re.compile(r"^[a-zA-Z0-9]{1}[a-zA-Z0-9_.%-+]{,63}@[a-zA-Z0-9]{1}[a-zA-Z0-9.-]{0,}\.[a-z|A-Z]{2,}]{,254}$")
	return True if re.match(pattern, email) else False


def is_disposable(email: str) -> bool:
	"""Make sure that email isn't disposable. Function will return True if email is disposable else return False"""
	domain = email.split('@')[1]

	with open('resource.txt') as f:
		for i in f.read().split('\n'):
			if domain == i:
				return True

	return False


def ping_mail(email):
	"""Check email exists using foreign API for SMTP ping"""
	response = get("https://isitarealemail.com/api/email/validate", params={'email': email})

	status = response.json()['status']
	match status:
		case 'valid':
			return {'is_valid': True, 'email': email}
		case 'invalid':
			return {'is_valid': False, 'email': email}
		case 'unknown':
			return {'is_valid': -1, 'email': email}


def deep_check(email: str) -> dict:
	"""
	Email deeply check.
	return: True if email exists
			False if email incorrect
			-1 if system can't verify email
	"""

	try:
		if not quick_check(email):
			raise IncorrectEmailException('Incorrect e-mail address!')
		if is_disposable(email):
			raise DisposableEmailException('E-mail is disposable! Please, use your real mail')
		ping_mail(email)
	except IncorrectEmailException as _e:
		print(_e)
		return {'is_valid': False, 'email': email}
	except DisposableEmailException as _e:
		print(_e)
		return {'is_valid': False, 'email': email}


if __name__ == '__main__':
	# update_db(URL)
	print(deep_check('ganjuibas@gmail.com'))
