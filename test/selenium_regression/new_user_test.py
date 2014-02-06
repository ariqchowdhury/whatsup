from selenium import webdriver
import unittest

class NewUserTest(unittest.TestCase):
	def setUp(self):
		self.browser = webdriver.Firefox()
		self.browser.implicitly_wait(3)

	def tearDown(self):
		self.browser.quit()

	def test_title(self):
		self.browser.get('http://localhost:8888')

		self.assertIn('Whatsup', self.browser.title)

	def test_login_form_present(self):
		pass

	def test_register(self):
		pass


if __name__ == '__main__':
	unittest.main()


