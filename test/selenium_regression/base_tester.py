from selenium import webdriver

import unittest

class BaseWhatsupTester(unittest.TestCase):
	def setUp(self):
		self.browser = webdriver.Firefox()
		self.browser.implicitly_wait(3)

	def tearDown(self):
		self.browser.quit()

	def whatsup_login(self, user, password):
		username_ele = self.browser.find_element_by_name("username")
		password_ele = self.browser.find_element_by_name("password")
		submit_login_ele = self.browser.find_element_by_id("signin")

		username_ele.send_keys(user)
		password_ele.send_keys(password)

		submit_login_ele.click()