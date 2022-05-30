import psycopg2

class DatabaseManager:
    def __init__(self, hostname, database, username, password, options):
        self.credentials = {'host': hostname, 'database': database, 'user': username, 'password': password, 'options':options}

    def fetchone(self, query: str, arguments: tuple):
        with psycopg2.connect(**self.credentials) as con:
            with con.cursor() as curs:
                curs.execute(query, arguments)
                return curs.fetchone()
    
    def fetchall(self, query: str, arguments: tuple):
        with psycopg2.connect(**self.credentials) as con:
            with con.cursor() as curs:
                curs.execute(query, arguments)
                return curs.fetchall()
    
    def wykonaj_query(self, query: str, arguments: tuple):
        with psycopg2.connect(**self.credentials) as con:
            with con.cursor() as curs:
                curs.execute(query, arguments)

    def znajdz_uzytkownika(self, login: str, haslo: str):
        return self.fetchone(f"SELECT * FROM uzytkownicy WHERE login=%s AND haslo=%s;", (login, haslo))
    
    def ilosc_produktu(self, id_produktu: int)-> int:
        aktualny_stan = 0
        stan_magazynowy = self.fetchall(f'SELECT SUM(ilosc) AS sprzedane, typ FROM stan_magazynowy WHERE id_produktu=%s GROUP BY typ;', (id_produktu,))
        for wpis in stan_magazynowy:
            if(wpis[1] == 'przyjecie'):
                aktualny_stan = aktualny_stan + wpis[0]
            else:
                aktualny_stan = aktualny_stan - wpis[0]

        return aktualny_stan
    
    def dodaj_uzytkownika(self, login: str, haslo: str, stanowisko: str):
        self.wykonaj_query(f"INSERT INTO uzytkownicy(login, haslo, stanowisko) VALUES (%s, %s, %s);", (login, haslo, stanowisko))
    
    def przyjmij_dostawe(self, id_produktu: int, ilosc: int):
        self.wykonaj_query(f"INSERT INTO stan_magazynowy (ilosc, typ, id_produktu) VALUES (%s, %s, %s);", (ilosc, "przyjecie", id_produktu))

    def rozpoczecie_sprzedazy(self, id_uzytkownika: int)-> int:
        sprzedaz = self.fetchone(f"INSERT INTO sprzedaz (data, status, id_uzytkownika) VALUES (current_timestamp, 'w trakcie', %s) RETURNING id_sprzedazy", (id_uzytkownika,))
        return sprzedaz[0]

    def znajdz_produkt(self, kod_kreskowy: str):
        return self.fetchone(f"SELECT id_produktu, cena FROM produkty WHERE kod_kreskowy=%s;", (kod_kreskowy,))

    def skanowanie_produktu(self, id_produktu: int, ilosc: int, cena: int, id_sprzedazy: int):
        self.wykonaj_query(f"INSERT INTO sprzedaz_produktu (id_produktu, id_sprzedazy, cena, ilosc) VALUES (%s, %s, %s, %s)", (id_produktu, id_sprzedazy, cena, ilosc))
    
    def anulowanie_sprzedazy(self, sprzedaz_id: int):
        self.wykonaj_query(f"UPDATE sprzedaz SET status = 'anulowana' WHERE id_sprzedazy = %s;", (sprzedaz_id,))
    
    def zakonczenie_sprzedazy(self, sprzedaz_id: int):
        self.wykonaj_query(f"UPDATE sprzedaz SET status = 'ukonczona' WHERE id_sprzedazy = %s;", (sprzedaz_id,))
        self.wykonaj_query(f"INSERT INTO stan_magazynowy (ilosc, id_produktu) SELECT ilosc, id_produktu FROM sprzedaz_produktu WHERE id_sprzedazy = %s;", (sprzedaz_id,))