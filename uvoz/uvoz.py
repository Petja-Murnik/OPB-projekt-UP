import auth_public  as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

import pandas as pd

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

################################### Zaposleni 

def ustvari_tabelo_zaposlenih():
    cur.execute("""
        CREATE TABLE zaposleni (
        ime TEXT NOT NULL,
        priimek TEXT NOT NULL,
        naslov TEXT NOT NULL,
        mesto TEXT NOT NULL,
        TRR TEXT PRIMARY KEY,
        uporabnisko_ime TEXT NOT NULL UNIQUE,
        geslo TEXT NOT NULL,
        placa NUMERIC NOT NULL,
        stevilo_ur NUMERIC NOT NULL
        );            
    """)
    conn.commit()

def pobrisi_tabelo_zaposlenih():
    cur.execute("""
    DROP TABLE zaposleni;
    """)
    conn.commit()  

def uvozi_podatke_zaposlenih():
    with open("podatki/Zaposleni.csv" , encoding  = "utf8" ,errors = "ignore") as m :
        rd = csv.reader(m)
        next(rd)
        for r in rd : 
            cur.execute("""
            INSERT INTO zaposleni
            (ime ,priimek , naslov, mesto , TRR,uporabnisko_ime , geslo , placa, stevilo_ur)
            VALUES
            (%s, %s , %s , %s , %s,%s, %s, %s,%s);
            """ , r)
    conn.commit()


pobrisi_tabelo_zaposlenih()
ustvari_tabelo_zaposlenih()
uvozi_podatke_zaposlenih()

#####################################KUPCI

def ustvari_tabelo_kupcev():
    cur.execute("""
        CREATE TABLE kupci(
        ime TEXT NOT NULL, 
        priimek TEXT NOT NULL,
        naslov TEXT NOT NULL,
        mesto TEXT NOT NULL,
        TRR TEXT PRIMARY KEY,
        uporabnisko_ime TEXT NOT NULL UNIQUE,
        geslo TEXT NOT NULL 
        ) ;
    """)
    conn.commit()

def pobrisi_tabelo_kupcev():
    cur.execute("""
    DROP TABLE kupci ;
    """)
    conn.commit()

def uvozi_podatke_kupcev():
    with open("podatki/kupci.csv" , encoding  = "utf8" ,errors = "ignore") as m :
        rd = csv.reader(m)
        next(rd)
        for r in rd :
            cur.execute("""
            INSERT INTO kupci 
            (ime, priimek , naslov, mesto , TRR ,uporabnisko_ime , geslo)
            VALUES
            (%s ,%s ,%s ,%s, %s, %s,%s);
            """, r)
    conn.commit()

pobrisi_tabelo_kupcev()
ustvari_tabelo_kupcev() 
uvozi_podatke_kupcev()
    
################ Tabele (povezovalne)
##Povezovalna tabela med [zaposleni(ključ TRR); vloga ;oddelek] 
def pomoc_dodaj_zaposleni():
    r = ["petja","murnik", "nkei","jsc","123","tsive0","asla",12,12]
    cur.execute("""
        INSERT INTO zaposleni
        (ime ,priimek , naslov, mesto , TRR,uporabnisko_ime , geslo , placa, stevilo_ur)
        VALUES
        (%s, %s,%s,%s,%s,%s,%s,%s,%s);
        """,r)
    conn.commit()

#pomoc_dodaj_zaposleni()    

def pomoc():
    df = pd.read_excel("podatki/Tabele.xlsx" ,sheet_name="Sheet2",skiprows=[0])
    print(df)

pomoc()    

#pip install openpyxl