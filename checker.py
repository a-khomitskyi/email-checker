from requests import get
from exceptions import IncorrectEmailException, DisposableEmailException
from os.path import getmtime
from datetime import datetime
import re

URL = 'https://gist.githubusercontent.com/michenriksen/8710649/raw/e09ee253960ec1ff0add4f92b62616ebbe24ab87/disposable-email-provider-domains'
res = get(URL).content


def _is_actual(file: object) -> bool:
	"""Check file's last time update
	:param file: Name of temporary domain file
	:return: Function will return True if date is actual else False"""
	return True if str(datetime.fromtimestamp(getmtime(file)).date()) == str(
		datetime.today().strftime('%Y-%m-%d')) else False


def _update_db(url: str) -> None:
	"""Update disposable email domains database. Will update one a day
	:param url: Link on text file of domain
	:return: None"""
	if not _is_actual('resource.txt'):

		res = get(URL).text

		with open('resource.txt', 'w') as f:
			for i in res.split(r'\n'):
				f.write(i)


def quick_check(email: str) -> dict:
	"""Email fast check using regexp (available patterns)
	:param email: E-mail address"""
	_update_db(URL)
	pattern = re.compile(r"^[a-zA-Z0-9]{1}[a-zA-Z0-9_.%-+]{,63}@[a-zA-Z0-9]{1}[a-zA-Z0-9.-]{0,}\.[a-z|A-Z]{2,}]{,254}$")
	return {'is_valid': True, 'email': email} if re.match(pattern, email) else {'is_valid': False, 'email': email}


def _is_disposable(email: str) -> bool:
	"""Make sure that email isn't disposable.
	:param email: E-mail address
	:return: Function will	return True if email is disposable else return False"""
	domain = email.split('@')[1]

	with open('resource.txt') as f:
		for i in f.read().split('\n'):
			if domain == i:
				return True

	return False


def ping_mail(email):
	"""Check email exists using foreign API for SMTP ping
	:param email: E-mail address
	:returns: False if e-mail is invalid; True if e-mail is valid; -1 if e-mail isn't verify"""
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
	"""Email deeply check. return: True if email exists
	False if email incorrect -1 if system can't verify email
	:param email: E-mail address
	:returns: False if e-mail is invalid; True if e-mail is valid; -1 if e-mail isn't verify"""

	try:
		if not quick_check(email):
			raise IncorrectEmailException('Incorrect e-mail address!')
		if _is_disposable(email):
			raise DisposableEmailException('E-mail is disposable! Please, use your real mail')
		ping_mail(email)
	except IncorrectEmailException as _e:
		print(_e)
		return {'is_valid': False, 'email': email}
	except DisposableEmailException as _e:
		print(_e)
		return {'is_valid': False, 'email': email}


if __name__ == '__main__':
	print(deep_check('ganjuibas@gmail.com'))
