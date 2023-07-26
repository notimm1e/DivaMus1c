import os, sys, time, urllib, orjson, io, random, subprocess, base64, traceback
import concurrent.futures
import selenium, requests, torch, openai, httpx
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from fp.fp import FreeProxy
import numpy as np
from PIL import Image
print_exc = lambda: sys.stdout.write(traceback.format_exc())

def print(*args, sep=" ", end="\n"):
	s = sep.join(map(str, args)) + end
	b = s.encode("utf-8")
	return sys.stdout.buffer.write(b)

if torch.cuda.is_available():
	try:
		torch.cuda.set_enabled_lms(True)
	except AttributeError:
		pass
image_to = lambda im, mode="RGB": im if im.mode == mode else im.convert(mode)
try:
	exc = concurrent.futures.exc_worker
except AttributeError:
	exc = concurrent.futures.exc_worker = concurrent.futures.ThreadPoolExecutor(max_workers=64)
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
	options.add_argument("--disable-gpu")
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
		if "Current browser version is " in (s := repr(ex)):
			v = s.split("Current browser version is ", 1)[-1].split(None, 1)[0]
			if os.name == "nt":
				url = f"https://msedgedriver.azureedge.net/{v}/edgedriver_win64.zip"
				import requests, io, zipfile
				with requests.get(url, headers={"User-Agent": "Mozilla/6.0"}) as resp:
					with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
						with z.open("msedgedriver.exe") as fi:
							with open("misc/msedgedriver.exe", "wb") as fo:
								b = fi.read()
								fo.write(b)
			else:
				url = f"https://msedgedriver.azureedge.net/{v}/edgedriver_linux64.zip"
				import requests, io, zipfile
				with requests.get(url, headers={"User-Agent": "Mozilla/6.0"}) as resp:
					with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
						with z.open("msedgedriver") as fi:
							with open("misc/msedgedriver", "wb") as fo:
								b = fi.read()
								fo.write(b)
			driver = browser["driver"](
				service=service,
				options=options,
			)
		else:
			raise
	except selenium.common.WebDriverException as ex:
		argv = " ".join(ex.args)
		search = "unrecognized Microsoft Edge version"
		if search in argv and "Chrome" in argv:
			v = argv.split("Stacktrace", 1)[0].rsplit("/", 1)[-1].strip()
			if os.name == "nt":
				url = f"https://chromedriver.storage.googleapis.com/{v}/chromedriver_win32.zip"
				import requests, io, zipfile
				with requests.get(url, headers={"User-Agent": "Mozilla/6.0"}) as resp:
					with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
						with z.open("msedgedriver.exe") as fi:
							with open("misc/msedgedriver.exe", "wb") as fo:
								b = fi.read()
								fo.write(b)
			else:
				url = f"https://chromedriver.storage.googleapis.com/{v}/chromedriver_linux64.zip"
				import requests, io, zipfile
				with requests.get(url, headers={"User-Agent": "Mozilla/6.0"}) as resp:
					with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
						with z.open("msedgedriver") as fi:
							with open("misc/msedgedriver", "wb") as fo:
								b = fi.read()
								fo.write(b)
			driver = browser["driver"](
				service=service,
				options=options,
			)
		else:
			raise
	driver.folder = folder
	driver.get("file://")
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
			exc.submit(getattr, driver, "title").result(timeout=0.5)
		except:
			print_exc()
			driver = create_driver()
	# exc.submit(ensure_drivers)
	return driver
def return_driver(d):
	d.get("file://")
	drivers.insert(0, d)
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

