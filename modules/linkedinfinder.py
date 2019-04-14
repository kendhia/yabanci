from __future__ import print_function
from selenium import webdriver
from pyvirtualdisplay import Display
from time import sleep
import os
import sys
from bs4 import BeautifulSoup

class Linkedinfinder(object):

	timeout = 10
	
	def __init__(self,showbrowser):
		display = Display(visible=0, size=(1600, 1024))
		display.start()
		if not showbrowser:
			os.environ['MOZ_HEADLESS'] = '1'
		self.driver = webdriver.Firefox()
		self.driver.implicitly_wait(15)
		self.driver.delete_all_cookies()


	def doLogin(self,username,password):
			
		self.driver.get("https://www.linkedin.com/uas/login")
		self.driver.execute_script('localStorage.clear();')

		#agent = self.driver.execute_script("return navigator.userAgent")
		#print("User Agent: " + agent)
		
		if(self.driver.title.encode('ascii','replace').startswith("Sign In")):
			print("\n[+] LinkedIn Login Page loaded successfully [+]")
			try:
				lnkUsername = self.driver.find_element_by_id("session_key-login")
			except:
				lnkUsername = self.driver.find_element_by_id("username")
			lnkUsername.send_keys(username)
			try:
				lnkPassword = self.driver.find_element_by_id("session_password-login")
			except:
				lnkPassword = self.driver.find_element_by_id("password")
			lnkPassword.send_keys(password)
			try:
				self.driver.find_element_by_id("btn-primary").click()
			except:
				self.driver.find_element_by_class_name("btn__primary--large").click()
			sleep(5)
			if(self.driver.title.encode('utf8','replace') == "Sign In to LinkedIn"):
				print("[-] LinkedIn Login Failed [-]\n")
			else:
				print("[+] LinkedIn Login Success [+]\n")


	def getLinkedinProfiles(self,first_name,last_name,username,password):
		
		picturelist = []
		url = "https://www.linkedin.com/search/results/people/?keywords=" + first_name + "%20" + last_name + "&origin=SWITCH_SEARCH_VERTICAL"
		self.driver.get(url)
		sleep(3)
		if "login" in self.driver.current_url: 
			self.doLogin(username,password)
			self.driver.get(url)
			sleep(3)
			if "login" in self.driver.current_url: 
				print("LinkedIn Timeout Error, session has expired and attempts to reestablish have failed")
				return picturelist	
		searchresponse = self.driver.page_source.encode('utf-8')
		soupParser = BeautifulSoup(searchresponse, 'html.parser')
		

		#LinkedIn has implemented some code to say no results seemly at random, need code to research if this result pops.
		## Anti Scraping Bypass (Try 3 times before skipping):
		#If there are no results do check
		if(len(soupParser.find_all('div', {'class': 'search-result__image-wrapper'})) == 0):
			#If there is the no results page do an additional try
			if(len(soupParser.find_all('div', {'class': 'search-no-results__image-container'}))!=0):
				#print("First Check")
				sleep(30)
				self.driver.get(url)
				if "login" in self.driver.current_url: 
					self.doLogin(username,password)
					self.driver.get(url)
					sleep(3)
					if "login" in self.driver.current_url: 
						print("LinkedIn Timeout Error, session has expired and attempts to reestablish have failed")
						return picturelist	
				searchresponse = self.driver.page_source.encode('utf-8')
				soupParser = BeautifulSoup(searchresponse, 'html.parser')
				if(len(soupParser.find_all('div', {'class': 'search-result__image-wrapper'})) == 0):
					if(len(soupParser.find_all('div', {'class': 'search-no-results__image-container'}))!=0):
						#print("Second Check")
						sleep(5)
						self.driver.get(url)
						if "login" in self.driver.current_url: 
							self.doLogin(username,password)
							self.driver.get(url)
							sleep(3)
							if "login" in self.driver.current_url: 
								print("LinkedIn Timeout Error, session has expired and attempts to reestablish have failed")
								return picturelist	
						searchresponse = self.driver.page_source.encode('utf-8')
						soupParser = BeautifulSoup(searchresponse, 'html.parser')
		#print("TEST\n\n\n\n\n\n")
		#print(len(soupParser.find_all('div', {'class': 'search-result__image-wrapper'})))
		#print(len(soupParser.find_all('div', {'class': 'search-no-results__image-container'})))
		for element in soupParser.find_all('div', {'class': 'search-result__image-wrapper'}):
			#print(element)
			try:
				# check for ghost-person tag in img class to skip headless profiles
				#ghostcheck = element.find('div')['class'] - OLD

				#ghostcheck = element.find_all('div')[1]['class']

				link = element.find('a')['href']
				#print(link)
				#profilepic = element.find('img')['src'] - OLD
				#profilepicreplaced = profilepic.replace("/mpr/mpr/shrink_100_100/","/media/") - OLD
				profilepic = element.find_all('div')[3]['style']
				profilepicreplaced = profilepic.replace("background-image: url(\"","").replace("\");","")
				#print(profilepicreplaced)
				picturelist.append(["https://linkedin.com" + link,profilepicreplaced,1.0])
				#print("append successs")
			#except Exception as e:
				#print("Error")
				#print(e)
				#continue			
			except:
				continue
		#print(picturelist)
		return picturelist

	def testdeletecookies(self):
		self.driver.delete_all_cookies()

	def kill(self):
		self.driver.quit()


