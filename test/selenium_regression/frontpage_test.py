import unittest

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from base_tester import BaseWhatsupTester

IP_ADDRESS = 'http://localhost:8888'

class FrontpageTest(BaseWhatsupTester):

	def test_title(self):
		self.browser.get(IP_ADDRESS)

		self.assertIn('Whatsup', self.browser.title)

	def test_featured_list(self):
		self.browser.get(IP_ADDRESS)

		# featured_list = self.browser.find_element_by_id("featured_list")
		list_elements = self.browser.find_elements_by_class_name("channel_title")

		for i, ele in enumerate(list_elements):
			print list_elements[i].text
			self.assertEqual("Channel %s" % (i+1), list_elements[i].text)

	def test_all_list(self):
		self.browser.get(IP_ADDRESS)

		all_list = self.browser.find_element_by_id("all_list")
		list_elements = all_list.find_elements_by_class_name("channel_title")

		for i, ele in enumerate(list_elements):
			self.assertEqual("Channel %s" % i, list_elements[i].text)

	def test_login(self):
		self.browser.get(IP_ADDRESS)

		try:
			self.whatsup_login("Ironman", "jarvis")
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
		self.browser.get(IP_ADDRESS)

		try:
			self.whatsup_login("Ironman", "jarvis")
		except NoSuchElementException:
			self.assertTrue(False)

		profile_menu = self.browser.find_element_by_id("user_dropdown")
		profile_menu.click()	

		logout_ele = self.browser.find_element_by_id("logout_link")
		logout_ele.click()

		self.assertIsNone(self.browser.get_cookie("whatsup_user_login"))

if __name__ == '__main__':
	unittest.main()


