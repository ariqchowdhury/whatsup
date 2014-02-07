import unittest

from selenium import webdriver

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
		list_elements = featured_list.find_elements_by_class_name("channel_title")

		print list_elements

		# list_elements[0].click()

		# sendMsg("short test")
		# short_msg_box = self.browser.find_element_by_id("short_messages_grid")
		# msg = short_msg_box.find_element_by_id("message_post_wrapper_1").find_element_by_id("message_post_msg").text
		# print msg


if __name__ == '__main__':
	unittest.main()

