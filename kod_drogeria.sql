CREATE TABLE kategorie (
    id_kategorii SERIAL PRIMARY KEY,
    nazwa        VARCHAR(50) NOT NULL
);


CREATE TABLE produkty (
    id_produktu  SERIAL PRIMARY KEY,
    kod_kreskowy VARCHAR(200) NOT NULL,
    nazwa        VARCHAR(50) NOT NULL,
    producent    VARCHAR(50) NOT NULL,
    cena         INTEGER NOT NULL,
    id_kategorii INTEGER NOT NULL
);


ALTER TABLE produkty ADD UNIQUE (kod_kreskowy);
ALTER TABLE produkty ADD CHECK (cena > 0);

CREATE TABLE sprzedaz (
    id_sprzedazy   SERIAL PRIMARY KEY,
    data           DATE NOT NULL,
    status         VARCHAR(50) NOT NULL,
    id_uzytkownika INTEGER NOT NULL
);


CREATE TABLE sprzedaz_produktu (
    id_produktu  INTEGER NOT NULL,
    id_sprzedazy INTEGER NOT NULL,
    cena         INTEGER NOT NULL,
    ilosc        INTEGER NOT NULL DEFAULT(1)
);

ALTER TABLE sprzedaz_produktu ADD PRIMARY KEY (id_produktu, id_sprzedazy);
ALTER TABLE sprzedaz_produktu ADD CHECK (cena > 0);
ALTER TABLE sprzedaz_produktu ADD CHECK (ilosc > 0);

CREATE TABLE stan_magazynowy (
    id_wpisu    SERIAL PRIMARY KEY,
    ilosc       INTEGER NOT NULL,
    typ         VARCHAR(50) NOT NULL,
    id_produktu INTEGER NOT NULL
);

ALTER TABLE stan_magazynowy ADD CHECK (ilosc > 0);
ALTER TABLE ONLY drogeria.stan_magazynowy ALTER COLUMN typ SET DEFAULT 'sprzedaz';

CREATE TABLE uzytkownicy (
    id_uzytkownika SERIAL PRIMARY KEY,
    login          VARCHAR(50) NOT NULL,
    haslo          VARCHAR(200) NOT NULL,
    stanowisko     VARCHAR(50) NOT NULL
);

ALTER TABLE uzytkownicy ADD UNIQUE (login);

ALTER TABLE produkty ADD FOREIGN KEY (id_kategorii) REFERENCES kategorie (id_kategorii);
ALTER TABLE sprzedaz_produktu ADD FOREIGN KEY (id_produktu) REFERENCES produkty (id_produktu);
ALTER TABLE sprzedaz_produktu ADD FOREIGN KEY (id_sprzedazy) REFERENCES sprzedaz (id_sprzedazy);
ALTER TABLE sprzedaz ADD FOREIGN KEY (id_uzytkownika) REFERENCES uzytkownicy (id_uzytkownika);
ALTER TABLE stan_magazynowy ADD FOREIGN KEY (id_produktu) REFERENCES produkty (id_produktu);

CREATE VIEW wyniki AS 
    SELECT id_uzytkownika, SUM(cena * ilosc)
        FROM sprzedaz
            JOIN sprzedaz_produktu USING(id_sprzedazy)
        WHERE status = 'ukonczona'
    GROUP BY id_uzytkownika;

CREATE OR REPLACE FUNCTION sprawdz_stanowisko() RETURNS TRIGGER AS $$
    BEGIN 
        IF (NEW.stanowisko != 'sprzedawca' AND NEW.stanowisko != 'kierownik') THEN
        RAISE EXCEPTION 'Nie ma takiego stanowiska!';
        END IF;
        RETURN NEW;
    END
$$ LANGUAGE plpgsql;

CREATE TRIGGER sprawdz_stanowisko_trigger BEFORE INSERT OR UPDATE ON uzytkownicy
	FOR EACH ROW EXECUTE PROCEDURE sprawdz_stanowisko();

CREATE OR REPLACE FUNCTION sprawdz_produkt() RETURNS TRIGGER AS $$
    BEGIN 
        IF (SELECT produkty.id_produktu FROM produkty WHERE NEW.id_produktu = produkty.id_produktu) IS NULL THEN
        RAISE EXCEPTION 'Nie ma takiego produktu!';
        END IF;
        RETURN NEW;
    END
$$ LANGUAGE plpgsql;

CREATE TRIGGER sprawdz_produkt_trigger BEFORE INSERT OR UPDATE ON sprzedaz_produktu
	FOR EACH ROW EXECUTE PROCEDURE sprawdz_produkt();