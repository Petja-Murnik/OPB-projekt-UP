#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottleext import get, post, run, request, template, redirect, static_file, url

# uvozimo ustrezne podatke za povezavo
import uvoz.auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import os
import hashlib

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

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




######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

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
    ime = request.forms.ime
    priimek = request.forms.priimek
    naslov = request.forms.naslov
    mesto = request.forms.mesto
    drzava = request.forms.mesto
    TRR = request.forms.TRR
    email = request.forms.email
    uporabnisko_ime = request.forms.uporabnisko_ime
    geslo = request.forms.geslo
    geslo2 = request.forms.geslo2

@get('/prijava/')
def prijava_get():
    napaka2 = None
    return template('login.html', napaka2=napaka2)

@post('/prijava/')
def prijava_post():
    uporabnisko_ime = request.forms.uporabnisko_ime
    geslo = request.forms.geslo
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
    response.set_cookie('uporabnisko_ime', uporabnisko_ime, secret=skrivnost)
    redirect(url('zacetna'))


#odjava
#@get('/odjava/')
#def odjava_get():
#    response.delete_cookie('uporabnisko_ime')
#    redirect(url('index'))


#KODE ZA KOŠARICO, SEZNAM KUPLJENIH STVARI...