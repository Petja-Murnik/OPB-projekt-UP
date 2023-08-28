#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottleext import get, post, run, request, template, redirect, static_file, url
from bottle import response

#za cookieje
from functools import wraps
# uvozimo ustrezne podatke za povezavo
from uvoz import auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import os
import hashlib
import json
import pickle
from datetime import date

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)
# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

#za debugiranje
import logging

#za debugiranje
#debug(True)
#za hashiranje gesel
def password_hash(s):
    """Vrni SHA-512 hash danega UTF-8 niza. Gesla vedno spravimo v bazo
       kodirana s to funkcijo."""
    h = hashlib.sha512()
    h.update(s.encode('utf-8'))
    return h.hexdigest()


#POMOŽNA KODA ZA COOKIE##################################################
def cookie_required_kupec(f):
    """
    Dekorator, ki zahteva veljaven piškotek. Če piškotka ni, uporabnika preusmeri na stran za prijavo.
    """
    @wraps(f)
    def decorated( *args, **kwargs):
        cookie = request.get_cookie("uporabnisko_ime")
        if cookie:
            return f(*args, **kwargs)
        return template("login.html")

    
        
        
    return decorated

def cookie_required_zaposlen_uporabnisko_ime(f):
    """
    Dekorator, ki zahteva veljaven piškotek. Če piškotka ni, uporabnika preusmeri na stran za .
    """
    @wraps(f)
    def decorated( *args, **kwargs):
        cookie = request.get_cookie("uporabnisko_ime")
        if cookie:
            return f(*args, **kwargs)
        return template("prijava_zaposleni.html",uporabnisko_ime = "", geslo = "",napaka2  = None)

    
        
        
    return decorated

def cookie_required_zaposlen_vloga(f):
    """
    Dekorator, ki zahteva veljaven piškotek. Če piškotka ni, uporabnika preusmeri na stran za prijavo.
    """
    @wraps(f)
    def decorated( *args, **kwargs):
        cookie = request.get_cookie("vloga")
        if cookie:
            return f(*args, **kwargs)
        return template("prijava_zaposleni.html",uporabnisko_ime = "", geslo = "",napaka2  = None)

    
        
        
    return decorated

#######################################################################################################KONEC COOKIE


@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')

@get("/")
def index():
    return template('zacetna.html', osebe = cur)

##################ZAPOSLENI
@get("/zacetna_zaposleni/")
@cookie_required_zaposlen_uporabnisko_ime
@cookie_required_zaposlen_vloga
def zacetna_zaposleni_get():
    vlogica= request.get_cookie("vloga")
    return template("zacetna_zaposleni.html" , v = vlogica)


@get("/zaposleni/")
@cookie_required_zaposlen_uporabnisko_ime
@cookie_required_zaposlen_vloga
def zaposleni_get():
    vlogica= request.get_cookie("vloga")
    uporabniski_imencek = request.get_cookie("uporabnisko_ime")
    if vlogica == "delavec":
        return template("nimas_dovoljenja.html")
    else:    
        cur.execute("SELECT * FROM zaposleni")
        print(vlogica)
        return template("zaposleni.html",  zaposlene=cur,v=vlogica,u = uporabniski_imencek )



@get("/dodaj_zaposlenega")
@cookie_required_zaposlen_uporabnisko_ime
@cookie_required_zaposlen_vloga
def dodaj_zaposlenega_get():
    return template("dodaj_zaposlenega.html",
                    ime = "",priimek = '',mesto = '',naslov = '',trr = "", uporabnisko_ime ='', geslo ='', placa = '', st_ur = '', vloga = '', oddelek ='',napaka= None)

@post('/dodaj_zaposlenega')
@cookie_required_zaposlen_uporabnisko_ime
@cookie_required_zaposlen_vloga
def dodaj_zaposlenega_post():
    vlogica= request.get_cookie("vloga")
    uporabniski_imencek = request.get_cookie("uporabnisko_ime")
    if vlogica == "delavec" or vlogica =="vodja izmene":
        return template("nimas_dovoljenja.html")
    else:
        ime = request.forms.getunicode('Ime')
        priimek = request.forms.getunicode('Priimek')
        mesto = request.forms.getunicode('Mesto')
        naslov = request.forms.getunicode('Naslov')
        trr = request.forms.getunicode('TRR')
        uporabnisko_ime = request.forms.getunicode('Uporabnisko_ime')
        geslo = request.forms.getunicode('Geslo')
        placa = request.forms.getunicode('Placa')
        st_ur = request.forms.getunicode('Stevilo_ur')
        vloga = request.forms.getunicode('Vloga')
        oddelek = request.forms.getunicode('Oddelek')
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

