import unittest

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from base_tester import BaseWhatsupTester

IP_ADDRESS = 'http://localhost:8888'

class ChannelTest(BaseWhatsupTester):

	def sendMsg(self, msg):
		comment_text = self.browser.find_element_by_id("comment")
		comment_text.send_keys(msg)

		send_button = self.browser.find_element_by_id("send")
		send_button.click()

	def test_send_message(self):
		self.browser.get(IP_ADDRESS)

		try:
			self.whatsup_login("tester", "tester")
		except NoSuchElementException:
			self.assertTrue(False)

		featured_list = self.browser.find_element_by_id("featured_list")
		list_elements = featured_list.find_elements_by_class_name("link_for_channel")

		title_element = list_elements[0].find_element_by_class_name("channel_title")

		title_element.click()

		self.sendMsg("short test")
		short_msg_box = self.browser.find_element_by_id("short_messages_grid")
		
		try:
			msg = short_msg_box.find_element_by_id("message_post_wrapper_0").find_element_by_id("message_post_msg").text
		except NoSuchElementException:
			self.assertTrue(False)

		self.sendMsg("short test")
		self.sendMsg("short test")
		self.sendMsg("short test")
		self.sendMsg("short test")

		self.sendMsg("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum tempus ipsum sed leo convallis, eu interdum metus luctus.")
		self.sendMsg("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum tempus ipsum sed leo convallis, eu interdum metus luctus.")
		
		short_msg_box = self.browser.find_element_by_id("short_messages_grid")
		short_msg_list = short_msg_box.find_elements_by_class_name("message_post")
		self.assertEqual(len(short_msg_list), 5)

		long_msg_box = self.browser.find_element_by_id("long_messages")
		long_msg_list = long_msg_box.find_elements_by_class_name("message_post")
		self.assertEqual(len(long_msg_list), 2)

if __name__ == '__main__':
	unittest.main()

