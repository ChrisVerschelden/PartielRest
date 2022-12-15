from flask import Flask, jsonify, abort, request
import mariadb
import urllib.parse

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False  # pour utiliser l'UTF-8 plutot que l'unicode


def execute_query(query, data=()):
    config = {
        'host': 'mariadb',
        'port': 3306,
        'user': 'root',
        'password': 'root',
        'database': 'chariots'
    }
    """Execute une requete SQL avec les param associés"""
    # connection for MariaDB
    conn = mariadb.connect(**config)
    # create a connection cursor
    cur = conn.cursor()
    # execute a SQL statement
    cur.execute(query, data)

    if cur.description:
        # serialize results into JSON
        row_headers = [x[0] for x in cur.description]
        rv = cur.fetchall()
        list_result = []
        for result in rv:
            list_result.append(dict(zip(row_headers, result)))
        return list_result
    else:
        conn.commit()
        return cur.lastrowid


####### groupes #######
#########################

##### GETS

@app.route('/groupes')
def get_groupes():
    """recupère la liste des groupes"""
    groupes = execute_query("select nom from groupes")
    # ajout de _links à chaque dico région
    if groupes == []:
        abort(404, "Aucun groupes dans cette base")

    for i in range(len(groupes)):
        groupes[i]["_links"] = [
            {
                "href": "/groupes/" + urllib.parse.quote(groupes[i]["nom"]),
                "rel": "self"
            },
            {
                "href": "/groupes/" + urllib.parse.quote(groupes[i]["nom"]) + "/concerts",
                "rel": "concerts"
            }
        ]
    return jsonify(groupes), 200


@app.route('/groupes/<string:nom>')
def get_groupe(nom: str):
    """recupère le détail d'un groupe"""
    groupe = execute_query("select nom from groupes where nom=?", (nom,))
    # ajout de _links à l'groupe
    groupe[0]["_links"] = [
        {
            "href": "/groupes/" + urllib.parse.quote(groupe[0]["nom"]),
            "rel": "self"
        },
        {
            "href": "/groupes/" + urllib.parse.quote(groupe[0]["nom"]) + "/concerts",
            "rel": "concerts"
        }
    ]
    return jsonify(groupe), 200


@app.route('/groupes/<string:nom>/concerts')
def get_concerts_for_groupe(nom: str):
    """Récupère les concerts d'un groupe"""
    concerts = execute_query("""select concerts.nom, groupes.nom as nom_groupe
                                    from concerts
                                    join groupes on concerts.groupe_id = groupes.id
                                    where lower(groupes.nom) = ?""", (urllib.parse.unquote(nom.lower()),))
    if concerts == []:
        abort(404, "Aucune concert pour cet groupes")
    # ajout de _links à chaque dico concert
    for i in range(len(concerts)):
        concerts[i]["_links"] = [{
            "href": "/concerts/" + concerts[i]["nom"],
            "rel": "self"
        },{
            "href": "/concerts/" + concerts[i]["nom"] + "/tickets",
            "rel": "tickets"
        }]
    return jsonify(concerts), 200

##### POSTS

@app.route('/groupes', methods=['POST'])
def post_groupe():
    """"Ajoute un groupe"""
    nom = request.args.get("nom")
    execute_query("insert into groupes (nom) values (?)", (nom,))
    # on renvoi le lien de l'groupe que l'on vient de créer
    reponse_json = jsonify({
        "_links": [{
            "href": "/groupes/" + urllib.parse.quote(nom),
            "rel": "self"
        }]
    })
    return reponse_json, 201  # created


@app.route('/groupes/<string:nom_groupe>/concerts', methods=['POST'])
def post_concert_for_groupe(nom_groupe):
    """créé une concert"""
    nom_concert = request.args.get("nom")
    date_concert = request.args.get("date")
    execute_query("insert into concerts (nom, date, groupe_id) values (?, ?, (select id from groupes where nom = ?))", (nom_concert,date_concert, nom_groupe))
    # on renvoi le lien du département  que l'on vient de créer
    reponse_json = jsonify({
        "_links": [{
            "href": "/concerts/" + nom_concert,
            "rel": "self"
        }]
    })
    return reponse_json, 201  # created

##### PUTS

@app.route('/groupes/<string:nom>', methods=['PUT'])
def put_groupe(nom: str):
    """"modifie un groupes"""
    new_nom = request.args.get("nom")
    execute_query("update groupes set nom=? where nom=?", (new_nom,nom))
    # on renvoi le lien de l'groupe que l'on vient de créer
    reponse_json = jsonify({
        "_links": [{
            "href": "/groupes/" + urllib.parse.quote(new_nom),
            "rel": "self"
        }]
    })
    return reponse_json, 201  # created

##### DELETES

@app.route('/groupes/<string:nom>', methods=['DELETE'])
def delete_groupe(nom: str):
    """"supprime un groupes"""
    execute_query("delete from groupes where nom=?", (nom,))
    # on renvoi le lien de l'groupe que l'on vient de créer
    return "", 204  # no data


####### concerts #######
#########################

@app.route('/concerts')
def get_concerts():
    """recupère la liste des concerts"""
    concerts = execute_query("select nom from concerts")
    # ajout de _links à chaque dico région
    if concerts == []:
        abort(404, "Aucune concert dans cette base")

    for i in range(len(concerts)):
        concerts[i]["_links"] = [
            {
                "href": "/concerts/" + urllib.parse.quote(concerts[i]["nom"]),
                "rel": "self"
            }
        ]
    return jsonify(concerts), 200