@get("/uredi_zaposlenega/<trr>")
@cookie_required_zaposlen_uporabnisko_ime
@cookie_required_zaposlen_vloga
def uredi_zaposlenega_get(trr):
    vlogica= request.get_cookie("vloga")
    uporabniski_imencek = request.get_cookie("uporabnisko_ime")
    if vlogica == "delavec" or vlogica =="vodja izmene":
        return template("nimas_dovoljenja.html")
    else:
        try: 
            # Preverimo, ali zaposleni s podanim imenom že obstaja
            cur.execute("SELECT * FROM zaposleni WHERE trr = %s", (trr,))
            zaposleni = cur.fetchone()
            cur.execute("SELECT * FROM vloge WHERE trr = %s", (trr,))
            vlogica =cur.fetchone()
            if zaposleni:
                # Zaposleni s podanim imenom obstaja, izvedemo posodobitev
                # Pripravimo podatke za prikaz v obrazcu za urejanje
                ime = zaposleni[0]
                uporabnisko_ime = zaposleni[5] 
                priimek = zaposleni[1]
                mesto = zaposleni[3]
                naslov = zaposleni[2]
                geslo = zaposleni[6]
                placa = zaposleni[7]
                st_ur = zaposleni[8]
                vloga = vlogica[1]
                id_oddelek =vlogica[2]
                # Lahko prav tako preberemo podatke iz tabele vloge, če je to potrebno
                # cur.execute("SELECT * FROM vloge WHERE TRR = %s", (trr,))
                # vloge = cur.fetchone()
                # vloga = vloge[1]
                # oddelek = vloge[2]

                # Prikazujemo obrazec za urejanje z že obstoječimi podatki
                return template("uredi_zaposlenega.html", ime=ime, priimek=priimek, mesto=mesto,
                                naslov=naslov, trr=trr, uporabnisko_ime=uporabnisko_ime, geslo=geslo, placa=placa,
                                st_ur=st_ur, vloga=vloga, oddelek=id_oddelek)
            else:
                # Zaposleni s podanim imenom ne obstaja, vrnejo lahko ustrezno sporočilo ali preusmerijo na drugo stran
                return "Zaposleni s tem imenom ne obstaja."
        except Exception as ex:
            print(ex)
            return "Zgodila se je napaka: %s" % ex

@post("/uredi_zaposlenega/<trr>")
@cookie_required_zaposlen_uporabnisko_ime
@cookie_required_zaposlen_vloga
def uredi_zaposlenega_post(trr):
    vlogica= request.get_cookie("vloga")
    uporabniski_imencek = request.get_cookie("uporabnisko_ime")
    if vlogica == "delavec" or vlogica =="vodja izmene":
        return template("nimas_dovoljenja.html")
    else:
        try:
            # Preberemo vse podatke iz POST zahteve
            ime = request.forms.getunicode('Ime')
            priimek = request.forms.getunicode('Priimek')
            mesto = request.forms.getunicode('Mesto')
            naslov = request.forms.getunicode('Naslov')
            uporabnisko_ime = request.forms.getunicode('Uporabnisko_ime')
            geslo = request.forms.getunicode('Geslo')
            placa = request.forms.getunicode('Placa')
            st_ur = request.forms.getunicode('Stevilo_ur')
            vloga = request.forms.getunicode('Vloga')
            oddelek = request.forms.getunicode('Oddelek')


            # Izvedemo SQL poizvedbo za posodobitev podatkov o zaposlenem, če je kaj spremenjeno
            cur.execute("""UPDATE zaposleni SET
                ime = %s, priimek = %s, mesto = %s, naslov = %s,
                uporabnisko_ime = %s, geslo = %s, placa = %s,
                stevilo_ur = %s WHERE trr = %s""",
                (ime, priimek, mesto, naslov, uporabnisko_ime,
                geslo, placa, st_ur, trr))

            # Preverimo, ali obstaja vnos za ta zaposleni v tabeli "vloge"
            cur.execute("SELECT * FROM vloge WHERE trr = %s", (trr,))
            vloga_obstaja = cur.fetchone()

            if vloga_obstaja:
                # Zaposleni ima že vnos v tabeli "vloge", izvedemo posodobitev
                cur.execute("""UPDATE vloge SET vloga = %s, id_oddelek = %s WHERE trr = %s""",
                            (vloga, oddelek, trr))
            else:
                # Zaposleni še nima vnosa v tabeli "vloge", izvedemo vstavljanje novega vnosa
                cur.execute("""INSERT INTO vloge (trr, vloga, id_oddelek) 
                                VALUES (%s, %s, %s)""",
                            (trr, vloga, oddelek))

            conn.commit()        
        except Exception as ex:
            conn.rollback()
            logging.exception("Napaka pri urejanju zaposlenega:")
            return "Zgodila se je napaka: %s" % ex
        redirect(url("zaposleni_get"))






