from flask import Flask, render_template

from glob import glob
import os
import sqlite3


os.chdir(os.path.dirname(__file__))
template_dir = os.path.join(os.getcwd(), "templates")
static_dir = os.path.join(os.getcwd(), "static")
#template_dir = "C:\\Users\\Cole\\Desktop\\Robotics\\Bionic Bulldogs website\\Flask\\templates"
#static_dir = "C:\\Users\\Cole\\Desktop\\Robotics\\Bionic Bulldogs website\\Flask\\static"
server = Flask(__name__, static_folder=static_dir, template_folder=template_dir, static_url_path="")
server.config["SEND_FILE_MAX_AGE_DEFAULT"] = 1


@server.after_request
def add_header(response):
	response.headers['Cache-Control'] = 'no-store'
	return response


def setup():
	members_conn = sqlite3.connect("data/members.db")
	members_cursor = members_conn.cursor()
	members_cursor.execute("CREATE TABLE IF NOT EXISTS current (name TEXT, bio TEXT, img TEXT, odr INTEGER UNIQUE)")
	members_conn.commit()
	members_conn.close()


@server.route("/")
@server.route("/home")
def home():
	with open(f"data/sponsors.data", "rt") as f:
		sponsors = [line.strip().split("\x1f") for line in f]
	return render_template("home.html", sponsors=sponsors)


#@server.route("/members", defaults={"year": "2019-2020"})
#@server.route("/members/{year}")
def members(year):
	conn = sqlite3.connect("data/members.db")
	cursor = conn.cursor()
	bios = cursor.execute("SELECT img, bio FROM current").fetchall()
	conn.close()
	res = render_template("members.html", bios=bios, ratio=66)
	with open("members_curr.html", "wt") as f:
		f.write(res)
	return res

@server.route("/members", defaults={"year": "2019-2020"})
@server.route("/members/{year}")
def members(year):
	with open(f"data/{year}.members", "rt") as f:
		bios = [line.strip().split("\x1f")[1:3] for line in f]
	res = render_template("members.html", bios=bios, ratio=66)
	return res


@server.route("/robot")
def robot():
	return render_template("robot.html")

@server.route("/outreach")
def outreach():
	return render_template("outreach.html")


@server.route("/404")
@server.errorhandler(404)
def page_not_found(e=None):
	if e is None:
		return render_template("404.html", title="404")
	return render_template("404.html", title="404"), 404


@server.route("/500")
@server.errorhandler(500)
def internal_error(e=None):
	if e is None:
		return render_template("500.html", title="500")
	return render_template("500.html", title="500"), 500


def run_server(port=5000):
	server.run(host="127.0.0.1", port=port, threaded=True)


def url_ok(url, port):
	from http.client import HTTPConnection
	try:
		conn = HTTPConnection(url, port)
		conn.request("GET", "/")
		r = conn.getresponse()
		return r.status == 200
	except:
		return False


def export():
	from time import sleep
	from threading import Thread
	import urllib.request
	t = Thread(target=run_server)
	t.daemon = True
	t.start()
	while not url_ok("127.0.0.1", 5000):
		sleep(0.1)
	with open("export/index.html", "wb") as f:
		f.write(urllib.request.urlopen("http://127.0.0.1:5050").read())
	with open("export/members.html", "wb") as f:
		f.write(urllib.request.urlopen("http://127.0.0.1:5050/members").read())
	with open("export/404.html", "wb") as f:
		f.write(urllib.request.urlopen("http://127.0.0.1:5050/404").read())
	with open("export/500.html", "wb") as f:
		f.write(urllib.request.urlopen("http://127.0.0.1:5050/500").read())


if __name__ == "__main__":
	#setup()
	server.run(host="0.0.0.0", port=5000)
