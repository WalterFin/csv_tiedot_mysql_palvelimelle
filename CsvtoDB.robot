*** Settings ***
Library    Collections
Library    CSVLibrary
Library    DatabaseLibrary
Library    DateTime
Library    String
Library    invoicenumbers.py

*** Variables ***
${dbname}    DB_name
${dbuser}    DB_User
${dbpass}    DB_password
${dbhost}    localhost
${dbport}    3306

*** Keywords ***
Make Connection
    Connect To Database    pymysql    ${dbname}    ${dbuser}
    ...    ${dbpass}    ${dbhost}    ${dbport}

*** Test Cases ***
Read csv file to invoiceheader
  #laskut tietokantaan invoiceheader
  #csv tiedoston rivit listaan
  @{list}=  read csv file to list  Untitled.csv
  Log  ${list}
  #laskuri ohittamaan csv-tiedoston ekan rivin
  ${counter}    Set Variable    0
  Make connection
    FOR    ${element}    IN    @{list}
        #ohitetaan eka rivi
        IF    ${counter}>0
            #muuttujat listan soluista, jotka tallennetaan mysql kantaan
            ${invoicenumber}=    Evaluate    int('${element}[0]')
            ${companyname}=    Set Variable    ${element}[1]
            ${companycode}=    Set Variable    ${element}[4]
            ${referencenumber}=    Evaluate    int('${element}[2]')
            ${date_object}=    Convert Date    ${element}[6]    date_format=%d.%m.%Y
            ${invoicedate}=    Evaluate    "${date_object}".split()[0]
            ${date_object}=    Convert Date    ${element}[3]    date_format=%d.%m.%Y
            ${duedate}=    Evaluate    "${date_object}".split()[0]
            ${bankaccountnumber}=    Set Variable    ${element}[5]
            ${amountexvat}=    Evaluate    float('${element}[7]')
            ${vat}=    Evaluate    float('${element}[9]')
            ${totalvalue}=    Evaluate    float('${element}[8]')
            Execute Sql String    insert ignore into invoiceheader values (${invoicenumber}, '${companyname}', ${companycode}, ${referencenumber}, '${invoicedate}', '${duedate}', '${bankaccountnumber}', ${amountexvat}, ${vat}, ${totalvalue}, 4, 'Not verified');
        END
        Log    ${counter}
        ${counter}    Evaluate    ${counter}+1
    END
*** Test Cases ***
Read csv file to invoicerow
  #laskujen erittely tietokantaan
  @{erittely}=  read csv file to list  laskujen erittely.csv
  ${counter}    Set Variable    0
  Make connection
  FOR    ${element}    IN    @{erittely}
      Log    ${element}
      IF    ${counter} > 0
          Log    ${element}
          ${invoicenumber}=    Evaluate    int('${element}[0]')
          ${description}=    Set Variable    ${element}[1]
          ${quanity}=    Evaluate    float('${element}[2]')
          ${unit}=    Set Variable    ${element}[3]
          ${unitprice}=    Evaluate    float('${element}[4]')
          ${vatstr}=    Set Variable    ${element}[5]
          ${vatstr}    Remove String    ${vatstr}    %
          ${vatpercent}=    Evaluate    float('${vatstr}')
          ${vatstr}=    Set Variable    ${element}[6]
          ${vatstr}=    Replace String    ${vatstr}    ,    .
          ${vat}=    Evaluate    float('${vatstr}')
          ${totalstr}=    Set Variable    ${element}[7]
          ${totalstr}=    Replace String    ${totalstr}    ,    .
          ${total}=    Evaluate    float('${totalstr}')
          ${rownumberstr}=    Catenate    ${invoicenumber}    ${counter}
          ${rownumberstr}=    Remove String    ${rownumberstr}    ${SPACE}
          ${rownumber}=    Evaluate    int('${rownumberstr}')
          Execute Sql String    insert ignore into invoicerow values (${invoicenumber}, ${rownumber}, '${description}', ${quanity}, '${unit}', ${unitprice}, ${vatpercent}, ${vat}, ${total});
      END
      ${counter}    Evaluate    ${counter}+1
  END
*** Test Cases ***
Check invoices
  Make Connection
  ${invoicenumberlist}=    invoice_numbers_list
  FOR    ${element}    IN    @{invoicenumberlist}
      ${statusidint}=    Set Variable    0
      ${ibanstatus}=    check_iban    ${element}
      ${referencestatus}=    check_referencenumber    ${element}
      ${totalcheck}=    check_sum    ${element}
      IF    ${ibanstatus} > 0
          ${statusidint}=    Set Variable    ${ibanstatus}
      ELSE IF    ${referencestatus} > 0
          ${statusidint}=    Set Variable    ${statusidint}
      END
      IF    ${totalcheck} > 0
          ${statusidint}=    Set Variable    ${totalcheck}
      END
      ${statusstr}=    get_status_string    ${statusidint}
      update_statusid    ${element}    ${statusidint}    ${statusstr}
  END