@get("/place/")
@cookie_required_zaposlen_uporabnisko_ime
@cookie_required_zaposlen_vloga
def place():
    if False:
        "TI baraba nesmes!"
    else:
        cur.execute("""
            SELECT * FROM ime_priimek_placa;
            """)
        conn.commit()
        results = cur.fetchall()
        print("Number of rows fetched:", len(results))
        print("Fetched rows:", results)
    return template("place.html",place = results)

# @get("/spremeni_placo")
# @cookie_required_zaposlen_uporabnisko_ime
# @cookie_required_zaposlen_vloga
# def spremeni_placo_get():
#     return template("spremeni_placo.html", trr = "",nova_placa = "", napaka= None)


# @post("/spremeni_placo")
# @cookie_required_zaposlen_uporabnisko_ime
# @cookie_required_zaposlen_vloga 
# def spremeni_placo_post():
#     moja_vloga= request.get_cookie("vloga")
#     if moja_vloga == "delavec":
#         print("TI pa ne smes HAHA")
#     else:
#         print(moja_vloga)
#         trr = request.forms.getunicode("TRR")
#         nova_placa = request.forms.getunicode("Nova placa")
#     try:
#         cur.execute("""UPDATE zaposleni
#             SET placa = %s
#             WHERE trr = %s;
#             """,(nova_placa, trr))
#         conn.commit()
#     except Exception as ex:
#         conn.rollback()
#         return template("spremeni_placo.html", trr = "",nova_placa = "", napaka= 'Zgodila se je napaka: %s' % ex)
#     return(url("place"))
        




######################################################################
# Glavni program





def hashGesla(s):
    m = hashlib.sha256()
    m.update(s.encode("utf-8"))
    return m.hexdigest()






########################################################### PRODUKTI
@get("/produkti/")
@cookie_required_zaposlen_uporabnisko_ime
def produkti():
    uporabniski_imencek = request.get_cookie("uporabnisko_ime")
    vlogica = request.get_cookie("vloga")
    cur.execute("SELECT * from produkti")
    return template("produkti.html", produkti=cur)

@get("/prodani_produkti/")
@cookie_required_zaposlen_uporabnisko_ime
def produkti_prodani_get():
    cur.execute("SELECT * from prodani_produkti")
    return template("prodani_produkti.html", produkti=cur)

# Pomozna metoda za brisanje prodanih produktov
@post('/prodani_produkti/brisi/')
def prodani_produkti_brisi():
        cur.execute("DELETE FROM prodani_produkti")
        redirect(url('prodani_produkti'))

@get("/produkti/dodaj")
@cookie_required_zaposlen_uporabnisko_ime
@cookie_required_zaposlen_vloga
def produkti_dodaj():
    vlogica= request.get_cookie("vloga")
    uporabniski_imencek = request.get_cookie("uporabnisko_ime")
    if vlogica == "delavec":
        return template("nimas_dovoljenja.html")
    else:
        return template("uredi_produkt.html")

