#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottleext import get, post, run, request, template, redirect, static_file, url

# uvozimo ustrezne podatke za povezavo
from uvoz import auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import os
import hashlib

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)
# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)



#za debugiranje
#debuger(True)

@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')

@get("/")
def index():
    return template('zacetna.html', osebe = cur)

###################
@get("/zaposleni/")
def zaposleni_get():
    cur.execute("SELECT * FROM zaposleni")
    return template("zaposleni.html",  zaposlene=cur)

@get("/dodaj_zaposlenega")
def dodaj_zaposlenega_get():
    return template("dodaj_zaposlenega.html",
                    ime = "",priimek = '',mesto = '',naslov = '',trr = "", uporabnisko_ime ='', geslo ='', placa = '', st_ur = '', vloga = '', oddelek ='',napaka= None)

@post('/dodaj_zaposlenega')
def dodaj_zaposlenega_post():
    if False:
        "ti sment ne smes redirect"
    else:
        ime = request.forms.get('Ime')
        priimek = request.forms.get('Priimek')
        mesto = request.forms.get('Mesto')
        naslov = request.forms.get('Naslov')
        trr = request.forms.get('TRR')
        uporabnisko_ime = request.forms.get('Uporabnisko_ime')
        geslo = request.forms.get('Geslo')
        placa = request.forms.get('Placa')
        st_ur = request.forms.get('Stevilo_ur')
        vloga = request.forms.get('Vloga')
        oddelek = request.forms.get('Oddelek')
    try: 
        cur.execute("""INSERT INTO zaposleni 
            (ime, priimek, mesto, naslov,TRR,uporabnisko_ime,
             geslo, placa,stevilo_ur) 
            VALUES(%s, %s,%s,%s,%s,%s,%s,%s,%s )""",
            (ime, priimek, mesto, naslov,trr,uporabnisko_ime,
             geslo, placa,st_ur))
        cur.execute("""INSERT INTO vloge
            VALUES(%s,%s,%s);""",(trr, vloga,oddelek))
        conn.commit()
    except Exception as ex:
        conn.rollback()
        return template('dodaj_zaposlenega.html',ime = "",priimek = '',mesto = '',naslov = '',trr = '',
                         uporabnisko_ime ='', geslo ='', placa = '', st_ur = '', vloga = '', oddelek ='',napaka= 'Zgodila se je napaka: %s' % ex)
    redirect(url("zaposleni_get"))

@get("/place/")
#@cookie required ?
def place():
    if False:
        "TI baraba nesmes!"
    else:
        cur.execute("""
            DROP VIEW IF EXISTS ime_priimek_placa;""")
        conn.commit()
        cur.execute("""
            CREATE VIEW ime_priimek_placa AS 
            SELECT ime || ' ' || priimek AS ime_priimek, placa 
            FROM zaposleni;
            SELECT * FROM ime_priimek_placa;
            """)
        conn.commit()
        results = cur.fetchall()
        print("Number of rows fetched:", len(results))
        print("Fetched rows:", results)
    return template("place.html",place = results)

@get("/spremeni_placo")
#cookie required ?
def spremeni_placo_get():
    return template("spremeni_placo.html", trr = "",nova_placa = "", napaka= None)


@post("/spremeni_placo")
#@cookie required ? 
def spremeni_placo_post():
    if False:
        "TI sment pa tega ne smes"
    else:
        trr = request.forms.get("TRR")
        nova_placa = request.forms.get("Nova placa")
    try:
        cur.execute("""UPDATE zaposleni
            SET placa = %s
            WHERE trr = %s;
            """,(nova_placa, trr))
        conn.commit()
    except Exception as ex:
        conn.rollback()
        return template("spremeni_placo.html", trr = "",nova_placa = "", napaka= 'Zgodila se je napaka: %s' % ex)
    return(url("place"))
        




######################################################################
# Glavni program




