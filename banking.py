import random
import sys
import sqlite3
card_num = 0
serial_number = 0
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS card( 
    id INTEGER, 
    number TEXT, 
    pin TEXT, 
    balance INTEGER DEFAULT 0
);''')


def convert(value):
    if value is None:
        return 0
    else:
        return value


def income():
    print("Enter income:")
    money = int(input())
    cur.execute('SELECT balance FROM card WHERE number = ?', (card_num,))
    cur_bal = cur.fetchone()
    bal = convert(cur_bal[0]) + money
    cur.execute('UPDATE card SET balance = ? WHERE number = ?', (bal, card_num))
    conn.commit()
    print("Income was added!")
    menu()


def transfer():
    cur.execute('SELECT number FROM card')
    numl = cur.fetchall()
    num = [x[0] for x in numl]
    print("Enter card number:")
    receiver_num = input()
    if receiver_num in num:
        print("Enter how much money you want to transfer:")
        money = int(input())
        cur.execute('SELECT balance FROM card WHERE number = ?', (receiver_num,))
        bal = cur.fetchone()
        receiver_balance = convert(bal[0])
        cur.execute('SELECT balance FROM card WHERE number = ?', (card_num,))
        cur_bal = cur.fetchone()
        current_balance = convert(cur_bal[0])
        if money > current_balance:
            print("Not enough money!")
            menu()
        else:
            current_balance -= money
            receiver_balance += money
            cur.execute("UPDATE card SET balance = ? WHERE number = ?", (current_balance, card_num))
            conn.commit()
            cur.execute('UPDATE card SET balance = ? WHERE number = ?', (receiver_balance, receiver_num))
            conn.commit()
            print("Success!")
            menu()
    elif receiver_num == card_num:
        print("You can't transfer money to the same account!")
        menu()
    if luhn_check(int(receiver_num)) is False:
        print("Probably you made a mistake in the card number. Please try again!")
        menu()
    else:
        print("Such a card does not exist.")
        menu()


def close():
    cur.execute('DELETE FROM card WHERE number = ?', (card_num,))
    conn.commit()
    print("The account has been closed!")
    main_menu()


def check_balance():
    cur.execute('SELECT balance FROM card WHERE number = ?', (card_num,))
    bal = cur.fetchall()
    balance = [x[0] for x in bal]
    print("Balance: ", balance[-1])
    menu()


def main_menu():
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")
    anw = int(input())
    if anw == 1:
        account_create()
    elif anw == 2:
        account_login()
    else:
        print("Bye!")
        sys.exit()


def menu():
    print("1. Balance")
    print("2. Add income")
    print("3. Do transfer")
    print("4. Close account")
    print("5. Log out")
    print("0. Exit")
    anw = int(input())
    if anw == 1:
        check_balance()
    elif anw == 2:
        income()
    elif anw == 3:
        transfer()
    elif anw == 4:
        close()
    elif anw == 5:
        print("You have successfully logged out!")
        main_menu()
    else:
        print("Bye!")
        sys.exit()


def save_card_info(i, numm, pin):
    info = [(i, numm, pin)]
    cur.executemany('INSERT INTO card VALUES (?, ?, ?, NULL)', info)
    conn.commit()


def account_create():
    global serial_number
    client_id = random.randint(100000000, 999999999)
    checksum = int(str(400000) + str(client_id))
    client_pin = str(random.randint(1000, 9999))
    client_card = str(400000) + str(client_id) + str(luhn(checksum))
    save_card_info(serial_number, client_card, client_pin)
    serial_number += 1
    print("Your card has been created")
    print("Your card number:")
    print(client_card)
    print("Your card PIN:")
    print(client_pin)
    main_menu()


def luhn_check(n):
    r = [int(ch) for ch in str(n)][::-1]
    return (sum(r[0::2]) + sum(sum(divmod(d*2, 10)) for d in r[1::2])) % 10 == 0


def luhn(card_number):
    arr_num = [int(x) for x in str(card_number)]
    odd_nums = arr_num[::2]
    even_nums = arr_num[1::2]
    summ = 0
    for i in range(0, len(even_nums)):
        summ += even_nums[i]
    for i in range(0, len(odd_nums)):
        odd_nums[i] *= 2
        if odd_nums[i] > 9:
            odd_nums[i] -= 9
        summ += odd_nums[i]
    if summ % 10 == 0:
        return 0
    else:
        return 10 - summ % 10


def account_login():
    global card_num
    print("Enter your card number:")
    card_num = input()
    print("Enter your PIN:")
    card_pin = input()
    cur.execute('SELECT number FROM card')
    numl = cur.fetchall()
    num = [x[0] for x in numl]
    cur.execute('SELECT pin FROM card')
    pinl = cur.fetchall()
    pin = [x[0] for x in pinl]
    if card_num in num and card_pin in pin:
        print("You have successfully logged in!")
        menu()
    else:
        print("Wrong card number or PIN!")
        main_menu()


main_menu()