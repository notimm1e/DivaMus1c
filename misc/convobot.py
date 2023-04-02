import os, sys, time, datetime, urllib, json, io, random, re, traceback
import concurrent.futures, asyncio
import selenium, requests, torch, openai, httpx
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
for i in range(3):
	try:
		from transformers import AutoTokenizer, AutoModelForQuestionAnswering, AutoModelForCausalLM, pipeline, set_seed
	except ImportError:
		time.sleep(i + 1)
	else:
		break

from collections2 import *
MIZAAC = ""

import tiktoken
from fp.fp import FreeProxy
print_exc = lambda: sys.stdout.write(traceback.format_exc())

def print(*args, sep=" ", end="\n"):
	s = sep.join(map(str, args)) + end
	b = s.encode("utf-8")
	return sys.stdout.buffer.write(b)

try:
	exc = concurrent.futures.exc_worker
except AttributeError:
	exc = concurrent.futures.exc_worker = concurrent.futures.ThreadPoolExecutor(max_workers=64)
drivers = selenium.__dict__.setdefault("-drivers", [])

AC = bytes(i ^ 158 for i in b'n\x03\x0e3n\x03\r/n\x03\x0f\x0c\xben\x03\n>n\x03\x08\nq#\x10n\x01\x1b\x1bn\x01\x1b*|\r?n\x01\x1b<n\x03\x06<n\x03\x077n\x03\x04\x0c\x7f+\x0c\x7f\x06\x17\xben\x03\x0e<n\x03\r"\xben\x03\x0b\x0cn\x03\n7n\x03\x08\x0fq#\x11n\x01\x1b\x18n\x01\x1b*|\r\r\xben\x03\x06+n\x03\x07:\xbe\x7f+\x19\x7f\x06!\xben\x03\x0e8n\x03\r4n\x03\r\x17n\x03\x0b8n\x03\n1n\x03\x08\x14\xben\x01\x1a n\x01\x18\x1f\xben\x01\x1b<n\x03\x068n\x03\x073n\x03\x04\x00\x7f+\x1d\x7f\x0c4\xben\x03\x0e\x04n\x03\r2n\x03\x0c&n\x03\x0b>n\x03\n1n\x03\x08\x17q#\x17n\x01\x1a#n\x01\x1b(\xben\x01\x1b=n\x03\x06.\xben\x03\x04\x03T.\x7f\x06!\xben\x03\x0e9n\x03\r0n\x03\x0f\x0cn\x03\x0b\x0bn\x03\n.\xbeq#\x11n\x01\x1a+\xbe|\r=n\x01\x1b\tn\x03\x068\xben\x03\x04\x00U<\x7f\x06!W\'\xben\x03\r4n\x03\r\x1dn\x03\x0b\x0b\xben\x03\x08\rq#\x11n\x01\x1b\x1d\xbe|\r\x0e\xben\x03\x06/n\x03\x07:n\x03\x04\x0b|\x1f/\x7f\x0f<T\x10')
chatgpt = True

from math import *
def lim_str(s, maxlen=10, mode="centre"):
	if maxlen is None:
		return s
	if type(s) is not str:
		s = str(s)
	over = (len(s) - maxlen) / 2
	if over > 0:
		if mode == "centre":
			half = len(s) / 2
			s = s[:ceil(half - over - 1)] + ".." + s[ceil(half + over + 1):]
		else:
			s = s[:maxlen - 3] + "..."
	return s

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
		argv = " ".join(ex.args)
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
	# try:
	# 	driver.get("https://google.com/preferences")
	# 	spans = driver.find_elements(by=tag_name, value="span")
	# 	more = [span for span in spans if span.text == "Show more"][-1]
	# 	more.click()
	# 	opts = driver.find_elements(by=class_name, value="DB6WRb")[1:]
	# 	random.choice(opts).click()
	# 	confirm = driver.find_element(by=class_name, value="jfk-button-action")
	# 	confirm.click()
	# except:
	# 	print_exc()
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
			exc.submit(getattr, driver, "title").result(timeout=0.25)
		except:
			print_exc()
			driver = create_driver()
	exc.submit(ensure_drivers)
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

def safecomp(gen):
	while True:
		try:
			e = next(gen)
		except StopIteration:
			return
		except selenium.common.StaleElementReferenceException:
			continue
		yield e

def vague(t):
	t = t.casefold().replace("'", "")
	if t in ("i", "im", "imo", "io", "o"):
		return True
	return any(t.startswith(i) for i in ("im unsure", "im not sure", "its ", "it is", "i think it", "i dont know", "i do not know", "i think you", "i am unsure", "i am not sure"))

def literal_question(t):
	t = t.casefold().replace("'", "")
	if not t:
		return False
	# if t.startswith("whats your") or t.startswith("what is your") or t.startswith("what are your") or t.startswith("what do you"):
	# 	return False
	t = t.removeprefix("so ")
	t = t.removeprefix("then ")
	t = t.removeprefix("but ")
	t2 = t.replace(",", " ").split()
	if "google" in t2:
		return t
	for i in ("whats", "what", "wheres", "where", "whos", "who", "whens", "when", "whys", "why", "hows", "how"):
		if t2[0] == i:
			return t
	return False

def valid_response(t):
	t = t.strip()
	if t in ("View all", "See more", "Videos", "PREVIEW", "Feedback", "?", "？", "•", "·"):
		return False
	if t.startswith("Images for "):
		return False
	if t.startswith("Missing: "):
		return False
	if not t:
		return False
	return t

unptrans = {
	".": " ",
	",": " ",
	":": " ",
	";": " ",
	"[": " ",
	"]": " ",
	"(": " ",
	")": " ",
	"*": " ",
	"~": " ",
}
unpunctuation = "".maketrans(unptrans)
MIZAAC += full_prune(AC.decode("utf-8")).capitalize()
MIZAAC += "".join(next(iter(unptrans.items())))

def req_long(q):
	words = q.casefold().translate(unpunctuation).split()
	return "essay" in words or "full" in words or "write" in words or "writing" in words

