# Employee Hub
### Final project SDA
Online aplikace pro správu firemních dat jako komplexní nástroj, který usnadňuje organizaci a sledování všech důležitých informací v rámci společnosti. 
Umožňuje efektivní správu objednávek, což zajišťuje rychlé a přesné zpracování požadavků zákazníků. 
Karta zaměstnance nabízí přehled o pracovních výkonech, dovolené a dalších relevantních údajích, čímž podporuje lepší komunikaci a spolupráci v týmu. 
Díky uživatelsky přívětivému rozhraní a přístupu z jakéhokoli zařízení se zvyšuje produktivita a transparentnost.

Tato aplikace je ideálním řešením pro menší moderní firmy, které chtějí optimalizovat své procesy a zefektivnit správu dat.

## Mockup
- [x] GIT
- [x] vytvoření wireframe
- [x] design UI prvků
- [x] uživatelské scénáře
- [x] prezentace mockupu
## Základ
- [x] HTML kostra
- [x] klíčové fce (registrace, přilášení, vyhledávání, přiřazování objednávek...)
- [x] testování
## Plná verze
- [x] pokročilé funkce
- [x] optimalizace výkonu
- [x] responzivní design
- [x] finální testování

# Instalace
## Krok 1 - Vytvoření a aktivace virtuálního prostředí
    python -m venv venv
    venv\Scripts\activate

## Krok 2 - Instalace závislostí
    pip install -r requirements.txt

## Krok 3 - Vytvoření migrací
    python manage.py makemigrations

## Krok 4 - Aplikace migrací
    python manage.py migrate

## Krok 5 - Vytvoření superuživatele
    python manage.py createsuperuser

## Krok 6 - Spuštění vývojového serveru
    python manage.py runserver