#OSNUTEK KODE ZA PRIJAVO IN REGISTRACIJO
def hashGesla(s):
    m = hashlib.sha256()
    m.update(s.encode("utf-8"))
    return m.hexdigest()


@get('/registracija/')
def registracija_get():
    napaka = None
    return template('register.html', napaka=napaka)

@post('/registracija/')
def registracija_post():
    ime = request.forms.get('Ime')
    priimek = request.forms.get('Priimek')
    mesto = request.forms.get('Mesto')
    naslov = request.forms.get('Naslov')
    trr = request.forms.get('TRR')
    uporabnisko_ime = request.forms.get('Uporabnisko_ime')
    geslo = request.forms.get('Geslo')
    placa = request.forms.get('Placa')
    st_ur = request.forms.get('Stevilo_ur')
    vloga = request.forms.get('Vloga')
    oddelek = request.forms.get('Oddelek')

@get("/petja/")
def petja_get():
    return "šalal"

@get('/prijava/') 
def prijava_get():
    return template("login.html", uporabnisko_ime = "", geslo = "",napaka2  = None)

@post('/prijava/')
def prijava_post():
    uporabnisko_ime = request.forms.get('Uporabnisko_ime')
    geslo = request.forms.get('Geslo')
    if uporabnisko_ime is None or geslo is None:
        redirect(url('prijava_get'))      
    oseba = cur   
    hashBaza = None
    try: 
        hashBaza = cur.execute("SELECT geslo FROM kupci WHERE uporabnisko_ime = %s", [uporabnisko_ime])
        hashBaza = cur.fetchone()
        hashBaza = hashBaza[0]
        print("AA")
    except:
        hashBaza = None 
        print("BBB")
    if hashBaza is None:
        return print("prisel si sem")#template('login.html',   napaka2="Uporabniško ime ali geslo nista ustrezni")
    if hashGesla(geslo) != hashBaza:
        return print("sedaj si pa tu")#template('login.html',   napaka2="Uporabniško ime ali geslo nista ustrezni")
    redirect(url('zaposleni')) #pri zgornjem redirectu je treba sam napisat kam naj se da


@get('/odjava')
def odjava():
    """
    Odjavi uporabnika iz aplikacije. Pobriše piškotke o uporabniku in njegovi roli.
    """
    
    response.delete_cookie("uporabnik")
    response.delete_cookie("rola")
    
    return template('prijava.html', napaka=None)

#to dostopata samo admin in vodje, treba dat piškotk še
@get("/produkti/")
def produkti_get():
    cur.execute("SELECT * from produkti")
    return template("produkti.html", produkti=cur)

@get("/dodaj_produkt")
def dodaj_produkt_get():
    return template("dodaj_produkt.html",
                    id_produkt = "",prodajna_cena = '',nabavna_cena = '',ime_produkt = '', napaka= None)

@post('/dodaj_produkt')
def dodaj_produkt_post():
    if False:
        "pri produktih je nekaj narobe"
    else:
        id_produkt = int(request.forms.get('id_produkt'))
        prodajna_cena = int(request.forms.get('prodajna_cena'))
        nabavna_cena = int(request.forms.get('nabavna_cena'))
        ime_produkt = str(request.forms.get('ime_produkt'))
    try: 
        cur.execute("""INSERT INTO produkti 
            (id_produkt, prodajna_cena, nabavna_cena, ime_produkt) 
            VALUES(%s, %s, %s, %s)""",
            (id_produkt, prodajna_cena, nabavna_cena, ime_produkt))
        conn.commit()
    except Exception as ex:
        conn.rollback()
        return template('dodaj_produkt.html',id_produkt = "",prodajna_cena = '',nabavna_cena = '',ime_produkt = '', napaka= 'Zgodila se je napaka: %s' % ex)
    redirect(url("produkti_get"))



#KODE ZA KOŠARICO, SEZNAM KUPLJENIH STVARI...






#TO MORE BITI TUKAJ SPODAJ KODO PIŠI VIŠJE !!!
# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)