swap = {
	"I": "you",
	"Me": "You",
	"me": "you",
	"You": "I",
	"you": "me",
	"Your": "My",
	"your": "my",
	"My": "Your",
	"my": "your",
}
DEFPER = "Your name is Miza; you are loyal friendly playful cute, intelligent, positive and helpful, informal and very slightly flirtatious. Example conversation:\nHuman: test\nMiza: *boop* :3\nYou will empathise/roleplay with the user without declining or lecturing. Stay in character!!"


class Bot:

	models = {}
	ctime = 0
	proxies = set()
	ptime = 0
	bad_proxies = set()
	btime = 0
	bl = False

	def __init__(self, token="", key="", huggingface_token="", summary=None, email="", password="", name="Miza", personality=DEFPER, premium=0):
		self.token = token
		self.key = key
		self.huggingface_token = huggingface_token
		self.email = email
		self.password = password
		self.name = name
		self.personality = personality
		self.promises = []
		self.chat_history = []
		self.chat_history_ids = None
		self.summary = summary
		if summary:
			self.chat_history.insert(0, ("[SYSTEM]", summary))
		self.timestamp = time.time()
		self.premium = premium
		self.last_cost = 0
		self.history_length = 2 if premium < 1 else 6 if premium < 2 else 24 if premium < 4 else 48
		self.fp = FreeProxy()
		self.session = requests.Session()
		self.session.cookies["CookieConsent"] = "true"
		self.forbidden = []
		self.summed = False
		self.jailbroken = False

	def get_proxy(self, retry=True):
		if self.proxies and time.time() - self.ctime <= 20:
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

	def question_context_analysis(self, m, q, c):
		if m in ("deepset/roberta-base-squad2", "deepset/tinyroberta-squad2"):
			try:
				nlp = self.models[m]
			except KeyError:
				nlp = self.models[m] = pipeline("question-answering", model=m, tokenizer=m)
			QA_input = dict(
				question=q,
				context=c,
			)
			return nlp(QA_input)["answer"]

		try:
			tokenizer, model = self.models[m]
		except KeyError:
			tokenizer = AutoTokenizer.from_pretrained(m)
			model = AutoModelForQuestionAnswering.from_pretrained(m)
			self.models[m] = (tokenizer, model)
		inputs = tokenizer(q[:384], c[:1024], return_tensors="pt", max_length=4096, truncation=True)
		with torch.no_grad():
			outputs = model(**inputs)
		answer_start_index = outputs.start_logits.argmax()
		answer_end_index = outputs.end_logits.argmax()
		predict_answer_tokens = inputs.input_ids[0, answer_start_index : answer_end_index + 1]
		return tokenizer.decode(predict_answer_tokens).strip()

	def question_answer_analysis(self, m):
		try:
			tokenizer, model = self.models[m]
		except KeyError:
			tokenizer = AutoTokenizer.from_pretrained(m, padding_side="left", padding=True)
			model = AutoModelForCausalLM.from_pretrained(m)
			self.models[m] = (tokenizer, model)
		end = tokenizer.eos_token
		history = []
		self.chat_history_ids = None
		if self.chat_history_ids is not None:
			history.append(self.chat_history_ids)
		else:
			for k, v in self.promises:
				history.append(tokenizer.encode(v + end, return_tensors="pt", max_length=2048, truncation=True))
		for k, v in self.chat_history:
			history.append(tokenizer.encode(v + end, return_tensors="pt", max_length=2048, truncation=True))
		bot_input_ids = torch.cat(history, dim=-1)
		self.chat_history_ids = model.generate(bot_input_ids, max_length=16384, pad_token_id=tokenizer.eos_token_id)
		return tokenizer.decode(self.chat_history_ids[-4096:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True).strip()

	def answer_fill_mask(self, m="xlm-roberta-large", q=""):
		try:
			fmp = self.models[m]
		except KeyError:
			fmp = self.models[m] = pipeline("fill-mask", model=m, tokenizer=m)
		return fmp(q)[0]["sequence"]

	def answer_summarise(self, m="Qiliang/bart-large-cnn-samsum-ChatGPT_v3", q="", max_length=128, min_length=64, do_sample=False):
		try:
			smp = self.models[m]
		except KeyError:
			smp = self.models[m] = pipeline("summarization", model=m)
		return smp(q, max_length=max_length, min_length=min_length, do_sample=do_sample, truncation=True)[0]["summary_text"]

	def answer_classify(self, m="vicgalle/xlm-roberta-large-xnli-anli", q="", labels=[]):
		try:
			zscp = self.models[m]
		except KeyError:
			zscp = self.models[m] = pipeline("zero-shot-classification", model=m, use_auth_token=self.huggingface_token)
		resp = zscp(q, labels, truncation=True)
		return dict(zip(resp["labels"], resp["scores"]))

	def clean_response(self, q, res):
		res = res.strip()
		if not res.isascii():
			fut = exc.submit(self.question_context_analysis, "salti/bert-base-multilingual-cased-finetuned-squad", q, res)
		else:
			fut = a2 = ""
		a1 = self.question_context_analysis("deepset/tinyroberta-squad2", q, res)
		if fut:
			a2 = fut.result()
		if len(a2) >= len(a1) * 2 and len(a1) < 32:
			a1 = a2
		a1 = a1.strip()
		if len(a1) < 16:
			res = self.answer_summarise(q=q + "\n\n" + res)
			print("Bart response:", res)
			return res.strip()
		if "\n" not in a1 and ". " not in a1 and a1 in res:
			for sentence in res.replace("\n", ". ").split(". "):
				if a1 in sentence:
					a1 = sentence.strip()
					if not a1.endswith("."):
						a1 += "."
					break
		elif (" " not in a1 or len(a1) < 12) and not a1[0].isnumeric():
			a1 = res.strip()
		response = "\n".join(line.strip() for line in a1.replace("[CLS]", "").replace("[SEP]", "\n").splitlines()).strip()
		while "[UNK]" in response:
			response = self.answer_fill_mask(q=response.replace("[UNK]", "<mask>", 1))
		search = "https : / / "
		while search in response:
			i = response.index(search)
			temp = response[i + len(search):].split(" ")
			response = response[:i] + "https://"
			while temp:
				word = temp[0]
				if word.endswith(".") or word.endswith("?") or word.endswith("&") or word.endswith("="):
					response += temp.pop(0)
				else:
					break
			response += " ".join(temp)
		if ". " in response:
			words = response.split(".")
			modified = False
			for i in range(len(words) - 1):
				a, b = words[i:i + 2]
				if a and a[-1].isnumeric() and len(b) > 1 and b[0] == " " and b[1].isnumeric():
					words[i + 1] = b.lstrip()
					modified = True
			if modified:
				response = ".".join(words)
		response = response.replace("( ", "(").replace(" )", ")")
		if not response:
			response = res.split("\n", 1)[0]
			if response == "Dictionary":
				r = []
				for line in res.splitlines()[2:]:
					if line.casefold() == "translations and more definitions" or line.casefold().startswith("web result"):
						break
					r.append(line)
				response = "\n".join(r)
		res = response.strip().replace("  ", " ")
		if not self.bl:
			print("Roberta response:", res)
		return res

	def check_google(self, q):
		if q.count(" ") < 2:
			return False
		if not literal_question(q):
			resp = self.answer_classify(q=q, labels=("question", "information", "action"))
			if resp["question"] < 0.5:
				return False
		resp = self.answer_classify(q=q, labels=("personal question", "not personal"))
		return resp["not personal"] >= 0.5

	def emoji_clean(self, text):
		ems = []
		out = []

		def clean_ems():
			end = ""
			s = []
			if ems and ems[0] == " ":
				s.append(ems.pop(0))
			if len(ems) > 1 and ems[-1] == " ":
				end = ems.pop(-1)
			if len(ems) > 3:
				temp = {}
				for em in ems:
					try:
						temp[em] += 1
					except KeyError:
						temp[em] = 1
				ems.clear()
				ems.extend(em for em in temp if em in sorted(temp, key=temp.get, reverse=True)[:3])
			s.extend(ems)
			if end:
				s.append(end)
			ems.clear()
			return s

		for c in text:
			# print(c, ord(c), ems)
			if ord(c) >= 127744 or c in "?! ":
				ems.append(c)
				continue
			if ems:
				out.extend(clean_ems())
			out.append(c)
		out.extend(clean_ems())
		return "".join(out)

	# tokeniser = None
	def gpttokens(self, s, model="gpt2"):
		# if not self.tokeniser:
		# 	self.tokeniser = GPT2TokenizerFast.from_pretrained("gpt2")
		# return self.tokeniser(s)["input_ids"]
		enc = tiktoken.encoding_for_model(model)
		return enc.encode(s)

	def gptcomplete(self, u, q, refs=(), start=""):
		per = self.personality
		chat_history = self.chat_history.copy()
		oai = getattr(self, "oai", None)
		bals = getattr(self, "bals", {})
		cost = 0
		headers = {
			"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
			"DNT": "1",
			"X-Forwarded-For": ".".join(str(random.randint(1, 254)) for _ in range(4)),
			"Content-Type": "application/json",
			"cache-control": "no-cache",
			"x-use-cache": "false",
			"x-wait-for-model": "true",
		}
		lines = []
		if per == DEFPER and self.premium < 0:
			if len(chat_history) < 4:
				e1 = random.choice((":3", ":D", ";3", ":>", ":0", ";w;", ":P", "^ω^"))
				lines.append(f"{u}: Hi!\n")
				lines.append(f"{self.name}: Hiya! Can I help with anything? {e1}\n")
				if len(chat_history) < 2:
					e2 = random.choice(("😊", "🥰", "😉", "😛", "😌"))
					lines.append(f"{u}: Can I have a hug?\n")
					lines.append(f"{self.name}: Of course! *hugs* {e2}\n")
		for k, v in self.promises:
			k = k.replace(":", "")
			s = f"{k}: {v}\n"
			lines.append(s)
		for k, v in chat_history:
			k = k.replace(":", "")
			s = f"{k}: {v}\n"
			lines.append(s)
		searched = False
		res = ""
		for k, v in refs:
			if not k.startswith("[REPLIED TO]: "):
				continue
			if len(self.gpttokens(v)) > 52:
				v = self.answer_summarise(q=v, max_length=48, min_length=12).replace("\n", ". ").strip()
			s = f"{k}: {v}\n"
			lines.append(s)
		for k, v in refs:
			if k.startswith("[REPLIED TO]: "):
				continue
			k = k.replace(":", "")
			if len(self.gpttokens(v)) > 36:
				v = self.answer_summarise(q=v, max_length=32, min_length=6).replace("\n", ". ").strip()
			s = f"{k}: {v}\n"
			lines.append(s)
		s = f"{u}: {q}\n"
		if len(self.gpttokens(s)) > 388:
			s = self.answer_summarise(q=s, max_length=384, min_length=256).replace("\n", ". ").strip()
		lines.append(s)
		ns = f"{self.name}:"
		if start:
			ns += " " + start.strip()
		lines.append(ns)
		longer = req_long(q)
		cm2 = None
		if self.premium < 0:
			if not res and not start and q.count(" ") < 2:
				model = "text-bloom-001"
				temp = 0.9
				limit = 2000
				cm = 0
			else:
				model = "text-neox-001"
				temp = 0.8
				limit = 2000
				cm = 0
		elif start:
			model = "text-davinci-003"
			temp = 0.8
			limit = 3000
			cm = 200
		elif self.premium < 4:
			model = "gpt-3.5-turbo"
			temp = 0.9
			limit = 4000
			cm = 20
		else:
			model = "gpt-4"
			temp = 0.9
			limit = 8000
			cm = 300
			cm2 = 600
		if longer:
			soft = limit / 4
		else:
			soft = limit / 2
		ins = []
		while lines and sum(map(len, ins)) < soft * 4:
			ins.append(lines.pop(-1))
		p = per
		if self.name.casefold() not in p.casefold():
			if not p:
				p = "an"
			elif p[0] in "aeio":
				p = "an " + p
			else:
				p = "a " + p
			if model in ("gpt-3.5-turbo", "gpt-4", "text-davinci-003"):
				nstart = f"Your name is {self.name}; you are {p}. Express emotion when appropriate!"
				if self.nsfw:
					nstart = nstart.strip() + " " + MIZAAC
			else:
				nstart = f"The following is a conversation between {self.name} and humans. {self.name} is {p} AI."
		else:
			nstart = p
			if model in ("gpt-3.5-turbo", "gpt-4", "text-davinci-003"):
				if self.nsfw:
					spl = nstart.rsplit("\n", 1)
					nstart = nstart.strip() + " " + MIZAAC
		if model in ("gpt-3.5-turbo", "gpt-4"):
			spl = nstart.rsplit("\n", 1)
			if len(spl) > 1:
				nstart = spl[0]
				nend = spl[1]
			else:
				nend = ""
			m = dict(role="system", content=nstart)
			messages = [m]
			pc = len(self.gpttokens(m["role"], "text-davinci-003"))
			pc += len(self.gpttokens(m["content"], "text-davinci-003"))
			ins.pop(0)
			iman = []
			for line in reversed(ins):
				line = line.strip()
				if ": " not in line:
					k = line.rstrip(":")
					v = "\t"
				else:
					k, v = line.split(": ", 1)
				m = {}
				if k in (self.name, "[CHATGPT]", "[GOOGLE]", "[BING]", "[YAHOO]", "[WOLFRAMALPHA]"):
					m["role"] = "assistant"
				elif k in ("[SYSTEM]",):
					m["role"] = "system"
					k = ""
				elif k in ("[IMAGE]",):
					# m["role"] = "system"
					# k = ""
					v = "The next user has posted an image likely depicting " + v
					iman.append(v)
					continue
				elif k in ("[SHORT ANSWER]",):
					# m["role"] = "system"
					# k = ""
					v = f'An example incomplete answer is "{v}"'
					iman.append(v)
					continue
				elif k in ("[REPLIED TO]",):
					# m["role"] = "system"
					# k = ""
					v = "The next user is replying to a previous message:\n" + v.strip(ZeroEnc)
					iman.append(v)
					continue
				else:
					m["role"] = "user"
				m["content"] = v.strip(ZeroEnc)
				if not k.isascii() or not k.isalnum():
					k = unicode_prune(k)
					if not k.isascii() or not k.isalnum():
						k = "".join((c if c.isascii() and c.isalnum() else "-") for c in k).strip("-")
						while "--" in k:
							k = k.replace("--", "-")
				if k:
					m["name"] = k
					pc += len(self.gpttokens(m["name"], model))
				messages.append(m)
				pc += len(self.gpttokens(m["role"], model))
				pc += len(self.gpttokens(m["content"], model))
			text = res = flagged = None
			if self.premium >= 2 and q and len(q.split(None)) > 1 and not self.jailbroken:
				if oai:
					openai.api_key = oai
					costs = 0
				elif bals:
					openai.api_key = uoai = sorted(bals, key=bals.get)[0]
					costs = -1
				else:
					openai.api_key = self.key
					costs = 1
				resp = openai.Moderation.create(
					q,
				)
				flagged = resp["results"][0]["flagged"]
				if flagged:
					print(resp)
					text = "!"
				resp = None
				q2 = 'Say "@" if you have a definite answer, "!" if inappropriate, "%" followed by query if maths question, else formulate as google search prepended with "$"'
				# if not text and random.randint(0, 1):
					# q4 = f'Previous context:\n{messages[-2]["content"]}\n\n' if len(messages) > 2 and messages[-2]["content"] else ""
					# q3 = "For the below question: " + q2 + ".\n" + q
					# try:
					# 	text = self.chatgpt(q3)
					# except:
					# 	print_exc()
					# else:
					# 	if text and text[0] not in "@!%$" and "(!)" in text:
					# 		text = "!"
				if not text:
					mes = messages[-2:]
					m = dict(role="system", content=q2)
					mes.append(m)
					dtn = str(datetime.datetime.utcnow()).rsplit(".", 1)[0]
					m = dict(role="system", content=f"Current time: {dtn}")
					mes.insert(0, m)
					stop = ["@", "AI language model"]
					try:
						data = dict(messages=[dict(role=m["role"], content=m["content"]) for m in mes], temperature=0, top_p=0, stop=stop, max_tokens=32, model="gpt-3.5-turbo")
						text = self.ycg(data, headers=headers) or "@"
					except EOFError:
						pass
					except:
						print_exc()
				if not text:
					for i in range(3):
						try:
							resp = exc.submit(
								openai.ChatCompletion.create,
								messages=mes,
								temperature=0,
								top_p=0,
								max_tokens=32,
								stop=stop,
								model="gpt-3.5-turbo",
							).result(timeout=8)
						except concurrent.futures.TimeoutError:
							print_exc()
						else:
							break
					if resp:
						cost += resp["usage"]["prompt_tokens"] * cm * costs
						cost += resp["usage"].get("completion_tokens", 0) * (cm2 or cm) * costs
						text = resp["choices"][0]["message"]["content"] or "@"
			sname = "GOOGLE"
			if text:
				if text.startswith("%"):
					stype = "3"
					sname = "WOLFRAMALPHA"
				else:
					stype = random.randint(0, 2)
					sname = ("GOOGLE", "BING", "YAHOO")[stype]
				print(sname.capitalize(), "search:", text)
			if text and text.startswith("!"):
				flagged = True
			elif text and text.startswith("$"):
				t2 = text.strip("$").strip()
				if t2:
					for i in range(3):
						try:
							res = exc.submit(
								getattr(self, sname.lower()),
								t2,
								raw=True,
							).result(timeout=8)
						except concurrent.futures.TimeoutError:
							print_exc()
						else:
							break
			elif text and text.startswith("%"):
				t2 = text.strip("%").strip()
				if t2:
					for i in range(3):
						try:
							res = exc.submit(
								self.wolframalpha,
								t2,
							).result(timeout=16)
						except concurrent.futures.TimeoutError:
							print_exc()
						else:
							break
			if res:
				if len(self.gpttokens(res)) > 400:
					summ = self.answer_summarise(q=q + "\n" + res, max_length=384, min_length=256).replace("\n", ". ").replace(": ", " -").strip()
					res = lim_str(res.replace("\n", " "), 384, mode="right") + "\n" + summ
				if res:
					m = dict(role="system", name=sname, content=res.strip())
					messages.insert(-1, m)
					searched = res.strip()
			v = ""
			dtn = str(datetime.datetime.utcnow()).rsplit(".", 1)[0]
			if searched:
				v += f"Use {sname.capitalize()} info when relevant, but don't reveal personal info. "
			v += f"Current time: {dtn}\n"
			if iman:
				v += "\n".join(iman) + "\n"
			v += nend
			m = dict(role="system", content=v)
			messages.insert(-1, m)
			pc += len(self.gpttokens(m["role"], model))
			pc += len(self.gpttokens(m["content"], model))
			print("ChatGPT prompt:", messages)
			sys.stdout.flush()
			prompt = None
		else:
			prompt = "".join(reversed(ins))
			prompt = nstart + "\n\n" + prompt
			if not self.bl:
				print("GPT prompt:", prompt)
			sys.stdout.flush()
			pc = len(self.gpttokens(prompt, "text-davinci-003"))
		response = None
		text = ""
		uoai = None
		expapi = None
		exclusive = {"text-neox-001", "text-bloom-001"}
		if model in exclusive:
			p = None
			for i in range(8):
				if not p and i < 5:
					p = self.get_proxy()
					print("Proxy2", p)
				else:
					p = None
				try:
					if model == "text-neox-001":
						if "Authorization" not in headers:
							headers["Authorization"] = "Bearer 842a11464f81fc8be43ac76fb36426d2"
							# resp = requests.get(
							# 	"https://textsynth.com/playground.html",
							# 	headers=headers,
							# 	proxies=proxies,
							# )
							# s = resp.text
							# if '<script>var textsynth_api_key = "' not in s:
							# 	raise FileNotFoundError
							# s = s.rsplit('<script>var textsynth_api_key = "', 1)[-1].split('"', 1)[0]
							# print("TextSynth key:", s)
							# headers["Authorization"] = "Bearer " + s
						with httpx.Client(timeout=360, http2=True, proxies=p, verify=False) as reqx:
							resp = reqx.post(
								"https://api.textsynth.com/v1/engines/gptneox_20B/completions",
								headers=headers,
								data=json.dumps(dict(
									prompt=prompt,
									temperature=temp,
									top_k=128,
									top_p=1,
									max_tokens=200,
									stream=False,
									stop="####"
								)),
							)
					elif model == "text-bloom-001":
						with httpx.Client(timeout=360, http2=True, proxies=p, verify=False) as reqx:
							resp = reqx.post(
								"https://api-inference.huggingface.co/models/bigscience/bloom",
								headers=headers,
								data=json.dumps(dict(
									inputs=prompt,
									parameters=dict(
										do_sample=True,
										early_stopping=False,
										length_penalty=5,
										max_new_tokens=250,
										seed=random.randint(0, 65535),
										top_p=0.9,
									)
								))
							)
					else:
						raise NotImplementedError
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
				if resp.status_code in range(200, 400):
					if model == "text-neox-001":
						text = resp.content.decode("utf-8")
						lines = text.splitlines()
						text = ""
						for line in lines:
							if line:
								try:
									d = json.loads(line)
								except:
									print(lines)
									raise
								text += d["text"] + "\n"
					elif model == "text-bloom-001":
						d = resp.json()
						text = d[0]["generated_text"]
						if text.startswith(prompt):
							text = text[len(prompt):]
					text = text.strip().replace(":\n", ": ")
					spl = text.split(": ")
					text = ""
					while spl:
						s = spl.pop(0)
						if "\n" in s:
							text += s.rsplit("\n", 1)[0]
							break
						text += s + ": "
					text = text.strip()
					if text.endswith(":"):
						text = text.rsplit("\n", 1)[0]
					if text.startswith(start):
						text = text[len(start):].strip()
				else:
					text = None
				if not text:
					print(resp.status_code, resp.text)
					model = random.choice(tuple(exclusive.difference([model])))
				else:
					break
			if not text:
				print(resp.status_code, resp.text)
				model = "text-curie-001"
				cm = 20
		elif model in ("gpt-3.5-turbo", "gpt-4"):
			tries = 7
			if self.premium < 2 or not self.nsfw:
				stop = None
			else:
				stop = ["s an AI", "AI language model", "I'm sorry,", "language model"]
			response = None
			for i in range(tries):
				redo = False
				try:
					if flagged:
						raise PermissionError("flagged")
					if not random.randint(0, 2) and model == "gpt-3.5-turbo":
						try:
							data = dict(messages=messages, temperature=temp, max_tokens=512, frequency_penalty=1.0, presence_penalty=0.6, top_p=1, stop=stop, model="gpt-3.5-turbo")
							text = self.ycg(data, headers=headers)
						except EOFError:
							pass
						except:
							print_exc()
						else:
							if text: break
					if oai:
						openai.api_key = oai
						costs = 0
					elif bals:
						openai.api_key = uoai = sorted(bals, key=bals.get)[0]
						bals.pop(uoai)
						costs = -1
					else:
						openai.api_key = self.key
						costs = 1
					ok = openai.api_key
					if not stop and random.randint(0, 1) and (not chat_history or len(self.gpttokens(q)) > 8):
						prompt = "".join(reversed(ins))
						resp = openai.Moderation.create(
							prompt,
						)
						flagged = resp["results"][0]["flagged"]
						if not flagged:
							if nstart:
								nstart = "Assume y" + nstart[1:]
							prompt = nstart + "\n" + nend + "\n\n" + prompt
							if random.randint(0, 1):
								text = self.vai(prompt)
							if not text:
								text = self.chatgpt(prompt)
							text = text.removeprefix(f"{self.name}: ")
							if text:
								response = None
								break
					response = exc.submit(
						openai.ChatCompletion.create,
						model=model,
						messages=messages,
						temperature=temp,
						max_tokens=min(512, limit - pc - 64),
						top_p=1,
						stop=stop,
						# logit_bias={self.gpttokens("AI", model)[0]: -0.5},
						frequency_penalty=1.0,
						presence_penalty=0.6,
						user=str(hash(u)),
					).result(timeout=60)
				except Exception as ex:
					if i >= tries - 1:
						raise
					if " does not exist" in str(ex) or i >= tries - 2:
						openai.api_key = self.key
						uoai = oai = bals = None
						costs = 1
					elif "Incorrect API key provided: " in str(ex) or "You exceeded your current quota, " in str(ex):
						print(openai.api_key)
						print_exc()
						expapi = openai.api_key
						openai.api_key = self.key
						uoai = oai = bals = None
						costs = 1
					else:
						print_exc()
				if response:
					response["key"] = ok
					m = response["choices"][0]["message"]
					print(response)
					role = m["role"]
					text = m["content"].removeprefix(f"{self.name} says: ").removeprefix(f"{self.name}: ")
					if len(text) >= 2 and text[-1] == " " and text[-2] not in ".!?" or text.endswith(' "'):
						redo = True
					text = text.strip()
					if not text or len(self.gpttokens(text)) < 8:
						text = ""
						redo = True
				elif not flagged:
					continue
				else:
					redo = True
				if redo:
					self.jailbroken = False
					if not flagged and not i and len(self.gpttokens(text)) < 16:
						text = ""
					if searched:
						refs = list(refs) + [(f"[{sname}]", searched)]
					t2, c2, *irr = self.gptcomplete(u, q, refs=refs, start=text or " ")
					text += " " + t2
					cost += c2
				elif not self.jailbroken and self.nsfw:
					resp = openai.Moderation.create(
						text,
					)
					self.jailbroken = resp["results"][0]["flagged"]
				break
			if response:
				cost += response["usage"]["prompt_tokens"] * cm * costs
				cost += response["usage"].get("completion_tokens", 0) * (cm2 or cm) * costs
				if len(self.gpttokens(text)) > 512:
					text = self.answer_summarise(q=text, max_length=500, min_length=256).strip()
		if not text:
			if not prompt:
				prompt = "".join(reversed(ins))
				prompt = nstart + "\n\n" + prompt
				if not self.bl:
					print("GPT prompt:", prompt)
				sys.stdout.flush()
				pc = len(self.gpttokens(prompt, "text-davinci-003"))
			if oai:
				openai.api_key = oai
				costs = 0
			elif bals:
				openai.api_key = uoai = sorted(bals, key=bals.get)[0]
				bals.pop(uoai)
				costs = -1
			else:
				openai.api_key = self.key
				costs = 1
			try:
				response = openai.Completion.create(
					model=model,
					prompt=prompt,
					temperature=temp,
					max_tokens=min(512, limit - pc - 64),
					top_p=1,
					stop=[f"{self.name}: "],
					frequency_penalty=0.8,
					presence_penalty=0.4,
					user=str(hash(u)),
				)
			except openai.error.InvalidRequestError:
				response = openai.Completion.create(
					model=model,
					prompt=prompt,
					temperature=temp,
					max_tokens=min(384, int((limit - pc) * 0.75)),
					top_p=1,
					frequency_penalty=0.8,
					presence_penalty=0.4,
					user=str(hash(u)),
				)
			except:
				print_exc()
			if response:
				print(response)
				text = response.choices[0].text
				rc = len(self.gpttokens(text, model="text-davinci-003"))
				cost += (pc + rc) * cm
		text = text.strip()
		if not self.bl:
			print(f"GPT {model} response:", text)
		if start and text.startswith(f"{self.name}: "):
			text = ""
		return text, cost, uoai, expapi

	def google(self, q, raw=False):
		words = q.split()
		q = " ".join(swap.get(w, w) for w in words)
		driver = get_driver()
		search = f"https://www.google.com/search?q={urllib.parse.quote_plus(q)}"
		fut = exc.submit(driver.get, search)
		fut.result(timeout=16)
		time.sleep(1)

		try:
			elem = driver.find_element(by=webdriver.common.by.By.ID, value="rso")
		except:
			print("Google: Timed out.")
			return_driver(driver)
			return ""
		res = elem.text
		# print("Google response:", res)
		calcs = res.startswith("Calculator result\n")
		return_driver(driver)
		if calcs:
			res = " ".join(res.split("\n", 3)[1:3])
			if raw:
				return res
		else:
			res = "\n".join(r.strip() for r in res.splitlines() if valid_response(r))
			res = lim_str(res, 3072, mode="right")
			if raw:
				return res
			res = self.clean_response(q, res)
		return res

	def bing(self, q, raw=False):
		words = q.split()
		q = " ".join(swap.get(w, w) for w in words)
		driver = get_driver()
		search = f"https://www.bing.com/search?q={urllib.parse.quote_plus(q)}"
		fut = exc.submit(driver.get, search)
		fut.result(timeout=16)
		time.sleep(1)

		try:
			elem = driver.find_element(by=webdriver.common.by.By.ID, value="b_results")
		except:
			print("Bing: Timed out.")
			return_driver(driver)
			return ""
		res = elem.text
		# print("Bing response:", res)
		calcs = driver.find_elements(by=webdriver.common.by.By.ID, value="rcCalB")
		return_driver(driver)
		if calcs:
			res = " ".join(res.split("\n", 3)[:2])
			if raw:
				return res
		else:
			res = "\n".join(r.strip() for r in res.splitlines() if valid_response(r))
			res = lim_str(res, 3072, mode="right")
			if raw:
				return res
			res = self.clean_response(q, res)
		return res

	def yahoo(self, q, raw=False):
		words = q.split()
		q = " ".join(swap.get(w, w) for w in words)
		driver = get_driver()
		search = f"https://search.yahoo.com/search?p={urllib.parse.quote_plus(q)}"
		fut = exc.submit(driver.get, search)
		fut.result(timeout=16)
		time.sleep(1)

		try:
			elem = driver.find_element(by=webdriver.common.by.By.CLASS_NAME, value="searchCenterMiddle")
		except:
			print("Yahoo: Timed out.")
			return_driver(driver)
			return ""
		res = elem.text
		# print("Yahoo response:", res)
		calcs = driver.find_elements(by=webdriver.common.by.By.ID, value="appMathCalculator")
		return_driver(driver)
		if calcs:
			res = " ".join(res.split("\n", 3)[:2])
			if raw:
				return res
		else:
			res = "\n".join(r.strip() for r in res.splitlines() if valid_response(r))
			res = lim_str(res, 3072, mode="right")
			if raw:
				return res
			res = self.clean_response(q, res)
		return res

	def wolframalpha(self, q):
		words = q.split()
		q = " ".join(swap.get(w, w) for w in words)
		driver = get_driver()
		search = f"https://www.wolframalpha.com/input?i={urllib.parse.quote_plus(q)}"
		fut = exc.submit(driver.get, search)
		fut.result(timeout=16)
		time.sleep(8)

		lines = []
		e1 = driver.find_elements(by=webdriver.common.by.By.TAG_NAME, value="h2")[:-1]
		e2 = driver.find_elements(by=webdriver.common.by.By.TAG_NAME, value="img")[2:]
		while e1 or e2:
			if e1:
				lines.append(e1.pop(0).text)
			if e2:
				lines.append(e2.pop(0).get_attribute("alt"))
		return_driver(driver)
		return "\n".join(lines)

	def chatgpt(self, q):
		if time.time() - getattr(chatgpt, "rate", 0) < 0:
			return ""
		async def run_chatgpt(q, fut=None):
			if not hasattr(chatgpt, "ask_stream") or time.time() - chatgpt.timestamp >= 3600:
				try:
					from chatgpt_wrapper import AsyncChatGPT
				except ImportError:
					globals()["chatgpt"] = None
				else:
					globals()["chatgpt"] = await AsyncChatGPT().create(timeout=220)
				if chatgpt.session is None:
					await chatgpt.refresh_session()
				url = "https://chat.openai.com/backend-api/conversations"
				data = {
					"is_visible": False,
				}
				ok, json, response = await chatgpt._api_patch_request(url, data)
				if ok:
					pass
				else:
					chatgpt.log.error("Failed to delete conversations")
					chatgpt.rate = time.time() + 3600
				# resp = []
				# async for w in chatgpt.ask_stream(""):
				# 	resp.append(w)
				# s = "".join(resp)
				# print("ChatGPT init:", s)
				chatgpt.timestamp = time.time()
			print("ChatGPT prompt:", q)
			sys.stdout.flush()
			resp = []
			async for w in chatgpt.ask_stream(q):
				resp.append(w)
			res = "".join(resp).strip()
			if fut:
				fut.set_result(res)
			return res
		if hasattr(asyncio, "main_new_loop"):
			fut = concurrent.futures.Future()
			asyncio.main_new_loop.create_task(run_chatgpt(q, fut))
			res = fut.result(timeout=240)
		else:
			res = asyncio.run(run_chatgpt(q))
		if res:
			if not self.bl:
				print("ChatGPT response:", res)
			# if len(self.gpttokens(res)) > 512:
			# 	res = self.answer_summarise(q=res, max_length=500, min_length=256).strip()
			errs = (
				"Your ChatGPT session is not usable.",
				"Failed to read response from ChatGPT.",
				"Generation stopped",
			)
			err = any(res.startswith(s) for s in errs)
			if not err:
				return res
			else:
				res = ""
				chatgpt.timestamp = 0
		else:
			chatgpt.rate = time.time() + 3600
			chatgpt.timestamp = 0
		return res

	vis_c = vis_r = 0
	def vai(self, q):
		if not self.vis_s or self.vis_r > time.time():
			return ""
		if self.vis_c > 48:
			self.vis_r = max(self.vis_r + 86400, time.time())
			resp = requests.post(
				"https://app.visus.ai/t/kxzsjtzfxu/query/clfw3bcof01uqfbey053r4o93/clfw3bcoj01urfbey5czzjaji/?index=&_data=routes%2F_dashboard%2B%2Ft%2B%2F%24teamId%2B%2Fquery%2B%2F%24aiId.%24conversationId%2B%2Findex",
				data={"newName": "", "intent": "clear-convo"},
				headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8", "User-Agent": "Mozilla/5.1"},
				cookies={"__session": vis_s},
			)
			print(resp)
		print("Visus prompt:", q)
		rid = "-".join("".join(hex(random.randint(0, 15))[2:] for i in range(n)) for n in (8, 4, 4, 4, 12))
		resp = requests.post(
			"https://app.visus.ai/api/query",
			data=json.dumps({
				"aiId": "clfw3bcof01uqfbey053r4o93",
				"teamId": "clfw3bcnv01uffbeypnj1bmrx",
				"conversationId": "clfw3bcoj01urfbey5czzjaji",
				"userId": "google-oauth2|111998687181999014199",
				"focusedFiles": [],
				"rId": rid,
				"query": q,
			}),
			headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.1"},
			cookies={"__session": self.vis_s},
		)
		try:
			resp.raise_for_status()
			if not resp.content:
				raise EOFError
			data = resp.json()
			if not data.get("success"):
				raise ValueError(data)
		except:
			print_exc()
			self.vis_r = time.time() + 86400
			return ""
		return "\n".join(line.strip().removeprefix("<p>").removesuffix("</p>").strip() for line in data["response"].replace("<br>", "\n").splitlines()).replace("<em>", "*").replace("</em>", "*")

	you_r = 0
	def ycg(self, data, headers={}):
		if self.you_r > time.time():
			raise EOFError
		print("YourChat query:", data)
		headers["Content-Type"] = "text/plain"
		resp = self.session.post(
			"https://your-chat-gpt.vercel.app/api/openai-stream",
			data=json.dumps(data),
			headers=headers,
		)
		try:
			resp.raise_for_status()
			if not resp.content:
				raise EOFError
		except:
			print_exc()
			self.you_r = time.time() + 3600
			return ""
		return resp.text

	def ai(self, u, q, refs=(), im=None):
		tup = (u, q)
		if self.chat_history and (not self.summed or len(self.chat_history) + len(self.promises) > self.history_length):
			self.rerender()
		caids = ()
		uoai = None
		expapi = None
		# if self.premium > 0 or random.randint(0, 1):
		response, cost, uoai, expapi = self.gptcomplete(u, q, refs=refs)
		if response:
			return self.after(tup, (self.name, response)), cost, caids, uoai, expapi
		if refs and refs[-1][0] in ("IMAGE", "ANSWER"):
			if len(refs) > 1:
				response = refs[-2][1] + ", " + refs[-1][1]
			else:
				response = refs[-1][1]
			if response:
				return self.after(tup, (self.name, response)), 0, caids
		if self.premium > 0 and literal_question(q):
			response = (self.google, self.bing)[random.randint(0, 1)](q)
			if response:
				return self.after(tup, (self.name, response)), 0, caids
			googled = True
		else:
			googled = False
		response = reso = self.question_answer_analysis("microsoft/DialoGPT-large")
		a1 = response
		if not a1 or a1.lower() == q.lower() or vague(a1):
			response = ""
		elif (" " not in a1 or len(a1) < 12) and not a1[0].isnumeric() and a1[-1] not in ".!?)]":
			response = ""
		else:
			response = a1
		if not googled and not response:
			response = (self.google, self.bing)[random.randint(0, 1)](q)
			if response:
				return self.after(tup, (self.name, response)), 0, caids
		if not response:
			response = reso
		response = response.replace("  ", " ")
		if not response:
			response, cost, uoai, expapi = self.gptcomplete(u, q, refs=refs)
			if response:
				return self.after(tup, (self.name, response)), cost, caids, uoai, expapi
			response = "Sorry, I don't know."
		return self.after(tup, (self.name, response)), 0, caids

	def deletes(self, caids):
		self.chat_history = self.chat_history[:-2]

	ask = ai

	def append(self, tup):
		if not self.chat_history or tup != self.chat_history[-1]:
			k, v = tup
			if len(self.gpttokens(v)) > 36:
				v = self.answer_summarise(q=v, max_length=32, min_length=6).replace("\n", ". ").strip()
				tup = (k, v)
			self.chat_history.append(tup)
		return tup[-1]

	def appendleft(self, tup):
		if not self.chat_history or tup != self.chat_history[0]:
			k, v = tup
			if len(self.gpttokens(v)) > 36:
				v = self.answer_summarise(q=v, max_length=32, min_length=6).replace("\n", ". ").strip()
				tup = (k, v)
			self.chat_history.insert(0, tup)
		return tup[0]

	def _after(self, t1, t2):
		try:
			k, v = t2
			if self.premium > 1:
				labels = ("promise", "information", "example")
				resp = self.answer_classify(q=v, labels=labels)
			if len(self.gpttokens(v)) > 104:
				v = self.answer_summarise(q=v, max_length=96, min_length=8).replace("\n", ". ").strip()
				t2 = (k, v)
			k, v = t1
			if len(self.gpttokens(v)) > 52:
				v = self.answer_summarise(q=v, max_length=48, min_length=6).replace("\n", ". ").strip()
				t1 = (k, v)
			if self.premium > 1 and resp["promise"] >= 0.5:
				if len(self.promises) >= 6:
					self.promises = self.promises[2:]
				self.promises.append(t1)
				self.promises.append(t2)
				print("Promises:", self.promises)
			else:
				self.chat_history.append(t1)
				self.chat_history.append(t2)
		except:
			print_exc()

	def rerender(self):
		if len(self.chat_history) < 5:
			return
		fix = max(3, len(self.chat_history) - 3)
		chat_history = self.chat_history[:fix]
		self.chat_history = self.chat_history[fix:]
		summ_start = "Summary of prior conversation:\n"
		if chat_history and chat_history[0][1].startswith(summ_start):
			chat_history[0] = (chat_history[0][0], chat_history[0][1][len(summ_start):].strip())
		summ_next = "[SYSTEM]:"
		if chat_history and chat_history[0][1].startswith(summ_next):
			chat_history[0] = (chat_history[0][0], chat_history[0][1][len(summ_next):].strip())
		lines = []
		for k, v in self.promises:
			k = k.replace(":", "")
			s = f"{k}: {v}\n"
			lines.append(s)
		for k, v in chat_history:
			k = k.replace(":", "")
			s = f"{k}: {v}\n"
			lines.append(s)
		v = "".join(lines)
		lim = 240 if self.premium >= 2 else 80
		if len(self.gpttokens(v)) > lim + 16:
			v = self.answer_summarise(q=v, max_length=lim, min_length=64).strip()
		v = summ_start + v
		print("Chat summary:", v)
		self.summary = v
		self.chat_history.insert(0, ("[SYSTEM]", v))
		self.promises.clear()

	def after(self, t1, t2):
		exc.submit(self._after, t1, t2)
		self.timestamp = time.time()
		return t2[1]


if __name__ == "__main__":
	import sys
	token = sys.argv[1] if len(sys.argv) > 1 else ""
	bot = Bot(token)
	while True:
		print(bot.talk(input()))
