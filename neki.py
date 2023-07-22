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

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)
# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)



#za debugiranje
#debug(True)

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

##################ZAPOSLINI
@get("/zaposleni/")
@cookie_required_zaposlen_uporabnisko_ime
@cookie_required_zaposlen_vloga
def zaposleni_get():
    vlogica= request.get_cookie("vloga")
    uporabniski_imencek = request.get_cookie("uporabnisko_ime")
    cur.execute("SELECT * FROM zaposleni")
    print(vlogica)
    return template("zaposleni.html",  zaposlene=cur,v=vlogica,u = uporabniski_imencek )

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
@cookie_required_zaposlen_uporabnisko_ime
@cookie_required_zaposlen_vloga
def spremeni_placo_get():
    return template("spremeni_placo.html", trr = "",nova_placa = "", napaka= None)


@post("/spremeni_placo")
@cookie_required_zaposlen_uporabnisko_ime
@cookie_required_zaposlen_vloga 
def spremeni_placo_post():
    moja_vloga= request.get_cookie("vloga",secret="skrivnost")
    if moja_vloga == "delavec":
        print("TI pa ne smes HAHA")
    else:
        print(moja_vloga)
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





def hashGesla(s):
    m = hashlib.sha256()
    m.update(s.encode("utf-8"))
    return m.hexdigest()


# @get('/registracija/')
# def registracija_get():
#     napaka = None
#     return template('register.html', napaka=napaka)

# @post('/registracija/')
# def registracija_post():
    
#     ime = request.forms.get('Ime')
#     priimek = request.forms.get('Priimek')
#     mesto = request.forms.get('Mesto')
#     naslov = request.forms.get('Naslov')
#     trr = request.forms.get('TRR')
#     uporabnisko_ime = request.forms.get('Uporabnisko_ime')
#     geslo = request.forms.get('Geslo')
#     placa = request.forms.get('Placa')
#     st_ur = request.forms.get('Stevilo_ur')
#     vloga = request.forms.get('Vloga')
#     oddelek = request.forms.get('Oddelek')

#     uporabnik1 =
@get("/dodaj_kupec")
def dodaj_kupec_get():
    return template("register.html",
                    ime = "",priimek = '',mesto = '',naslov = '',trr = "", uporabnisko_ime ='', geslo ='',napaka= None)

@post('/dodaj_kupec')
def dodaj_kupec_post():
    if False:
        "ti sment ne smes redirect"
    else:
        ime = request.forms.get('Ime')
        priimek = request.forms.get('Priimek')
        naslov = request.forms.get('Naslov')
        mesto = request.forms.get('Mesto')
        trr = request.forms.get('TRR')
        uporabnisko_ime = request.forms.get('Uporabnisko_ime')
        geslo = request.forms.get('Geslo')
    try: 
        cur.execute("""INSERT INTO kupci 
            (ime, priimek, naslov, mesto,trr,uporabnisko_ime,
             geslo) 
            VALUES(%s, %s,%s,%s,%s,%s,%s)""",
            (ime, priimek, mesto, naslov,trr,uporabnisko_ime,
             geslo))
        conn.commit()
    except Exception as ex:
        conn.rollback()
        return template('register.html',ime = "",priimek = '',mesto = '',naslov = '',trr = '',
                         uporabnisko_ime ='', geslo ='',napaka= 'Zgodila se je napaka: %s' % ex)
    redirect(url("/"))



########################################################### PRODUKTI
@get("/produkti/")
def produkti_get():
    cur.execute("SELECT * from produkti")
    return template("produkti.html", produkti=cur)

@get("/produkti/dodaj")
def produkti_dodaj():
    return template("uredi_produkt.html")

@post('/uredi_produkt')
def uredi_produkt_post():
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
        return template('uredi_produkt.html',id_produkt = "",prodajna_cena = '',nabavna_cena = '',ime_produkt = '', napaka= 'Zgodila se je napaka: %s' % ex)
    redirect(url("produkti_get"))

###################################################PRIJAVA zaposleni
@get('/prijava_zaposleni/') 
def prijava_zaposleni_get():
    return template("prijava_zaposleni.html", uporabnisko_ime = "", geslo = "",napaka2  = None)

