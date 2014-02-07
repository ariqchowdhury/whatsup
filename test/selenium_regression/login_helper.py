from selenium import webdriver

def whatsup_login(driver, user, password):
	username_ele = driver.find_element_by_name("username")
	password_ele = driver.find_element_by_name("password")
	submit_login_ele = driver.find_element_by_id("signin")

	username_ele.send_keys(user)
	password_ele.send_keys(password)

	submit_login_ele.click()