import os, time
import concurrent.futures
import selenium
from selenium import webdriver

try:
	exc = concurrent.futures.exc_worker
except AttributeError:
	exc = concurrent.futures.exc_worker = concurrent.futures.ThreadPoolExecutor(max_workers=16)
drivers = selenium.__dict__.setdefault("-drivers", [])

class_name = webdriver.common.by.By.CLASS_NAME
css_selector = webdriver.common.by.By.CSS_SELECTOR
xpath = webdriver.common.by.By.XPATH
tag_name = webdriver.common.by.By.TAG_NAME
driver_path = "misc/msedgedriver"
browsers = dict(
	edge=dict(
		driver=webdriver.edge.webdriver.WebDriver,
		service=webdriver.edge.service.Service,
		options=webdriver.EdgeOptions,
		path=driver_path,
	),
)
browser = browsers["edge"]

def create_driver():
	ts = time.time_ns()
	folder = os.path.join(os.getcwd(), f"d~{ts}")
	service = browser["service"](browser["path"])
	options = browser["options"]()
	options.add_argument("--headless")
	# options.add_argument("--disable-gpu")
	options.add_argument("--no-sandbox")
	options.add_argument("--deny-permission-prompts")
	options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
	prefs = {
		"download.default_directory" : folder,
		"profile.managed_default_content_settings.geolocation": 2,
	}
	options.add_experimental_option("prefs", prefs)

	try:
		driver = browser["driver"](
			service=service,
			options=options,
		)
	except selenium.common.SessionNotCreatedException as ex:
		if "Current browser version is " in ex.args[0]:
			v = ex.args[0].split("Current browser version is ", 1)[-1].split(None, 1)[0]
			url = f"https://msedgedriver.azureedge.net/{v}/edgedriver_win64.zip"
			import requests, io, zipfile
			with requests.get(url, headers={"User-Agent": "Mozilla/6.0"}) as resp:
				with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
					with z.open("msedgedriver.exe") as fi:
						with open("misc/msedgedriver.exe", "wb") as fo:
							b = fi.read()
							fo.write(b)
			driver = browser["driver"](
				service=service,
				options=options,
			)
		else:
			raise
	except selenium.common.WebDriverException as ex:
		argv = " ".join(args)
		search = "unrecognized Microsoft Edge version"
		if search in argv and "Chrome" in argv:
			v = argv.split("Stacktrace", 1)[0].rsplit("/", 1)[-1].strip()
			url = f"https://chromedriver.storage.googleapis.com/{v}/chromedriver_win32.zip"
			import requests, io, zipfile
			with requests.get(url, headers={"User-Agent": "Mozilla/6.0"}) as resp:
				with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
					with z.open("chromedriver.exe") as fi:
						with open("misc/msedgedriver.exe", "wb") as fo:
							b = fi.read()
							fo.write(b)
			driver = browser["driver"](
				service=service,
				options=options,
			)
		else:
			raise
	driver.folder = folder
	return driver

LAST_DRIVER = 0
def ensure_drivers():
	globals()["LAST_DRIVER"] = time.time()
	while len(drivers) < 1:
		drivers.append(exc.submit(create_driver))
		time.sleep(1)
def get_driver():
	globals()["LAST_DRIVER"] = time.time()
	if not drivers:
		drivers.append(exc.submit(create_driver))
	try:
		driver = drivers.pop(0)
		if hasattr(driver, "result"):
			driver = driver.result()
	except selenium.common.exceptions.WebDriverException:
		print_exc()
		driver = create_driver()
	else:
		try:
			exc.submit(getattr, driver, "title").result(timeout=0.25)
		except:
			print_exc()
			driver = create_driver()
	exc.submit(ensure_drivers)
	return driver
def return_driver(d):
	d.get("file://")
	drivers.append(d)