def determine_cuda(mem=1, priority=None, multi=False):
	if not torch.cuda.is_available():
		if multi:
			return [-1], torch.float32
		return -1, torch.float32
	n = torch.cuda.device_count()
	if not n:
		if multi:
			return [-1], torch.float32
		return -1, torch.float32
	import pynvml
	pynvml.nvmlInit()
	dc = pynvml.nvmlDeviceGetCount()
	handles = [pynvml.nvmlDeviceGetHandleByIndex(i) for i in range(dc)]
	gmems = [pynvml.nvmlDeviceGetMemoryInfo(d) for d in handles]
	tinfo = [torch.cuda.get_device_properties(i) for i in range(n)]
	high = max(COMPUTE_LOAD)
	if priority == "full":
		key = lambda i: (p := tinfo[i]) and (gmems[i].free >= mem, COMPUTE_LOAD[i], p.major, p.minor, p.multi_processor_count, p.total_memory)
	elif priority:
		key = lambda i: (p := tinfo[i]) and (gmems[i].free >= mem, COMPUTE_LOAD[i] < high * 0.975, p.multi_processor_count, p.total_memory)
	elif priority is False:
		key = lambda i: (p := tinfo[i]) and (gmems[i].free >= mem, COMPUTE_LOAD[i] < high * 0.75, COMPUTE_LOAD[i], -gmems[i].free, p.multi_processor_count)
	else:
		key = lambda i: (p := tinfo[i]) and (gmems[i].free >= mem, COMPUTE_LOAD[i] < high * 0.5, COMPUTE_LOAD[i], -p.multi_processor_count, -gmems[i].free)
	pcs = sorted(range(n), key=key, reverse=True)
	if multi:
		return [i for i in pcs if gmems[i].free >= mem], torch.float16
	return pcs[0], torch.float16

mcache = {}
def cached_model(cls, model, **kwargs):
	t = (cls, model, tuple(kwargs.items()))
	try:
		return mcache[t]
	except KeyError:
		mcache[t] = cls(model, **kwargs)
	print("CACHED_MODEL:", t)
	return mcache[t]

def backup_model(cls, model, force=False, **kwargs):
	t = (cls, model, tuple(kwargs.keys()))
	try:
		return mcache[t]
	except KeyError:
		pass
	if force:
		try:
			return cls(model, **kwargs)
		except Exception as ex:
			ex2 = ex
	else:
		try:
			return cls(model, local_files_only=True, **kwargs)
		except:
			fut = exc.submit(cached_model, cls, model, **kwargs)
			try:
				return fut.result(timeout=24)
			except Exception as ex:
				ex2 = ex
	if isinstance(ex2, concurrent.futures.TimeoutError):
		try:
			return fut.result(timeout=60)
		except concurrent.futures.TimeoutError:
			raise RuntimeError("Model is loading, please wait...")
	raise ex2

def safecomp(gen):
	while True:
		try:
			e = next(gen)
		except StopIteration:
			return
		except selenium.common.StaleElementReferenceException:
			continue
		yield e