@post("/produkti/dodaj")
@cookie_required_zaposlen_uporabnisko_ime
@cookie_required_zaposlen_vloga
def produkti_dodaj_post():
    vlogica= request.get_cookie("vloga")
    uporabniski_imencek = request.get_cookie("uporabnisko_ime")
    if vlogica == "delavec" :
        return template("nimas_dovoljenja.html")
    else:
        id_produkt = request.forms.getunicode('id_produkt')
        prodajna_cena = request.forms.getunicode('prodajna_cena')
        nabavna_cena = request.forms.getunicode('nabavna_cena')
        ime_produkt = request.forms.getunicode('ime_produkt')
        cur.execute("INSERT INTO produkti (id_produkt, prodajna_cena, nabavna_cena, ime_produkt) VALUES (%s, %s, %s, %s)", (id_produkt, prodajna_cena, nabavna_cena, ime_produkt))
        redirect(url('produkti'))

@get('/produkti/uredi/<id_produkt>')
@cookie_required_zaposlen_uporabnisko_ime
@cookie_required_zaposlen_vloga
def produkti_uredi(id_produkt):
    vlogica= request.get_cookie("vloga")
    uporabniski_imencek = request.get_cookie("uporabnisko_ime")
    if vlogica == "delavec" :
        return template("nimas_dovoljenja.html")
    else:
        cur.execute("SELECT id_produkt, prodajna_cena, nabavna_cena, ime_produkt FROM produkti WHERE id_produkt = %s", [id_produkt])
        res = cur.fetchone()
        if res is None:
            redirect(url('produkti'))
        id_produkt, prodajna_cena, nabavna_cena, ime_produkt = res
        return template("uredi_produkt.html", id_produkt=id_produkt, prodajna_cena=prodajna_cena, nabavna_cena=nabavna_cena, ime_produkt=ime_produkt)
        
@post('/produkti/uredi/<id_produkt>')
@cookie_required_zaposlen_uporabnisko_ime
@cookie_required_zaposlen_vloga
def produkti_uredi_post(id_produkt):
    vlogica= request.get_cookie("vloga")
    uporabniski_imencek = request.get_cookie("uporabnisko_ime")
    if vlogica == "delavec" :
        return template("nimas_dovoljenja.html")
    else:
        novi_id_produkt = request.forms.getunicode('id_produkt')
        prodajna_cena = request.forms.getunicode('prodajna_cena')
        nabavna_cena = request.forms.getunicode('nabavna_cena')
        ime_produkt = request.forms.getunicode('ime_produkt')
        cur.execute("UPDATE produkti SET id_produkt = %s, prodajna_cena = %s, nabavna_cena = %s, ime_produkt = %s WHERE id_produkt = %s", [novi_id_produkt, prodajna_cena, nabavna_cena, ime_produkt, id_produkt])
        redirect(url('produkti'))

@post('/produkti/brisi/<id_produkt>')
@cookie_required_zaposlen_uporabnisko_ime
@cookie_required_zaposlen_vloga
def produkti_brisi(id_produkt):
    vlogica= request.get_cookie("vloga")
    uporabniski_imencek = request.get_cookie("uporabnisko_ime")
    if vlogica == "delavec" :
        return template("nimas_dovoljenja.html")
    else:
        cur.execute("DELETE FROM produkti WHERE id_produkt = %s", [id_produkt])
        redirect(url('produkti'))

###################################################PRIJAVA zaposleni
@get('/prijava_zaposleni/') 
def prijava_zaposleni_get():
    return template("prijava_zaposleni.html", uporabnisko_ime = "", geslo = "",napaka2  = None)

