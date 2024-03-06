import re
import pymysql
dbname = "DB_name"
dbuser = "DB_username"
dbpass = "password"
dbhost = "localhost"
dbport = 3306  # MySQLin portti
#laskunnumerot listassa
def invoice_numbers_list():
    # Yhdistetään tietokantaan
    connection = pymysql.connect(host=dbhost,
                                 port=dbport,
                                 user=dbuser,
                                 password=dbpass,
                                 database=dbname)
    
    cursor = connection.cursor()

    try:
        # Suoritetaan SELECT-kysely tietyn sarakkeen tiedon hakemiseksi
        query = f"SELECT invoicenumber FROM invoiceheader"
        cursor.execute(query)

        # Haetaan kaikki tiedot sarakkeesta
        column_values = [row[0] for row in cursor.fetchall()]

        return column_values

    finally:
        # Suljetaan tietokantayhteys
        cursor.close()
        connection.close()
#invoicestatus tietokannasta
def get_status_string(statusnumber):
    #yhteys tietokantaan
    connection = pymysql.connect(host=dbhost,
                                 port=dbport,
                                 user=dbuser,
                                 password=dbpass,
                                 database=dbname)
    cursor = connection.cursor()
    try:
        # Suoritetaan SELECT-kysely
        query = f"SELECT name FROM invoicestatus WHERE id = {statusnumber}"
        cursor.execute(query)
        # Haetaan statys string
        cell_value = cursor.fetchone()[0]
    finally:
        # Suljetaan tietokantayhteys
        cursor.close()
        connection.close()
        return cell_value
#iban tarkastus
def check_iban(invoicenumber):
#yhteystietokantaan
    connection = pymysql.connect(host=dbhost,
                                 port=dbport,
                                 user=dbuser,
                                 password=dbpass,
                                 database=dbname)
    cursor = connection.cursor()
#haetaan iban tietokannasta ja palautetaan tarkistettu arvo
    try:
        # Suoritetaan SELECT-kysely
        query = f"SELECT bankaccountnumber FROM invoiceheader WHERE invoicenumber = {invoicenumber}"
        cursor.execute(query)
        # Haetaan statys string
        iban = cursor.fetchone()[0]
        iban = int(iban)%97
    finally:
        # Suljetaan tietokantayhteys
        cursor.close()
        connection.close()
        if iban == 1:
            return 0
        else:
            return 2
#viitenumerontarkistus
def check_referencenumber(invoicenumber):
#yhteystietokantaan
    connection = pymysql.connect(host=dbhost,
                                 port=dbport,
                                 user=dbuser,
                                 password=dbpass,
                                 database=dbname)
    cursor = connection.cursor()
#haetaan viitenumero mysql-kannasta ja palautetaan tarkistus
    try:
        # Suoritetaan SELECT-kysely
        query = f"SELECT referencenumber FROM invoiceheader WHERE invoicenumber = {invoicenumber}"
        cursor.execute(query)
        kertoimet = [7, 3, 1]
        viitestr = str(cursor.fetchone()[0])
        viitestr = re.sub(r'[ ]', '', viitestr)
        tarkistusnuomero = int(viitestr[-1:])
        viitestr = viitestr[:-1]
        #tarkasta viitenumero
        counter = 0
        summa = 0
        for item in viitestr[::-1]:
            if counter > 2:
                counter = 0
            summa = summa + (int(item) * kertoimet[counter])
            counter += 1
    finally:
        # Suljetaan tietokantayhteys
        cursor.close()
        connection.close()
        if (summa + tarkistusnuomero) % 10 == 0:
            return 0
        else:
            return 2
#laskujensumman tarkistus
def check_sum(invoicenumber):
#yhteystietokantaan
    connection = pymysql.connect(host=dbhost,
                                 port=dbport,
                                 user=dbuser,
                                 password=dbpass,
                                 database=dbname)
    cursor = connection.cursor()
#summa laskusta ja erittelystä
    try:
        # Suoritetaan SELECT-kysely
        query = f"SELECT totalamount FROM invoiceheader WHERE invoicenumber = {invoicenumber}"
        cursor.execute(query)
        laskunsumma = cursor.fetchone()[0]
        query = f"SELECT SUM(total) FROM invoicerow WHERE invoicenumber = {invoicenumber}"
        cursor.execute(query)
        erittelynsumma = cursor.fetchone()[0]
    finally:
        # Suljetaan tietokantayhteys
        cursor.close()
        connection.close()
        if erittelynsumma == laskunsumma:
            return 0
        else:
            return 3
def update_statusid(invoicenumber, statusid, statuscomment):
    connection = pymysql.connect(host=dbhost,
                                 port=dbport,
                                 user=dbuser,
                                 password=dbpass,
                                 database=dbname)
    
    cursor = connection.cursor()
    try:
        # Suoritetaan UPDATE-kysely
        query = f"UPDATE invoiceheader SET invoicestatus_id = %s, comment = %s WHERE invoicenumber = %s"
        cursor.execute(query, (statusid, statuscomment, invoicenumber))
        # Tallennetaan muutokset tietokantaan
        connection.commit()
    finally:
        # Suljetaan tietokantayhteys
        cursor.close()
        connection.close()