@post('/prijava_zaposleni/')
def prijava_zaposleni_post():
    uporabnisko_ime = request.forms.get('Uporabnisko_ime')
    geslo = request.forms.get('Geslo')
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
        return print("prisel si sem")#template('login.html',   napaka2="Uporabniško ime ali geslo nista ustrezni")
    if geslo != hashBaza:
        return print("sedaj si pa tu")#print(#template('login.html',   napaka2="Uporabniško ime ali geslo nista ustrezni")
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
        return template("zaposleni.html",  zaposlene=cur,v=vloga_za_cookie,u=uporabnisko_ime)
        #return print(request.get_cookie("uporabnisko_ime"))        
    else:
        return print("tu te ni")
    redirect(url('zaposleni')) #pri zgornjem redirectu je treba sam napisat kam naj se da

#OSNUTEK KODE ZA PRIJAVO IN REGISTRACIJO

@get('/prijava/') 
def prijava_get():
    return template("login.html", uporabnisko_ime = "", geslo = "",napaka2  = None)

@post('/prijava/')
def prijava_post():
    uporabnisko_ime = request.forms.get('Uporabnisko_ime')
    geslo = request.forms.get('Geslo')
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
        return print("prisel si sem")#template('login.html',   napaka2="Uporabniško ime ali geslo nista ustrezni")
    if geslo != hashBaza:
        print(hashBaza)
        print(geslo)#template('login.html',   napaka2="Uporabniško ime ali geslo nista ustrezni")
    if geslo == hashBaza:
        response.set_cookie("uporabnisko_ime",uporabnisko_ime)
        cur.execute("SELECT * FROM zaposleni")
        return template("zacetna.html",  zaposlene=cur)
        #return print(request.get_cookie("uporabnisko_ime"))     
    else:
        return print("tu te ni")
    
    #redirect(url('zaposleni')) #pri zgornjem redirectu je treba sam napisat kam naj se da

# @get('/registracija/')
# def registracija_get():
#     #return template("registracija.html", uporabnisko_ime = "", geslo1 = "", geslo2 = "",ime = "",priimek = "",naslov = "",trr = "",mesto = "", napaka = None )



# @post("/registracija/")
# def registracija_post():
#     uporabnisko_ime = request.forms.get('Uporabnisko_ime')
#     geslo1 = request.forms.get('Geslo1')
#     geslo2 = request.forms.get('Geslo2')
#     ime = request.forms.get('Ime')
#     priimek = request.forms.get('Priimek')
#     naslov = request.forms.get('Naslov')
#     trr = request.forms.get('TRR')
#     mesto = request.forms.get("Mesto")
#     cur.execute("SELECT * FROM kupci WHERE uporabnisko_ime = %s", [uporabnisko_ime])
#     if cur.fetchone():
#         print('ime že zasedeno')
#         # return template("registracija.html", uporabnisko_ime="", geslo1="", geslo2="", napaka='To uporabniško ime je že zasedeno.')
#     elif not geslo1 == geslo2:
#         print('gesli se ne ujemata')
#         # Geslo se ne ujemata
#         # return template("registracija.html",  uporabnisko_ime="", geslo1="", geslo2="", napaka='Gesli se ne ujemata.')    
#     else:
#         cur.execute("INSERT INTO kupci (ime, priimek, naslov, mesto, trr, uporabnisko_ime, geslo) VALUES (%s,%s,%s,%s,%s,%s,%s)",
#                     (ime, priimek, naslov, mesto, trr, uporabnisko_ime, geslo1))
#         conn.commit()
#         response.set_cookie("uporabnisko_ime", uporabnisko_ime)
#         print("juhuhu")
    #neki   

        


# @get('/odjava')
# def odjava():
#     """
#     Odjavi uporabnika iz aplikacije. Pobriše piškotke o uporabniku in njegovi roli.
#     """
    
#     response.delete_cookie("uporabnik")
#     response.delete_cookie("rola")
    
#     return template('prijava.html', napaka=None)



###############KOŠARICA IN NJENA VSEBINA################################

