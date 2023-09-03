import auth_public  as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv
import hashlib
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

#pobrisi_tabelo_vlog()
#pobrisi_tabelo_zaposlenih()
#ustvari_tabelo_zaposlenih()
#uvozi_podatke_zaposlenih()

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

#pobrisi_tabelo_kupcev()
#ustvari_tabelo_kupcev() 
#uvozi_podatke_kupcev()

################################### Oddelki

def ustvari_tabelo_oddelkov():
    cur.execute("""
    CREATE TABLE oddelki(
    id_oddelek INTEGER PRIMARY KEY,
    TRR TEXT NOT NULL,
    stanje NUMERIC NOT NULL,
    ime TEXT NOT NULL
    );
    """)
    conn.commit()

def pobrisi_tabelo_oddelkov():
    cur.execute("""
    DROP TABLE oddelki;
    """)
    conn.commit()

def uvozi_podatke_oddelkov():
    df = pd.read_excel("podatki/Tabele.xlsx" ,sheet_name="Sheet3", skiprows=[0],  header=None)
    for row in df.itertuples():
        vrstica = list(row)[1:]
        cur.execute("""
            INSERT INTO oddelki(
            id_oddelek , TRR, stanje , ime)
            VALUES
            (%s, %s, %s, %s);
        """, vrstica)
    conn.commit()    

#pobrisi_tabelo_oddelkov()
#ustvari_tabelo_oddelkov()
#uvozi_podatke_oddelkov()

################################PRODUKTI

def ustvari_tabelo_produktov():
    cur.execute("""
    CREATE TABLE produkti(
    id_produkt INTEGER PRIMARY KEY,
    prodajna_cena NUMERIC NOT NULL,
    nabavna_cena NUMERIC NOT NULL,
    ime_produkt TEXT NOT NULL
    );
    """)
    conn.commit()

def pobrisi_tabelo_produktov():
    cur.execute("""
    DROP TABLE produkti ;
    """)
    conn.commit()

def uvozi_podatke_produktov():    
    df = pd.read_excel("podatki/Tabele.xlsx" ,sheet_name="Sheet5", skiprows=[0],  header=None)
    for row in df.itertuples():
        vrstica = list(row)[1:]
        cur.execute("""
            INSERT INTO produkti(
            id_produkt , prodajna_cena, nabavna_cena , ime_produkt)
            VALUES
            (%s, %s, %s, %s);
        """, vrstica)
    conn.commit()    

#ustvari_tabelo_produktov()
#uvozi_podatke_produktov()

################ Tabele (povezovalne)
##Povezovalna tabela med [zaposleni(ključ TRR); vloga ;oddelek] 

def ustvari_tabelo_vlog():
    cur.execute("""
    CREATE TABLE vloge(
    TRR TEXT REFERENCES zaposleni(TRR),
    vloga TEXT NOT NULL,
    id_oddelek INTEGER REFERENCES oddelki(id_oddelek)
    );
    """)
    conn.commit()

def pobrisi_tabelo_vlog():
    cur.execute("""
    DROP TABLE vloge ;
    """)
    conn.commit()

def uvozi_podatke_vlog():
    df = pd.read_excel("podatki/Tabele.xlsx" ,sheet_name="Sheet2", skiprows=[0],  header=None)
    for row in df.itertuples():
        vrstica = list(row)[1:]
        cur.execute("""
        INSERT INTO vloge(TRR, vloga,id_oddelek )
        VALUES 
        (%s,%s,%s) ;
        """, vrstica)
    conn.commit()

#ustvari_tabelo_vlog()
#pobrisi_tabelo_vlog()
#uvozi_podatke_vlog()

######Povezovalna tabela med[id_oddelek  in id_produkt]

def ustvari_tabelo_proizvodnja():
    cur.execute("""
    CREATE TABLE proizvodnja(
    id_oddelek INTEGER REFERENCES oddelki(id_oddelek),
    id_produkt INTEGER REFERENCES produkti(id_produkt)
    );
    """)
    conn.commit()

def pobrisi_tabelo_proizvodnja():
    cur.execute("""
    DROP TABLE proizvodnja ;
    """)
    conn.commit()

def uvozi_podatke_proizvodnja():
    df = pd.read_excel("podatki/Tabele.xlsx" ,sheet_name="Sheet4", skiprows=[0],  header=None)
    for row in df.itertuples():
        vrstica = list(row)[1:]
        cur.execute("""
        INSERT INTO proizvodnja(id_oddelek , id_produkt)
        VALUES (%s, %s);
        """,vrstica)
    conn.commit()

#ustvari_tabelo_proizvodnja()
#uvozi_podatke_proizvodnja()




#Tulele je nekaj funkcij k sem jih uporabil da sem preveril če stvar dela
#ni relevantno 
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
    for row in df.itertuples():
        print(row)

#pomoc()    

#pip install openpyxl
##############Za spreminjanje gesel v tabeli kupci
def password_hash(s):
    """Vrni SHA-512 hash danega UTF-8 niza. Gesla vedno spravimo v bazo
       kodirana s to funkcijo."""
    h = hashlib.sha512()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

def pomoc_hash():
    cur.execute("SELECT * FROM kupci")
    rows = cur.fetchall()
    for row in rows:
        trr  = row[4]
        staro_geslo = row[6]
        novo_geslo = password_hash(staro_geslo) 
        cur.execute("UPDATE kupci SET geslo = %s WHERE trr = %s" , (novo_geslo, trr))
        print(novo_geslo , staro_geslo)
    conn.commit()     

# pomoc_hash()
# print(password_hash("pb4CbuMIXf1F"))

def pomoc_hash_zaposleni():
    cur.execute("SELECT * FROM zaposleni")
    rows = cur.fetchall()
    for row in rows:
        trr  = row[4]
        staro_geslo = row[6]
        novo_geslo = password_hash(staro_geslo)
        cur.execute("UPDATE zaposleni SET geslo = %s WHERE trr = %s" , (novo_geslo, trr))
        print(novo_geslo , staro_geslo) 
    conn.commit()
#pomoc_hash_zaposleni()

def stvari_iz_produkti_v_nove():
    cur.execute("SELECT * FROM produkti")
    rows = cur.fetchall()
    for row in rows:
        prodajna_cena = row[1]
        nabavna_cena = row[2]
        ime_produkt = row[3]
        print(f"nekie {prodajna_cena} neki {nabavna_cena} neki {ime_produkt}")
        cur.execute("""INSERT INTO produkti_nova (prodajna_cena, nabavna_cena, ime_produkt)
        VALUES (%s, %s, %s)""" , (prodajna_cena , nabavna_cena , ime_produkt))
    conn.commit()

stvari_iz_produkti_v_nove()    

















