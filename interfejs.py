import psycopg2
import decimal as dec
from tkinter import N
import PySimpleGUI as sg
from DatabaseManager import DatabaseManager

HOSTNAME = 'hostname'
DATABASE = 'database'
USERNAME = 'username'
PASSWORD = 'password'
OPTIONS = 'options'

def stworz_okno(tytul: str, layout: list) -> sg.Window:
    sg.theme('DarkRed')
    return sg.Window(tytul, layout)

def zaloguj():
    layout = [
        [sg.Text('Logowanie')],
        [sg.Text('Login', size =(15, 1)), sg.InputText()],
        [sg.Text('Hasło', size =(15, 1)), sg.InputText()],
        [sg.Submit(button_text='Zaloguj')]
    ]
    window = stworz_okno('LOGOWANIE', layout)
    databaseManager = DatabaseManager(HOSTNAME, DATABASE, USERNAME, PASSWORD, OPTIONS)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            window.close()
            break
        if event == 'Zaloguj':
            user = databaseManager.znajdz_uzytkownika(values[0], values[1])
            if(user is None):
                sg.popup('Błedne dane logowania!')
            else:
                window.close()
                return show_menu(databaseManager, user)

def show_menu(databaseManager: DatabaseManager, user: tuple):
    layout = [
        [sg.Text('Wybierz operację')],
        [sg.Button('Przyjmij dostawę')],
        [sg.Button('Sprzedaż')],
        [sg.Button('Sprawdź stan magazynowy')],
        [sg.CloseButton(button_text='Wyjście')]
    ]
    if user[3] == 'kierownik':
        layout.append([sg.Button('Dodaj użytkownika')])

    window = stworz_okno('DROGERIA', layout)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Wyjście'):
            break
        if event == 'Sprawdź stan magazynowy':
            sprawdz_stan_magazynowy(databaseManager)
        if event == 'Dodaj użytkownika':
            dodaj_uzytkownika(databaseManager)
        if event == 'Przyjmij dostawę':
            przyjecie_dostawy(databaseManager)
        if event == 'Sprzedaż':
            sprzedaz(databaseManager, user[0])

    window.close()
    
def sprawdz_stan_magazynowy(databaseManager: DatabaseManager):
    layout = [
        [sg.Text('Stan magazynowy')],
        [sg.Text('Kod kreskowy:', size =(15, 1)), sg.InputText()],
        [sg.Submit(button_text='Wyślij'), sg.CloseButton(button_text='Wyjście')]
    ]
    window = stworz_okno('STAN MAGAZYWNOWY', layout)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Wyjście'):
            break
        if values[0] != "":
            produkt = databaseManager.znajdz_produkt(values[0])
            if produkt is None:
                sg.popup('Produkt nie istnieje!')
            else:
                ilosc = databaseManager.ilosc_produktu(produkt[0])
                sg.popup(f'Jest {ilosc} sztuk')

    window.close()

def dodaj_uzytkownika(databaseManager: DatabaseManager):
    layout = [
        [sg.Text('Dodaj użytkownika')],
        [sg.Text('Login:', size =(15, 1)), sg.InputText()],
        [sg.Text('Hasło:', size =(15, 1)), sg.InputText()],
        [sg.Text('Stanowisko:', size =(15, 1)), sg.InputText()],
        [sg.Submit(button_text='Wyślij'), sg.CloseButton(button_text='Wyjście')]
    ]
    window = stworz_okno('NOWY UŻYTKOWNIK', layout)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Wyjście'):
            break
        if values[0] != "" and values[1] != "" and values[2] != "":
            try:
                databaseManager.dodaj_uzytkownika(values[0], values[1], values[2])
                sg.popup(f'Dodałem nowego użytkownika')
            except (psycopg2.errors.UniqueViolation) as blad:
                sg.popup("Użytkownik o tym loginie już istnieje!", blad)
            except (psycopg2.errors.RaiseException) as blad:
                sg.popup('Wystąpił błąd!', blad)
    
    window.close()

def przyjecie_dostawy(databaseManager: DatabaseManager):
    layout = [
        [sg.Text('Kod kreskowy:', size =(15, 1)), sg.InputText()],
        [sg.Text('Ilość: ', size =(15, 1)), sg.InputText()],
        [sg.Submit(button_text='Wyślij'), sg.CloseButton(button_text='Wyjście')]
    ]
    window = stworz_okno('DOSTAWA', layout)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Wyjście'):
            break
        if values[0] != "" and values[1] != "":
            produkt = databaseManager.znajdz_produkt(values[0])
            if produkt is None:
               sg.popup('Produkt nie istnieje!')
            else: 
                databaseManager.przyjmij_dostawe(produkt[0], values[1])
                ilosc = values[1]
                sg.popup(f'Dodałem {ilosc} sztuk')

    window.close()

def sprzedaz(databaseManager: DatabaseManager, user_id: int):
    layout = [
        [sg.Text('Kod kreskowy:', size =(15, 1)), sg.InputText()],
        [sg.Text('Ilość:', size =(15, 1)), sg.InputText()],
        [sg.Submit(button_text='Dodaj'), sg.Submit(button_text='Zakończ sprzedaż'), sg.CloseButton(button_text='Anuluj sprzedaż')],
    ]
    window = stworz_okno('SKANOWANIE', layout)

    sprzedaz_id = databaseManager.rozpoczecie_sprzedazy(user_id)
    while True:
        event, values = window.read()
        if event == 'Dodaj':
            produkt = databaseManager.znajdz_produkt(values[0])
            if(produkt is None):
                sg.popup('Produkt nie istnieje!')
            else:
                try:
                    databaseManager.skanowanie_produktu(produkt[0], values[1], produkt[1], sprzedaz_id)
                    sg.popup('Dodałem produkt')
                except (psycopg2.errors.UniqueViolation) as blad:
                    sg.popup("Produkt już został zeskanowany!")
        if event in (sg.WIN_CLOSED, 'Anuluj sprzedaż'):
            databaseManager.anulowanie_sprzedazy(sprzedaz_id)
            sg.popup('Anulowałem sprzedaz')
            break
        if event == 'Zakończ sprzedaż':
            databaseManager.zakonczenie_sprzedazy(sprzedaz_id)
            sg.popup('Zakonczylem sprzedaz')
            break

    window.close()
            
if __name__ == "__main__":
    zaloguj()
