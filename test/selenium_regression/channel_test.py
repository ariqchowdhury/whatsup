import unittest

from selenium import webdriver

from login_helper import whatsup_login

IP_ADDRESS = 'http://localhost:8888'

class ChannelTest(BaseWhatsupTester):

	def sendMsg(self, msg):
		comment_text = self.browser.find_element_by_id("comment")

	def test_send_message(self):
		self.browser.get(IP_ADDRESS)

		try:
			whatsup_login(self.browser, "Ironman", "jarvis")
		except NoSuchElementException:
			self.assertTrue(False)

		featured_list = self.browser.find_element_by_id("featured_list")
		list_elements = featured_list.find_elements_by_class_name("channel_title")

		list_elements[0].click()

		

