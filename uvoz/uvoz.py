import auth as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

import pandas as pd

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 


def ustvari_tabelo_zaposlenih():
    cur.execute("""
        CREATE TABLE zaposleni (
        ime_priimek TEXT NOT NULL,
        naslov TEXT NOT NULL,
        mesto TEXT NOT NULL,
        TRR TEXT PRIMARY KEY,
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
    with open("podatki/Zaposleni.csv" , encoding  = "utf8" ,errors = "ignore") as f :
        rd = csv.reader(f)
        next(rd)
        for r in rd : 
            cur.execute("""
            INSERT INTO zaposleni
            (ime_priimek , naslov, mesto , TRR , placa, stevilo_ur)
            VALUES
            (%s, %s , %s , %s , %f,%f)
            """ , r)
    conn.commit()

ustvari_tabelo_zaposlenih()
uvozi_podatke_zaposlenih()