@post('/prijava_zaposleni/')
def prijava_zaposleni_post():
    uporabnisko_ime = request.forms.getunicode('Uporabnisko_ime')
    geslo = password_hash(request.forms.getunicode('Geslo'))
    if uporabnisko_ime is None or geslo is None:
        redirect(url(''))      
    oseba = cur   
    hashBaza = None
    try: 
        hashBaza = cur.execute("SELECT geslo FROM zaposleni WHERE uporabnisko_ime = %s", [uporabnisko_ime])
        hashBaza = cur.fetchone()
        hashBaza = hashBaza[0]
        print("AA")
    except:
        hashBaza = None 
        print("BBB")
    if hashBaza is None:
        return template('napacno_geslo_zaposleni.html',   napaka2="Zaposleni s tem imenom ne obstaja")
    if geslo != hashBaza:
        return template('napacno_geslo_zaposleni.html',   napaka2="Geslo ni pravilno")
    if geslo == hashBaza:
        cur.execute("""
            SELECT vloge.vloga, zaposleni.uporabnisko_ime, zaposleni.geslo, zaposleni.trr
            FROM zaposleni
            LEFT JOIN vloge ON zaposleni.trr = vloge.trr
            WHERE zaposleni.uporabnisko_ime = %s;
            """, (uporabnisko_ime,))
        vloga_za_cookie = str(cur.fetchone()[0]) 
        response.set_cookie("uporabnisko_ime",uporabnisko_ime,path = "/")
        response.set_cookie("vloga",vloga_za_cookie,path = "/")
        cur.execute("SELECT * FROM zaposleni")
#        print(request.get_cookie("uporabnisko_ime"))
#        print(request.get_cookie("vloga"))
        redirect(url('/zacetna_zaposleni/'))
        #return print(request.get_cookie("uporabnisko_ime"))        
    else:
        return print("tu te ni")
     #pri zgornjem redirectu je treba sam napisat kam naj se da

#OSNUTEK KODE ZA PRIJAVO IN REGISTRACIJO

@get('/prijava/') 
def prijava_get():
    return template("login.html", uporabnisko_ime = "", geslo = "",napaka2  = None)

@post('/prijava/')
def prijava_post():
    uporabnisko_ime = request.forms.getunicode('Uporabnisko_ime')
    geslo = password_hash(request.forms.getunicode('Geslo'))
    if uporabnisko_ime is None or geslo is None:
        redirect(url(''))      
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
        #redirect na login
    if hashBaza is None:
        return template('napacno_geslo.html',   napaka2="Uporabnik s tem imenom ne obstaja")
    if geslo != hashBaza:
        print(hashBaza)
        print(geslo)
        return template('napacno_geslo.html',   napaka2="Geslo ni pravilno")
    if geslo == hashBaza:
        response.set_cookie("uporabnisko_ime",uporabnisko_ime, path="/")
        cur.execute("SELECT * FROM zaposleni")
        return template("zacetna.html",  zaposlene=cur)
        #return print(request.get_cookie("uporabnisko_ime"))     
    else:
        return print("tu te ni")
    



@get('/registracija/')
def registracija_get():
    return template("registracija.html", uporabnisko_ime = "", geslo1 = "", geslo2 = "",ime = "",priimek = "",naslov = "",trr = "",mesto = "", napaka = None )