class Bot:

	models = {}
	ctime = 0
	proxies = set()
	ptime = 0
	bad_proxies = set()
	btime = 0

	def __init__(self, token=""):
		self.token = token
		self.session = requests.Session()
		self.timestamp = time.time()
		self.fp = FreeProxy()

	def get_proxy(self, retry=True):
		if self.proxies and time.time() - self.ctime <= 120:
			return random.choice(tuple(self.proxies))
		while not self.proxies or time.time() - self.ptime > 240:
			i = random.randint(1, 3)
			if i == 1:
				repeat = False
				self.fp.country_id = ["US"]
			elif i == 2:
				repeat = True
				self.fp.country_id = None
			else:
				repeat = False
				self.fp.country_id = None
			proxies = self.fp.get_proxy_list(repeat)
			self.proxies.update("http://" + p for p in proxies)
			if self.proxies:
				self.ptime = time.time()
				break
			else:
				time.sleep(1)
		proxies = list(self.proxies)
		# print(proxies)
		if time.time() - self.btime > 480:
			self.bad_proxies.clear()
			self.btime = time.time()
		else:
			self.proxies.difference_update(self.bad_proxies)
		futs = [exc.submit(self.check_proxy, p) for p in proxies]
		for i, (p, fut) in enumerate(zip(proxies, futs)):
			try:
				assert fut.result(timeout=6)[0] == 105
			except:
				# print_exc()
				self.proxies.discard(p)
				self.bad_proxies.add(p)
		if not self.proxies:
			if not retry:
				return
				raise FileNotFoundError("Proxy unavailable.")
			return self.get_proxy(retry=False)
		self.ctime = time.time()
		return random.choice(tuple(self.proxies))

	def check_proxy(self, p):
		url = "https://raw.githubusercontent.com/thomas-xin/Miza/master/misc/deleter.py"
		with httpx.Client(timeout=3, http2=True, proxies=p, verify=False) as reqx:
			resp = reqx.get(url)
			return resp.content

	def art_dalle(self, prompt, kwargs=None, count=1):
		openai.api_key = self.token
		resp = openai.Image.create(
			prompt=prompt,
			n=count,
			size="512x512",
			user=str(id(self)),
		)
		print(resp)
		futs = []
		for im in resp.data:
			fut = exc.submit(self.session.get, im.url)
			futs.append(fut)
		for fut in futs:
			yield fut.result().content

	def dalle_i2i(self, prompt, image_1b, image_2b=None, force=False, count=1):
		openai.api_key = self.token
		if image_2b:
			im = Image.open(io.BytesIO(image_2b))
			if "A" not in im.mode:
				im.putalpha(im.convert("L").point(lambda x: x ^ 255))
				b = io.BytesIO()
				im.save(b, format="png")
				b.seek(0)
				image_2b = b.read()
			resp = openai.Image.create_edit(
				prompt=prompt,
				image=image_1b,
				mask=image_2b,
				n=count,
				size="512x512",
				user=str(id(self)),
			)
		else:
			if not prompt or not force:
				resp = openai.Image.create_variation(
					image=image_1b,
					n=count,
					size="512x512",
					user=str(id(self)),
				)
			else:
				im = Image.new("LA", (512, 512), 0)
				b = io.BytesIO()
				im.save(b, format="png")
				b.seek(0)
				image_2b = b.read()
				resp = openai.Image.create_edit(
					prompt=prompt,
					image=image_1b,
					mask=image_2b,
					n=count,
					size="512x512",
					user=str(id(self)),
				)
		print(resp)
		futs = []
		for im in resp.data:
			fut = exc.submit(self.session.get, im.url)
			futs.append(fut)
		for fut in futs:
			yield fut.result().content, 180000

	def art_mage(self, prompt, kwargs=None, **void):
		driver = get_driver()

		folder = driver.folder
		search = "https://www.mage.space/"
		fut = exc.submit(driver.get, search)
		fut.result(timeout=24)

		# elems = driver.find_elements(by=class_name, value="mantine-1qsvvs3")
		# if elems:
		# 	elems[0].click()
		# 	elems = driver.find_elements(by=class_name, value="mantine-q5ciiw")
		# 	if elems:
		# 		elems[0].click()
		# 	elems = driver.find_elements(by=class_name, value="mantine-8jlqcf")
		# 	if elems:
		# 		elems[0].click()

		time.sleep(2)
		elems = driver.find_elements(by=webdriver.common.by.By.ID, value="mantine-R3bm")
		if elems:
			driver.execute_script("document.getElementById('mantine-R3bm').style['z-index'] = -3")
			time.sleep(1)

		bar = driver.find_element(by=webdriver.common.by.By.ID, value="search-bar")
		bar.clear()
		try:
			bar.send_keys(prompt)
		except selenium.common.exceptions.WebDriverException:
			driver.execute_script("document.getElementById('search-bar').focus()")
			driver.execute_script(f"document.execCommand('insertText', false, {repr(prompt)});")

		driver.execute_script("document.getElementById('ZQvTCDloXyqgqlOiDvup').click()")
		# generate = driver.find_element(by=webdriver.common.by.By.ID, value="ZQvTCDloXyqgqlOiDvup")
		# generate.click()

		elems = None
		i = 0
		while not elems:
			if i >= 120:
				print("Mage: unavailable")
				return
			elems = driver.find_elements(by=tag_name, value="img")
			for e in reversed(elems):
				a = e.get_attribute("src")
				if "fdf0bcda49214494b6965064309ed6cc" in a:
					continue
				if a.startswith("https://cdn.mage.space/generate/"):
					break
			else:
				elems.clear()
			time.sleep(1)
			i += 1
		time.sleep(1)
		elems = driver.find_elements(by=class_name, value="mantine-1q3qenk")
		driver.delete_all_cookies()
		return_driver(driver)
		if elems:
			print("Mage: censored")
			raise PermissionError

		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
			"DNT": "1",
			"X-Forwarded-For": ".".join(str(random.randint(1, 254)) for _ in range(4)),
			"X-Real-Ip": ".".join(str(random.randint(1, 254)) for _ in range(4)),
		}
		print("Mage:", a)
		resp = self.session.get(a, headers=headers)
		if resp.status_code in range(200, 400):
			return [resp.content]
		print(resp.status_code, resp.text)

	def art_deepai(self, prompt, kwargs=None, **void):
		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
			"DNT": "1",
			"X-Forwarded-For": ".".join(str(random.randint(1, 254)) for _ in range(4)),
			"X-Real-Ip": ".".join(str(random.randint(1, 254)) for _ in range(4)),
			"api-key": "quickstart-QUdJIGlzIGNvbWluZy4uLi4K",
		}
		resp = self.session.post(
			"https://api.deepai.org/api/text2img",
			files=dict(text=prompt),
			headers=headers,
		)
		if resp.status_code in range(200, 400):
			print("DeepAI:", resp.text)
			url = resp.json()["output_url"]
			b = self.session.get(url, headers=headers).content
			image = Image.open(io.BytesIO(b))
			ims = [
				image.crop((0, 0, 512, 512)),
				image.crop((512, 0, 1024, 512)),
				image.crop((512, 512, 1024, 1024)),
				image.crop((0, 512, 512, 1024)),
			]
			ims2 = []
			for im in ims:
				p = np.sum(im.resize((32, 32)).convert("L"))
				if p > 1024:
					b = io.BytesIO()
					im.save(b, format="png")
					b.seek(0)
					ims2.append(b.read())
			if ims2:
				return ims2
			print("DeepAI: censored")
			raise PermissionError
		print(resp.status_code, resp.text)

	def art_openjourney(self, prompt, kwargs=None, **void):
		# if not any(w in prompt for w in ("style", "stylised", "stylized")):
		# 	prompt += ", mdjrny-v4 style"
		headers = {
			"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
			"DNT": "1",
			"X-Forwarded-For": ".".join(str(random.randint(1, 254)) for _ in range(4)),
			"X-Real-Ip": ".".join(str(random.randint(1, 254)) for _ in range(4)),
			"cache-control": "no-cache",
			"x-use-cache": "false",
			"x-wait-for-model": "true",
		}
		resp = None
		p = None
		for i in range(8):
			if not p and i < 5:
				p = self.get_proxy()
				print("Proxy2", p)
			else:
				p = None
			try:
				with httpx.Client(timeout=360, http2=True, proxies=p, verify=False) as reqx:
					resp = reqx.post(
						"https://api-inference.huggingface.co/models/prompthero/openjourney",
						headers=headers,
						data=dict(inputs=prompt, wait_for_model=True),
					)
			except Exception as ex:
				self.proxies.discard(p)
				print(repr(ex))
				p = None
				continue
			if resp.status_code == 503:
				try:
					d = resp.json()
					time.sleep(d["estimated_time"])
				except:
					p = None
				continue
			elif resp.status_code not in range(200, 400) or not resp.content:
				self.proxies.discard(p)
				p = None
				continue
			break
		if resp.status_code in range(200, 400):
			print("Openjourney:", resp)
			b = resp.content
			im = Image.open(io.BytesIO(b))
			p = np.sum(im.resize((32, 32)).convert("L"))
			if p > 1024:
				return [b]
			print("Openjourney: censored")
			raise PermissionError
		print(resp.status_code, resp.text)

	safety_checkers = {}
	# device, dtype = determine_cuda(0)
	# gen = torch.Generator(f"cuda:{device}" if device >= 0 else "cpu").manual_seed(time.time_ns() - 1)
	def art_stablediffusion_local(self, prompt, kwargs=None, model="stabilityai/stable-diffusion-xl-base-1.0", fail_unless_gpu=True, nsfw=False, count=1):
		from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline, StableDiffusionInpaintPipeline, StableDiffusionImageVariationPipeline
		if not kwargs.get("--init-image"):
			pf = StableDiffusionPipeline
		elif kwargs.get("--mask"):
			pf = StableDiffusionInpaintPipeline
		elif prompt:
			pf = StableDiffusionImg2ImgPipeline
		else:
			pf = StableDiffusionImageVariationPipeline
		out = []
		if self.models:
			device = next(iter(self.models))
			dtype = torch.float32 if device == "cpu" else torch.float16
		else:
			try:
				device, dtype = determine_cuda(priority=False)
				if not device:
					raise FileNotFoundError
			except:
				if torch.cuda.is_available():
					device = 0
					dtype = torch.float16
				else:
					device = -1
					dtype = torch.float32
		images = self.art_stablediffusion_sub(pf, model, prompt, kwargs, count, device, dtype, nsfw, fail_unless_gpu)
		out = []
		for im in images:
			b = io.BytesIO()
			im.save(b, format="png")
			print("StablediffusionL:", b)
			b.seek(0)
			out.append(b.read())
		return out

	def art_stablediffusion_sub(self, pf, model, prompt, kwargs, count, device=-1, dtype=torch.float32, nsfw=False, fail_unless_gpu=False):
		from diffusers import DPMSolverMultistepScheduler, StableDiffusionPipeline, StableDiffusionImg2ImgPipeline, StableDiffusionInpaintPipeline, StableDiffusionImageVariationPipeline
		cia = torch.cuda.is_available()
		models = self.models.setdefault(device, {})
		checkers = self.safety_checkers.setdefault(device, {})
		pipe = cia and models.get((pf, model))
		if pipe == False and fail_unless_gpu:
			return ()
		if not pipe:
			kw = {}
			try:
				if fail_unless_gpu and (device < 0 or not models.get((pf, model), True)):
					return
				pipe = backup_model(pf.from_pretrained, model, requires_safety_checker=True, torch_dtype=dtype, use_safetensors=True, variant="fp16", **kw)
				if device >= 0:
					pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead", fullgraph=True)
					pipe = pipe.to(f"cuda:{device}")
					pipe.enable_attention_slicing()
					pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
					try:
						pipe.enable_model_cpu_offload()
					except AttributeError:
						pass
			except:
				print_exc()
				if fail_unless_gpu:
					models[(pf, model)] = False
					print("StablediffusionL: CUDA f16 init failed")
					return ()
				pipe = backup_model(pf.from_pretrained, model, requires_safety_checker=pf is not StableDiffusionImageVariationPipeline, **kw)
			checkers[model] = pipe.safety_checker
			models[(pf, model)] = pipe
		if nsfw:
			pipe.safety_checker = lambda images, **kwargs: (images, [False] * len(images))
		else:
			pipe.safety_checker = checkers[model]
		# pipe = pipe.to(f"cuda:{device}")
		if kwargs.get("--init-image"):
			b = kwargs["--init-image"]
			if not isinstance(b, str):
				b = io.BytesIO(b)
			im = Image.open(b)
		if kwargs.get("--mask"):
			b = kwargs["--mask"]
			if not isinstance(b, str):
				b = io.BytesIO(b)
			mask = Image.open(b)
		with torch.cuda.device(device):
			if pf is StableDiffusionInpaintPipeline:
				data = pipe(
					prompt,
					image=image_to(im),
					mask_image=image_to(mask, mode="L"),
					num_images_per_prompt=count,
					num_inference_steps=int(kwargs.get("--num-inference-steps", 24)),
					guidance_scale=float(kwargs.get("--guidance-scale", 7.5)),
					strength=float(kwargs.get("--strength", 0.8)),
					output_type="latent",
				)
			elif pf is StableDiffusionImg2ImgPipeline:
				data = pipe(
					prompt,
					image=image_to(im),
					num_images_per_prompt=count,
					num_inference_steps=int(kwargs.get("--num-inference-steps", 24)),
					guidance_scale=float(kwargs.get("--guidance-scale", 7.5)),
					strength=float(kwargs.get("--strength", 0.8)),
					output_type="latent",
				)
			elif pf is StableDiffusionImageVariationPipeline:
				data = pipe(
					image=image_to(im),
					num_images_per_prompt=count,
					num_inference_steps=int(kwargs.get("--num-inference-steps", 24)),
					guidance_scale=float(kwargs.get("--guidance-scale", 7.5)),
					output_type="latent",
				)
			else:
				data = pipe(
					prompt,
					num_images_per_prompt=count,
					num_inference_steps=int(kwargs.get("--num-inference-steps", 24)),
					guidance_scale=float(kwargs.get("--guidance-scale", 7.5)),
					output_type="latent",
				)
		if not data or not data.images:
			return ()
		nsfw_content_detected = [data.nsfw_content_detected] if not isinstance(data.nsfw_content_detected, (list, tuple)) else data.nsfw_content_detected
		images = []
		for im, n in zip(data.images, nsfw_content_detected):
			if n:
				continue
			p = np.sum(im.resize((32, 32)).convert("L"))
			if p <= 1024:
				continue
			images.append(im)
		if not images and all(nsfw_content_detected):
			raise PermissionError("NSFW filter detected in non-NSFW channel. If you believe this was a mistake, please try again.")
		if model == "stabilityai/stable-diffusion-xl-base-1.0":
			model = "stabilityai/stable-diffusion-xl-refiner-1.0"
			cia = torch.cuda.is_available()
			models = self.models.setdefault(device, {})
			checkers = self.safety_checkers.setdefault(device, {})
			pipe = cia and models.get((pf, model))
			if pipe == False and fail_unless_gpu:
				return ()
			if not pipe:
				kw = {}
				try:
					if fail_unless_gpu and (device < 0 or not models.get((pf, model), True)):
						return
					pipe = backup_model(pf.from_pretrained, model, requires_safety_checker=True, torch_dtype=dtype, use_safetensors=True, variant="fp16", **kw)
					if device >= 0:
						pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead", fullgraph=True)
						pipe = pipe.to(f"cuda:{device}")
						pipe.enable_attention_slicing()
						pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
						try:
							pipe.enable_model_cpu_offload()
						except AttributeError:
							pass
				except:
					print_exc()
					if fail_unless_gpu:
						models[(pf, model)] = False
						print("StablediffusionL: CUDA f16 init failed")
						return ()
					pipe = backup_model(pf.from_pretrained, model, requires_safety_checker=pf is not StableDiffusionImageVariationPipeline, **kw)
				models[(pf, model)] = pipe
			pipe.safety_checker = lambda images, **kwargs: (images, [False] * len(images))
			data = pipe(
				[prompt] * len(images),
				image=images,
				num_images_per_prompt=1,
				num_inference_steps=int(kwargs.get("--num-inference-steps", 24)),
				guidance_scale=float(kwargs.get("--guidance-scale", 7.5)),
			)
			images = data.images
		return images

	def art_textsynth(self, prompt, kwargs=None, count=1):
		headers = {
			"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
			"DNT": "1",
			"Content-Type": "application/json",
			"X-Forwarded-For": ".".join(str(random.randint(1, 254)) for _ in range(4)),
			"X-Real-Ip": ".".join(str(random.randint(1, 254)) for _ in range(4)),
			"cache-control": "no-cache",
		}
		kwargs = kwargs or {}
		resp = None
		p = None
		for i in range(8):
			if not p and i < 5:
				p = self.get_proxy()
				print("Proxy2", p)
			else:
				p = None
			try:
				if "Authorization" not in headers:
					headers["Authorization"] = "Bearer 842a11464f81fc8be43ac76fb36426d2"
				with httpx.Client(timeout=360, http2=True, proxies=p, verify=False) as reqx:
					resp = reqx.post(
						"https://api.textsynth.com/v1/engines/stable_diffusion/text_to_image",
						headers=headers,
						data=orjson.dumps(dict(
							prompt=prompt,
							image_count=count,
							timesteps=int(kwargs.get("--num-inference-steps", 50)),
							guidance_scale=float(kwargs.get("--guidance-scale", 7.5)),
							width=512,
							height=512,
						)),
					)
			except Exception as ex:
				self.proxies.discard(p)
				print(repr(ex))
				p = None
				continue
			if resp.status_code == 503:
				try:
					d = resp.json()
					time.sleep(d["estimated_time"])
				except:
					p = None
				continue
			elif resp.status_code not in range(200, 400) or not resp.content:
				self.proxies.discard(p)
				p = None
				continue
			break
		if resp.status_code in range(200, 400):
			print("TextSynth:", resp)
			d = resp.json()
			print(d)
			ds = d["images"]
			ims = [base64.b64decode(b["data"].encode("ascii")) for b in ds]
			return ims
		print(resp.status_code, resp.text)

	def art_clipdrop(self, prompt, kwargs=None, **void):
		driver = get_driver()

		folder = driver.folder
		search = "https://clipdrop.co/stable-diffusion"
		fut = exc.submit(driver.get, search)
		fut.result(timeout=24)

		time.sleep(2)

		bar = driver.find_element(by=webdriver.common.by.By.NAME, value="prompt")
		bar.clear()
		try:
			bar.send_keys(prompt)
		except selenium.common.exceptions.WebDriverException:
			driver.execute_script("document.getElementsByName('prompt')[0].focus()")
			driver.execute_script(f"document.execCommand('insertText', false, {repr(prompt)});")

		driver.execute_script('for (var i=0; i<document.getElementsByClassName("transition-all").length; i++) {var e = document.getElementsByClassName("transition-all")[i]; if (e.textContent == "Generate") {e.click()}};')

		elems = None
		ims = []
		i = 0
		while not elems:
			if i >= 90 and ims:
				break
			if i >= 360:
				print("ClipDrop: unavailable")
				return
			elems = driver.find_elements(by=tag_name, value="img")
			for e in reversed(elems):
				a = e.get_attribute("src")
				if e not in ims and a.startswith("blob:https://clipdrop.co/"):
					ims.append(e)
					if len(ims) >= 4:
						break
					continue
			else:
				elems.clear()
			time.sleep(1)
			i += 1

		# Credit to https://github.com/fredi-python/ClipDropSDXL/tree/main and of course StabilityAI for the feature! This is only temporary until v1.0 releases!
		def get_file_content_chrome(driver, uri):
			result = driver.execute_async_script("""
				var uri = arguments[0];
				var callback = arguments[1];
				var toBase64 = function(buffer){for(var r,n=new Uint8Array(buffer),t=n.length,a=new Uint8Array(4*Math.ceil(t/3)),i=new Uint8Array(64),o=0,c=0;64>c;++c)i[c]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(c);for(c=0;t-t%3>c;c+=3,o+=4)r=n[c]<<16|n[c+1]<<8|n[c+2],a[o]=i[r>>18],a[o+1]=i[r>>12&63],a[o+2]=i[r>>6&63],a[o+3]=i[63&r];return t%3===1?(r=n[t-1],a[o]=i[r>>2],a[o+1]=i[r<<4&63],a[o+2]=61,a[o+3]=61):t%3===2&&(r=(n[t-2]<<8)+n[t-1],a[o]=i[r>>10],a[o+1]=i[r>>4&63],a[o+2]=i[r<<2&63],a[o+3]=61),new TextDecoder("ascii").decode(a)};
				var xhr = new XMLHttpRequest();
				xhr.responseType = 'arraybuffer';
				xhr.onload = function(){ callback(toBase64(xhr.response)) };
				xhr.onerror = function(){ callback(xhr.status) };
				xhr.open('GET', uri);
				xhr.setRequestHeader("X-Forwarded-For", '""" + ".".join(str(random.randint(1, 254)) for _ in range(4)) + """');
				xhr.setRequestHeader("X-Real-Ip", '""" + ".".join(str(random.randint(1, 254)) for _ in range(4)) + """');
				xhr.send();
			""", uri)
			if type(result) == int:
				raise Exception("Request failed with status %s" % result)
			return base64.b64decode(result)

		out = []
		for i, im in enumerate(ims):
			url = im.get_attribute('src')
			print("ClipDrop:", url)
			b = get_file_content_chrome(driver, url)
			out.append(b)
		return out

	def art(self, prompt, url="", url2="", kwargs={}, specified=False, dalle2=False, openjourney=False, nsfw=False, count=1):
		funcs = []
		# if not url and not dalle2 and nsfw:
		# 	funcs.append((self.art_textsynth, 4))
		if not specified and not url:
			funcs.append((self.art_deepai, 4))
			if openjourney:
				funcs.insert(0, (self.art_openjourney, 1))
			if dalle2:
				funcs.insert(0, (self.art_dalle, 4))
		if not specified and not url and os.name == "nt":
			funcs.append((self.art_mage, 1))
		if not funcs:
			return ()
		eff = 0
		funceff = [random.choice(funcs) for i in range(count - 1)]
		funceff.insert(0, funcs[0])
		if count > 1 and not specified and not url and os.name == "nt":
			funceff = [(self.art_clipdrop, (3 if count == 9 else 4))] * count + [(a, min(b, 2)) for a, b in funceff]
		while funceff:
			counts = [t[1] for t in funceff]
			imc = sum(counts)
			i = np.argmin(counts)
			if not i and len(funceff) > 1:
				i = 1
			if imc - counts[i] < count:
				break
			funceff.pop(i)
		futs = []
		for func, it in funceff:
			if eff >= count:
				break
			c = min(it, count - eff)
			fut = exc.submit(func, prompt, kwargs, count=c)
			futs.append(fut)
			eff += c
		random.shuffle(futs)
		out = []
		for fut in futs:
			try:
				ims = fut.result(timeout=420)
				if not ims:
					continue
				out.extend(ims)
			except:
				print_exc()
		print(len(out), futs, funceff, count)
		if not out and not nsfw and count:
			raise PermissionError("NSFW filter detected in non-NSFW channel. If you believe this was a mistake, please try again.")
		return out

if __name__ == "__main__":
	import sys
	token = sys.argv[1] if len(sys.argv) > 1 else ""
	bot = Bot(token)
	while True:
		print(bot.art(input(), url="a"))
