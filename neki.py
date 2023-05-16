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
#proba za zaposlene 
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





######################################################################
# Glavni program


# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)

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


@post('/prijava/')
def prijava_post():
    uporabnisko_ime = request.forms.get('Uporabnisko_ime')
    geslo = request.forms.get('Geslo')
    if uporabnisko_ime is None or geslo is None:
        redirect(url('prijava_get'))
        return
    oseba = cur   
    hashBaza = None
    try: 
        hashBaza = cur.execute("SELECT geslo FROM oseba WHERE uporabnisko_ime = %s", (uporabnisko_ime, ))
        hashBaza = cur.fetchone()
        hashBaza = hashBaza[0]
    except:
        hashBaza = None
    if hashBaza is None:
        return template('login.html',   napaka2="Uporabniško ime ali geslo nista ustrezni")
    if hashGesla(geslo) != hashBaza:
        return template('login.html',   napaka2="Uporabniško ime ali geslo nista ustrezni")
    redirect(url('prijava_post'))


@get('/odjava')
def odjava():
    """
    Odjavi uporabnika iz aplikacije. Pobriše piškotke o uporabniku in njegovi roli.
    """
    
    response.delete_cookie("uporabnik")
    response.delete_cookie("rola")
    
    return template('prijava.html', napaka=None)

#to dostopata samo admin in vodje, treba dat piškotk še
@get('/dodaj_izdelek')
def dodaj_izdelek():

   
    # vrnemo template za dodajanje izdelka
    return template('dodaj_izdelek.html')

@post('/dodaj_izdelek')
def dodaj_izdelek_post():

    id_produkt = int(request.forms.get('id_produkt'))
    prodajna_cena = int(request.forms.get('prodajna_cena'))
    nabavna_cena = int(request.forms.get('nabavna_cena'))
    ime_produkt = str(request.forms.get('ime_produkt'))


#KODE ZA KOŠARICO, SEZNAM KUPLJENIH STVARI...