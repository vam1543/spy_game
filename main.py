from flask import Flask, render_template, request
import time
import random

GAME_LIFETIME = 86400
MIN_GAMERS = 3
MAX_GAMERS = 20
LOCATIONS_FILE = "locations.txt"
GAME_URL = "http://localhost:15430/add_player?gameid="
# GAME_URL = "http://84.201.162.208:15430/add_player?gameid="


app = Flask(__name__)
random.seed()

games = {}

@app.route('/')
def main_page():
	return render_template('main_page.html')

@app.route('/newgame')
def newgame():
	return render_template('newgame.html')


@app.route('/subscribe_game')
def subscribegame():
	return render_template('subscribe_game.html')


def clear_games():
	global games
	curtime = time.time()
	clearlist = []
	for game_id in games.keys():
		if games[game_id]["createtime"] < curtime - GAME_LIFETIME:
			clearlist.append(game_id)
			
	for game_id in clearlist:
		del games[game_id]


def load_std_locations():
	with open(LOCATIONS_FILE, encoding="utf-8") as fin:
		locations = []
		words = fin.read().split("\n")
		for cur_loc in words:
			cur_loc = cur_loc.strip()
			if cur_loc:
				locations.append(cur_loc)
	return locations
		
def create_game(gamers, locations, use_std):
	global games
	curid = 1
	while curid in games.keys():
		curid += 1

	curkey = str(curid) + str(random.randrange(10)) + str(random.randrange(10))

	games[curid] = {
		"key": curkey,
		"gamers": gamers,
		"locations": locations,
		"use_std_locations": use_std,
		"loc": locations[random.randrange(len(locations))],
		"spy": random.randrange(1, gamers + 1),
		"curcount": 0,
		"createtime": time.time(),
	} 

	return curkey



@app.route('/newgame_create', methods=["POST"])
def newgame_create():
	global games
	clear_games()
	try:
		gamers = int(request.form.get("count", ""))
		if gamers < MIN_GAMERS or gamers > MAX_GAMERS:
			raise Exception("Wrong count of gamers")
	except Exception:
		return render_template("error_go_main.html", error_text = "")

	words_form = request.form.get("words", "")
	locations = []
	words_form = words_form.split("\n")
	for cur_loc in words_form:
		cur_loc = cur_loc.strip()
		if cur_loc:
			locations.append(cur_loc)
	if len(locations) < 3:
		locations = load_std_locations()
		used_std = True
	else:
		used_std = False

	game_key = create_game(gamers, locations, used_std)
	game_url = GAME_URL + game_key
	used_std_str = "да" if used_std else "нет"

	return render_template('newgame_create.html', gamers=gamers, used_std=used_std_str, game_key=game_key, game_url=game_url)


@app.route('/add_player')
def add_player():
	global games
	try:
		game_key = request.args.get("gameid", "")
		game_id = int(game_key) // 100
	except Exception:
		return render_template("error_go_main.html", error_text = "Не указан или указан некорректный номер игры")


	if game_id not in games.keys():
		return render_template("error_go_main.html", error_text = "Указан несуществующий номер игры")
	if games[game_id]["key"] != game_key:
		return render_template("error_go_main.html", error_text = "Указан несуществующий номер игры")

	if games[game_id]["curcount"] == games[game_id]["gamers"]:
		return render_template("error_go_main.html", error_text = "В эту игру уже зашли все игроки")

	games[game_id]["curcount"] += 1
	curnom = games[game_id]["curcount"]

	if curnom != games[game_id]["spy"]:
		curtext1 = "Вы в локации"
		curtext2 = games[game_id]["loc"]
		curcolor="green"
	else:
		curtext1 = "Вы"
		curtext2 = "шпион"
		curcolor = "red"

	return render_template('add_player.html', gamers=games[game_id]["gamers"], curnom=curnom, curtext1=curtext1, curtext2=curtext2, curcolor=curcolor, 
			locs=games[game_id]["locations"], game_key=game_key, game_url=GAME_URL+game_key)


if __name__ == '__main__':
	app.run(host="::", port=15430, debug=True)