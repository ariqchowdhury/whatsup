import unittest

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from login_helper import whatsup_login

IP_ADDRESS = 'http://localhost:8888'

class FrontpageTest(unittest.TestCase):
	def setUp(self):
		self.browser = webdriver.Firefox()
		self.browser.implicitly_wait(3)

	def tearDown(self):
		self.browser.quit()

	def test_title(self):
		self.browser.get(IP_ADDRESS)

		self.assertIn('Whatsup', self.browser.title)

	def test_featured_list(self):
		self.browser.get(IP_ADDRESS)

		featured_list = self.browser.find_element_by_id("featured_list")
		list_elements = featured_list.find_elements_by_class_name("channel_title")

		for i, ele in enumerate(list_elements):
			self.assertEqual("Channel %s" % i, list_elements[i].text)

	def test_all_list(self):
		self.browser.get(IP_ADDRESS)

		all_list = self.browser.find_element_by_id("all_list")
		list_elements = all_list.find_elements_by_class_name("channel_title")

		for i, ele in enumerate(list_elements):
			self.assertEqual("Channel %s" % i, list_elements[i].text)

	def test_login(self):
		self.browser.get(IP_ADDRESS)

		# login to website using test account
		# username_ele = self.browser.find_element_by_name("username")
		# password_ele = self.browser.find_element_by_name("password")
		# submit_login_ele = self.browser.find_element_by_id("signin")

		# username_ele.send_keys("Ironman")
		# password_ele.send_keys("jarvis")

		# submit_login_ele.click()

		try:
			whatsup_login(self.browser, "Ironman", "jarvis")
		except NoSuchElementException:
			self.assertTrue(False)

		# check that the navbar displays the username and register
		# form is removed
		user_dropdown = self.browser.find_element_by_id("user_dropdown")

		self.assertEqual(user_dropdown.text, "Ironman")

		try:
			register_form = self.browser.find_element_by_id("register_form")
		except NoSuchElementException:
			self.assertTrue(True)
		else:
			self.assertTrue(False)

		# Confirm user got the login cookie
		self.assertIsNotNone(self.browser.get_cookie("whatsup_user_login"))

	def test_logout(self):
		pass

if __name__ == '__main__':
	unittest.main()