# @post('/dodaj_v_kosaro/')
# def dodaj_post():
#     if False:
#         "pri produktih je nekaj narobe"
#     else:
#         prodajna_cena = int(request.forms.get('prodajna_cena'))
#         ime_produkt = str(request.forms.get('ime_produkt'))
#     redirect(url('dodaj_get'))

    
# @post("/produkti/dodaj")
# def produkti_dodaj_post():
#     if False:
#         "pri produktih je nekaj narobe"
#     else:
#         id_produkt = int(request.forms.get('id_produkt'))
#         prodajna_cena = int(request.forms.get('prodajna_cena'))
#         nabavna_cena = int(request.forms.get('nabavna_cena'))
#         ime_produkt = str(request.forms.get('ime_produkt'))
#     try: 
#         cur.execute("""INSERT INTO produkti 
#             (id_produkt, prodajna_cena, nabavna_cena, ime_produkt) 
#             VALUES (?, ?, ?, ?)""",
#             (id_produkt, prodajna_cena, nabavna_cena, ime_produkt))
#         conn.commit()
#     except Exception as ex:
#         conn.rollback()
#         print("Zgodila se je napaka")
#     redirect(url("produkti_get"))

@get("/produkti/uredi/<id_produkt>")
def produkti_uredi(cur, id_produkt):
    cur.execute("""
        SELECT id_produkt, prodajna_cena, nabavna_cena, ime_produkt FROM produkti WHERE id_produkt = ?
    """, (id_produkt, ))
    res = cur.fetchone()
    if res is None:
        #nastavi_sporocilo(f"Produkti {id_produkt} ne obstaja!")
        redirect(url('produkti'))
    id_produkt, prodajna_cena, nabavna_cena, ime_produkt = res
    return template("uredi_produkt.html", id_produkt=id_produkt, prodajna_cena=prodajna_cena, nabavna_cena=nabavna_cena, ime_produkt=ime_produkt)


@post("/produkti/uredi/<id_produkt>")
def produkti_uredi_post(cur, id_produkt):
    nov_id_produkt = int(request.forms.get('id_produkt'))
    prodajna_cena = int(request.forms.get('prodajna_cena'))
    nabavna_cena = int(request.forms.get('nabavna_cena'))
    ime_produkt = str(request.forms.get('ime_produkt'))
    try:
        cur.execute("""UPDATE produkti
            SET id_produkt = %s, prodajna_cena = %s, nabavna_cena = %s, ime_produkt = %s
            WHERE id_produkt = %s;
            """,(nov_id_produkt, prodajna_cena, nabavna_cena, ime_produkt, id_produkt))
        conn.commit()
    except:
        #nastavi_sporocilo(f"Urejanje produkta {id_produkt} ni uspelo.")
        redirect(url('uredi_produkt.html', id_produkt=id_produkt))
    redirect(url('produkti'))

@post("/produkti/brisi/<id_produkt>")
def produkti_brisi(cur, id_produkt):
    cur.execute("""
        DELETE FROM produkti WHERE id_produkt = ?;
        """, (id_produkt ))
        
# stara metoda - zdej samo za dodajanje 
@get("/dodaj_produkt")
def dodaj_produkt_get():
    return template("uredi_produkt.html",
                    id_produkt = "",prodajna_cena = '',nabavna_cena = '',ime_produkt = '', napaka= None)





#potrbujemo nakupuj-sesznam vseh izdelkov klikneš nanga in da v košarico.
@get("/nakupuj/")
def nakupuj_get():
    cur.execute("SELECT prodajna_cena, ime_produkt FROM produkti")
    rows = cur.fetchall()
    return template("nakupuj.html", produkti=rows)

@get('/kosarica/')
def kosara():
    ime_produkt = request.query.get('ime_produkt')

    cur.execute("CREATE TABLE IF NOT EXISTS kosara (ime_produkt TEXT, cena INTEGER)")
    cur.execute("INSERT INTO kosara (ime_produkt, cena) SELECT ime_produkt, prodajna_cena FROM produkti WHERE ime_produkt=?", (ime_produkt,))
    return template("kosarica.html")








#TO MORE BITI TUKAJ SPODAJ KODO PIŠI VIŠJE !!!
# poženemo strežnik na podanih vratih, npr. http://localhost:8080/
if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)