@post('/registracija/')
def registracija_post():
    uporabnisko_ime = request.forms.getunicode('Uporabnisko_ime')
    geslo1 = password_hash(request.forms.getunicode('Geslo1'))
    geslo2 = password_hash(request.forms.getunicode('Geslo2'))
    ime = request.forms.getunicode('Ime')
    priimek = request.forms.getunicode('Priimek')
    naslov = request.forms.getunicode('Naslov')
    trr = request.forms.getunicode('TRR')
    mesto = request.forms.getunicode("Mesto")
    cur.execute("SELECT * FROM kupci WHERE uporabnisko_ime = %s", [uporabnisko_ime])
    if cur.fetchone():
        print('ime že zasedeno')
        # return template("registracija.html", uporabnisko_ime="", geslo1="", geslo2="", napaka='To uporabniško ime je že zasedeno.')
    elif not geslo1 == geslo2:
        print('gesli se ne ujemata')
        # Geslo se ne ujemata
        # return template("registracija.html",  uporabnisko_ime="", geslo1="", geslo2="", napaka='Gesli se ne ujemata.')    
    else:
        cur.execute("INSERT INTO kupci (ime, priimek, naslov, mesto, trr, uporabnisko_ime, geslo) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (ime, priimek, naslov, mesto, trr, uporabnisko_ime, geslo1))
        conn.commit()
        response.set_cookie("uporabnisko_ime", uporabnisko_ime, path="/")
        print("juhuhu")#neki
    redirect('/')

        


@get('/odjava')
def odjava():
    """
    Odjavi uporabnika iz aplikacije. Pobriše piškotke o uporabniku in njegovi roli.
    """
    
    response.delete_cookie("uporabnisko_ime")
    response.delete_cookie("vloga")
    response.delete_cookie("kosarica")
    
    redirect('/')



###############KOŠARICA IN NJENA VSEBINA################################

# @post('/dodaj_v_kosaro/')
# def dodaj_post():
#     if False:
#         "pri produktih je nekaj narobe"
#     else:
#         prodajna_cena = int(request.forms.getunicode('prodajna_cena'))
#         ime_produkt = str(request.forms.getunicode('ime_produkt'))
#     redirect(url('dodaj_get'))

#potrbujemo nakupuj-sesznam vseh izdelkov klikneš nanga in da v košarico.
@get("/nakupuj/")
def nakupuj_get():
    cur.execute("SELECT prodajna_cena, ime_produkt FROM produkti")
    rows = cur.fetchall()
    kosarica = request.get_cookie("kosarica")
    if kosarica is None:
        kosarica = {}
    else:
        kosarica = json.loads(kosarica)
    
    print(request.get_cookie("uporabnisko_ime"))
    prijavljen = False if request.get_cookie("uporabnisko_ime") is None else True
    return template("nakupuj.html", produkti=rows, kosarica=kosarica, prijavljen=prijavljen)

@post("/dodaj_v_kosarico")
def dodaj_v_kosarico():
    kosarica = request.get_cookie("kosarica")
    if kosarica is None:
        kosarica = {}
    else:
        kosarica = json.loads(kosarica)
    
    prodajna_cena = request.forms.getunicode('prodajna_cena')
    ime_produkt = request.forms.getunicode('ime_produkt')
    kolicina = request.forms.getunicode('kolicina')
    kosarica[ime_produkt] = (prodajna_cena, kolicina)
    kosarica_str = json.dumps(kosarica)
    response.set_cookie("kosarica", value=kosarica_str)
    cur.execute("SELECT prodajna_cena, ime_produkt FROM produkti")
    rows = cur.fetchall()
    return template("nakupuj.html", produkti=rows, kosarica=kosarica, prijavljen=True)

@post("/odstrani_iz_kosarice")
def odstrani_iz_kosarice():
    kosarica = request.get_cookie("kosarica")
    if kosarica is None:
        kosarica = {}
    else:
        kosarica = json.loads(kosarica)

    ime_prod = request.forms.getunicode('ime_prod')
    del kosarica[ime_prod]
    kosarica_str = json.dumps(kosarica)
    print(kosarica_str)
    response.set_cookie("kosarica", value=kosarica_str)
    cur.execute("SELECT prodajna_cena, ime_produkt FROM produkti")
    rows = cur.fetchall()
    return template("nakupuj.html", produkti=rows, kosarica=kosarica, prijavljen=True)

@get("/zakljuci_nakup")
def zakljuci_nakup():
    kosarica = request.get_cookie("kosarica")
    uporabnisko_ime = request.get_cookie("uporabnisko_ime")
    if kosarica is None:
        return template("nakup_zakljucen_napaka.html")
    else:
        kosarica = json.loads(kosarica)

    for produkt in kosarica.items():
        print(f"Dodajanje {len(kosarica.items())} produktov...")
        cur.execute("INSERT INTO prodani_produkti (cas_nakupa, uporabnisko_ime, produkt, cena, kolicina) VALUES (%s,%s,%s,%s,%s)", (str(date.today()), uporabnisko_ime, produkt[0], (produkt[1])[0], (produkt[1])[1] ))
        conn.commit()
    response.delete_cookie("kosarica")
    

    return template("nakup_zakljucen.html")

#Funkcija da vse gesla v tabeli zaposleni ter vse gesla v tabeli kupci update s funkcijo 
# hash neki tako da bodo gesla hashirana 












#TO MORE BITI TUKAJ SPODAJ KODO PIŠI VIŠJE !!!
# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)