def update():
	if time.time() - LAST_DRIVER >= 3600:
		globals()["LAST_DRIVER"] = time.time()
		if not drivers:
			return
		try:
			d = drivers.pop(0)
			if hasattr(d, "result"):
				d = d.result()
		except:
			pass
		else:
			drivers.clear()
			return_driver(d)

def safecomp(gen):
	while True:
		try:
			e = next(gen)
		except StopIteration:
			return
		except selenium.common.StaleElementReferenceException:
			continue
		yield e


def yt_download(url, fmt="mp3", timeout=256):
	driver = get_driver()
	try:
		folder = driver.folder
		search = f"https://yt-download.org/api/button/{fmt}?url=" + url
		fut = exc.submit(driver.get, search)
		fut.result(timeout=16)

		w = driver.current_window_handle

		t = time.time()
		elems = None
		while not elems:
			if fmt == "mp3":
				elems = driver.find_elements(by=class_name, value="bit256")
			else:
				for q in (1080, 720, 480, 360, 240, 144):
					elems = driver.find_elements(by=class_name, value=f"v{q}p")
					if elems:
						break
			if not elems:
				elems = driver.find_elements(by=class_name, value="alert")
				if elems:
					raise FileNotFoundError("Video unavailable.")
			time.sleep(0.2)
			if time.time() - t > 16:
				raise TimeoutError("Widget failed to load.")
		elems[0].click()

		time.sleep(1)
		driver.switch_to.window(w)

		t = time.time()
		elems = None
		while not elems:
			elems = list(safecomp(e for e in driver.find_elements(by=css_selector, value="*") if e.text == "CONVERT" or e.text == "DOWNLOAD"))
			time.sleep(1)
			driver.switch_to.window(w)
			# if time.time() - t > 16:
				# raise TimeoutError("Convert button failed to load.")
		# time.sleep(10)
		if not os.path.exists(folder):
			os.mkdir(folder)
		if elems[0].text == "CONVERT":
			try:
				e = driver.find_element(by=xpath, value="//iframe[2]")
			except:
				pass
			else:
				driver.execute_script("arguments[0].setAttribute('style', 'z-index:-2147483648')", e)
			elems[0].click()

			t = time.time()
			while True:
				if elems:
					try:
						if elems[0].text == "DOWNLOAD":
							break
					except selenium.common.exceptions.StaleElementReferenceException:
						elems = ()
				if not elems:
					try:
						for e in driver.find_elements(by=css_selector, value="*"):
							if e.text == "DOWNLOAD":
								elems = (e,)
							elif "Convert Status: failed" in e.text:
								raise RuntimeError("Conversion failed.")
					except selenium.common.exceptions.StaleElementReferenceException:
						elems = ()
				time.sleep(1)
				if time.time() - t > timeout:
					raise TimeoutError("Download button failed to load.")
				driver.switch_to.window(w)
		try:
			e = driver.find_element(by=xpath, value="//iframe[2]")
		except:
			pass
		else:
			driver.execute_script("arguments[0].setAttribute('style', 'z-index:-2147483648')", e)
		elems[0].click()

		titles = list(safecomp(e for e in driver.find_elements(by=css_selector, value="*") if "Download " in e.text))
		if titles:
			title = titles[0].text.split("Download ", 1)[-1].split("\n", 1)[0]
		else:
			title = url.split("?", 1)[0].rsplit("/", 1)[-1]

		t = time.time()
		elems = None
		while not elems:
			elems = [e for e in os.listdir(folder) if e.endswith(f".{fmt}")]
			time.sleep(0.5)
			if time.time() - t > timeout:
				raise TimeoutError("Request timed out.")

		ts = time.time_ns()
		fn = f"cache/{ts}.{fmt}"
		if not os.path.exists("cache"):
			os.mkdir("cache")
		os.rename(os.path.join(folder, elems[0]), fn)
	finally:
		if os.path.exists(folder):
			for fn in os.listdir(folder):
				os.remove(os.path.join(folder, fn))
			os.rmdir(folder)
		driver.close()
	return title, fn