@app.route('/concerts/<string:nom>')
def get_concert(nom: str):
    """recupère un concert spécifique"""
    concert = execute_query("select nom, date from concerts where nom=?", (nom,))
    # ajout de _links à l'concert
    concert[0]["_links"] = [{
            "href": "/concerts/" + urllib.parse.quote(concert[0]["nom"]) + "/tickets",
            "rel": "tickets"
        }
    ]
    return jsonify(concert), 200


@app.route('/concerts/<string:nom>/tickets')
 #localhost:5000/concerts/GodzillaTour/tickets
def get_tickets_for_concert(nom: str):
    """Récupère les tickets d'un concert"""
    var_requete = """select concerts.nom, tickets.place, tickets.price
                                from tickets
                                join concerts on concert_id = concerts.id
                                where lower(concerts.nom)=?"""
    tickets = execute_query("""select concerts.nom, tickets.place, tickets.price
                                from tickets
                                right join concerts on concert_id = concerts.id
                                where concerts.nom=?""", (nom,))
    
    if tickets == []:
        abort(404, var_requete)#"Aucun ticket pour ce concert")
    # ajout de _links à chaque dico ticket
    for i in range(len(tickets)):
        tickets[i]["_links"] = [{
            "href": "/concerts/" + urllib.parse.unquote(nom.lower()) + "/" + tickets[i]["nom"],
            "rel": "self"
        },{
            "href": "/concerts/" + urllib.parse.unquote(nom.lower()) + "/tickets/" + tickets[i]["place"],
            "rel": "ticket"
        }]
    return jsonify(tickets), 200

@app.route('/concerts/<string:nom>/tickets/<string:place>')
def get_ticket_for_concert(nom: str, place: str):
    """Récupère un tickets d'un concert"""
    tickets = execute_query("""select tickets.id
                                from tickets
                                join concerts on concert_id = concerts.id
                                where nom = ? and place=""", (urllib.parse.unquote(nom.lower()),urllib.parse.unquote(place.lower())))
    if tickets == []:
        abort(404, "Aucun ticket pour ce concert")
    # ajout de _links à chaque dico mail
    for i in range(len(tickets)):
        tickets[i]["_links"] = [{
            "href": "/concerts/" + urllib.parse.unquote(nom.lower()) + "/" + tickets[i]["nom"],
            "rel": "self"
        }]
    return jsonify(tickets), 200


#### POSTS 

@app.route('/concerts/<string:nom_concerts>/tickets', methods=['POST'])
def post_ticket_for_concerts(nom_concerts):
    """créé un mail dans une concert"""
    price_concert = request.args.get("title")
    place_concert = request.args.get("message")
    execute_query("insert into tickets (place, price, concert_id) values (?,?, (select id from concerts where lower(nom) = ?))", (title_concert, message_concert, from_concert, nom_concerts.lower()))
    # on renvoi le lien du département  que l'on vient de créer
    reponse_json = jsonify({
        "_links": [{
            "href": "/concerts/" + nom_concert,
            "rel": "self"
        }]
    })
    return reponse_json, 201  # created


##### DELETES

@app.route('/concerts/<string:nom>', methods=['DELETE'])
def delete_concert(nom: str):
    """"supprime un concerts"""
    execute_query("delete from concerts where nom=?", (nom,))
    # on renvoi le lien de l'groupe que l'on vient de créer
    return "", 204  # no data


####### tickets #######
#########################

@app.route('/tickets')
def get_tickets():
    """recupère la liste des tickets"""
    tickets = execute_query("select * from tickets")
    # ajout de _links à chaque dico région
    if tickets == []:
        abort(404, "Aucune ticket dans cette base")

    for i in range(len(tickets)):
        tickets[i]["_links"] = [
            {
                "href": "/tickets/" + str(tickets[i]["id"]),
                "rel": "self"
            }
        ]
    return jsonify(tickets), 200


#### PUTS ####

##### PUTS

@app.route('/tickets/<string:id>', methods=['PUT'])
def put_ticket(id: str):
    """"modifie un groupes"""
    new_available = request.args.get("available")
    execute_query("update tickets set available=? where id=?", (new_available,id))
    # on renvoi le lien de l'groupe que l'on vient de créer
    reponse_json = jsonify({
        "_links": [{
            "href": "/tickets/" + id,
            "rel": "self"
        }]
    })
    return reponse_json, 201  # created


##### DELETES

@app.route('/tickets/<string:id>', methods=['DELETE'])
def delete_ticket(id: str):
    """"supprime un tickets"""
    execute_query("delete from tickets where id=?", (id,))
    return "", 204  # no data


# we define the route /
@app.route('/')
def welcome():
    liens = [{}]
    liens[0]["_links"] = [{
        "href": "/groupes",
        "rel": "groupes"
    },{
        "href": "/concerts",
        "rel": "concerts"
    },{
        "href": "/tickets",
        "rel": "tickets"
    }]
    return jsonify(liens), 200

if __name__ == '__main__':
    # define the localhost ip and the port that is going to be used
    app.run(host='0.0.0.0', port=5000)
