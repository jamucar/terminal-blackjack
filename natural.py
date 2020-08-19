#!/usr/bin/env python3
'''
Terminal Blackjack game with basic rules, bet, hit, stick, blackjack pays 3 to 2, double down and split your first hand.
'''

import random
import time
import os
import csv
import datetime
from functools import reduce


class Card:
    def __init__(self, suit, value):
        '''every card has a suit and value'''
        self.suit = suit
        self.value = value

    def __repr__(self):
        '''Oveloading the objects prit() function as if one card up one down'''
        return(f"+---+ +---+\n|{self.suit}  | |X X| \n| {self.value} | | X | \n|  {self.suit}| |X X|\n+---+ +---+")




class Deck:
    def __init__(self):
        '''Creates a list of card obects for every suit and value'''
        self.cards = 6 * [Card(s, v) for s in ["♣", "♠", "♦", "♥"] for v in
                      ["A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"]]

    def shuffle(self):
        '''shuffle the card deck'''
        random.shuffle(self.cards)

    def cards_left(self):
        '''returns cards left in deck as int'''
        return (len(self.cards))

    def cards_in_deck(self):
        '''displays cards left in string'''
        return f'Cards in deck: {len(self.cards)}'

    def deal(self):
        '''removes a card from the deck'''
        return self.cards.pop(0)



class Hand:
    def __init__(self, dealer=False):
        '''the hand inclues a list with the cards, and the hands value'''
        self.dealer = dealer
        self.cards = []
        self.value = 0
        self.bet = 0


    def add_card(self, card):
        '''adds a card to the hand'''
        self.cards.append(card)



    def calculate_value(self):
        '''calculates the value of the hand'''
        self.value = 0
        has_ace = False
        aces = []
        for card in self.cards:
            if card.value.isnumeric():
                self.value += int(card.value)
            else:
                if card.value == "A":
                    has_ace = True
                    aces.append("a")
                    self.value += 11
                else:
                    self.value += 10


        for item in aces:
            if has_ace and self.value > 21:
                self.value -= 10


    def get_cards(self):
        return self.cards


    def get_value(self):
        '''calls calculate_value and returns the hand value'''
        self.calculate_value()
        return self.value


    def display(self):
        '''displays player cards and one of dealers cards'''
        if self.dealer and len(self.cards) == 2:

            print(self.cards[0])
        else:
            self.display_dealer()


    def display_dealer(self):
        '''Normal display for non hidden cards'''

        print("+---+ " * len(self.cards), end="")
        print()
        for card in self.cards:
            print("|{}  | ".format(card.suit), end="")

        print()
        for card in self.cards:
            print("| {} | ".format(card.value), end="")


        print()
        for card in self.cards:
            print("|  {}| ".format(card.suit), end="")

        print()
        print("+---+ " * len(self.cards), end="")

        print("\nValue:", self.get_value())


class Bankroll:
    def __init__(self):
        '''starts as 10000'''
        #self.money = 10000

        try:
            with open('data.csv','r') as file:
                reader = csv.reader(file)
                csv_file = csv.DictReader(file)
                rows = list(csv_file)
                x = rows[len(rows)-1]

                self.money = float(x.get("Bankroll"))

        except FileNotFoundError:
            with open('data.csv', 'w', newline = '') as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Hands_Won", "Hands_Lost", "Bankroll"])
                writer.writerow([datetime.datetime.now(), 0, 0, 10000])
                self.money = 10000


    def close(self, w, l):
        '''enters data in csv file, keeps track of bank'''
        with open('data.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([datetime.datetime.now(), w, l, self.money])


    def get_bankroll(self):
        '''returns money left'''
        return self.money

    def win(self, x):
        '''adds bet amount to bankroll if you win'''
        self.money += x

    def loose(self, x):
        '''removes bet amount from bankroll if you loose'''
        self.money -= x

    def __repr__(self):
        '''overloads bankroll print()'''
        return (f"{self.money}")





class Bet:
    def __init__(self):
        '''minimum bet is 50$, it is your rent for sitting in the table'''
        self.min = 50
        self.amount = self.min

    def get_bet(self):
        '''returns bet amount'''
        return self.amount

    def create(self, x):
        self.amount = x
        return self.amount

    def more(self):
        '''adds min amount to current bet'''
        self.amount += self.min

    def double(self):
        self.amount += self.amount

    def display_bet(self):
        print(f'Current bet is {self.amount}')

    def __repr__(self):
        return (f"{self.amount}")



class Game:
    def __init__(self):
        self.hands_won = 0
        self.hands_lost = 0
        self.bankroll = Bankroll()

    def play(self):
        '''Order of executions'''
        self.clear()
        self.init_deck()
        playing = True

        while playing:


            self.split = False
            self.player_hand = Hand()
            self.dealer_hand = Hand(dealer=True)
            self.bet = Bet()

            self.print_game(open = True)
            self.place_bet()

            for i in range(2):
                self.player_hand.add_card(self.deck.deal())
                self.print_game()
                self.dealer_hand.add_card(self.deck.deal())
                self.print_game()

            while True:

                if self.calculate_split():
                    self.split_hand()
                else:
                    self.hit_stick_double(self.bet, self.player_hand)
                self.dealer_turn()
                self.get_results()
                break

            again = input("Play Again? [Y/N] ")
            while again.lower() not in ["y", "n"]:
                again = input("Please enter Y or N ")
            if again.lower() == "n":
                self.close()
                playing = False


    def hit_stick_double(self, bet, hand, hit = False):
        while hand.get_value() < 21:
            if hit:
                choice = self.choice(h = True)
                if choice in ['hit', 'h']:
                    hand.add_card(self.deck.deal())
                    self.print_game()
                else:
                    self.print_game()
                    break
            else:
                choice = self.choice()
                if choice in ['hit', 'h']:
                    hit = True
                    hand.add_card(self.deck.deal())
                    self.print_game()

                elif choice in ["d", "double"]:
                    hand.add_card(self.deck.deal())
                    bet.double()
                    self.print_game()
                    break
                else:
                    self.print_game()
                    break

    def split_hand(self):
        '''creates two new hands'''
        choice = self.choice(s = True)
        if choice in ['y', 'yes']:
            self.split = True
            cards = self.player_hand.get_cards()
            self.hand_1 = Hand()
            self.bet_1 = Bet()
            self.hand_1.add_card(card = cards[0])
            self.bet_1.create(self.bet.get_bet())
            self.hand_2 = Hand()
            self.bet_2 = Bet()
            self.hand_2.add_card(card = cards[1])
            self.bet_2.create(self.bet.get_bet())
            self.print_game()
            self.hand_1.add_card(self.deck.deal())
            self.hand_2.add_card(self.deck.deal())
            self.print_game()
            self.hit_stick_double(self.bet_1, self.hand_1)
            self.hit_stick_double(self.bet_2, self.hand_2)

        else:
            self.hit_stick_double(self.bet, self.player_hand)
#


    def choice(self, s = False, h = False):
        if s:
            print ("You can split your hand!")
            choice = input("Do you want to split?  [Yes / No] ").lower()
            while choice not in ["y", "n", "Yes", "No"]:
                choice = input("Please enter 'yes', 'no' or (or Y / N  ) ").lower()
            return choice

        if h:
            choice = input("Please choose [Hit / Stick ] ").lower()
            while choice not in ["h", "s", "hit", "stick"]:
                choice = input("Please enter 'hit' or 'stick' (or H/S) ").lower()
            return choice

        else:
            choice = input("Please choose [Hit / Stick / Double] ").lower()
            while choice not in ["h", "s", "d", "hit", "stick", "double"]:
                choice = input("Please enter 'hit' , 'stick' or 'double' (or H/S/D) ").lower()
            return choice


    def clear(self):
        '''Clearing for os system'''
        # windows
        if os.name == 'nt':
            _ = os.system('cls')

        # mac and linux
        else:
            _ = os.system('clear')

    def init_deck(self):
        '''initialices the deck'''

        self.deck = Deck()
        self.deck.shuffle()
        print("Shuffling deck")
        for i in range(int((self.deck.cards_left()) / 6)):
           time.sleep(0.02)
           x = "/"
           print(i*x, end="\r")



    def place_bet(self):
        '''Asks the player if he wants the minimum bet or he wants to raise,
        will raise on 50 dollar intervals,
        will keep asking until he settles for ammount or reaches table limit which is 1000'''

        money = self.bet.get_bet()
        while money < 1000:
            self.print_game()
            print(f"Your bankroll is {self.bankroll} $")

            self.bet.display_bet()

            choice = input("Please choose [Raise or Stay] ").lower()
            while choice not in ["r", "s", "raise", "stay"]:
                choice = input("Please enter 'raise' or 'stay' (orR/S) ").lower()
            if choice in ['raise', 'r']:
                self.bet.more()
            else:
                break

    def calculate_split(self):
        '''calculates if split is possible'''
        cards = self.player_hand.get_cards()
        if cards[0].value == cards[1].value:
            return True


    def dealer_turn(self):
        '''Dealer allways hits untill 17'''
        self.print_game(dealer = True)
        while self.dealer_hand.get_value() < 17:
            self.dealer_hand.add_card(self.deck.deal())
            self.print_game(dealer = True)
            if self.player_is_over(dealer = True):
                print("Dealer Bust!")
                continue


    def get_results(self):
        '''
        Displays the results, if players hand value is bellow and closer to 21 than the dealers he wins, and adds bet to baknroll
        else if values are equal, as long as its bellow 21, its a tie, and you keep your bet.
        else if dealer goes over and you dont, you win and add bet to bankroll.
        else if both go over or any other condition, you loose the bet, like in casino
        '''

        if self.split:
            dealer_hand_value = self.dealer_hand.get_value()
            values = [[self.bet_1.get_bet() , self.bet_2.get_bet()] , [self.hand_1.get_value(), self.hand_2.get_value()]]
            self.print_game()
            self.get_winner(dealer_hand_value, values)

        else:
            player_hand_value = self.player_hand.get_value()
            dealer_hand_value = self.dealer_hand.get_value()
            bet = self.bet.get_bet()
            values =[[bet],[player_hand_value]]
            self.get_winner(dealer_hand_value, values)


    def get_winner(self, dealer_hand_value, values):
        '''analize who the winner is and money won or lost, works for split hand and normal hand'''

        self.print_game(dealer = True)
        print("Final Results:" )

        for i in range(len(values[1])):
            print("Hand:", i+1)

            if values[1][i] == 21 and dealer_hand_value != 21:
                print ("You Win")
                print ("Blackjack pays 3 to 2")
                print (f'collect your {(values[0][i] * 3) / 2}')
                self.hands_won += 1
                self.bankroll.win((values[0][i] * 3) / 2)


            elif (values[1][i] < 21) and (values[1][i] > dealer_hand_value):
                print("You Win!")
                print(f"collect your {values[0][i]} $")
                self.bankroll.win(values[0][i])
                self.hands_won += 1


            elif self.player_is_over(dealer = True) and values[1][i] <= 21:
                print("You Win, Dealer Bust!")
                print(f"collect your {values[0][i]} $")
                self.bankroll.win(values[0][i])
                self.hands_won += 1


            elif (values[1][i] == dealer_hand_value) and (values[1][i] <= 21):
                print("Tie!")

            else:
                print("Dealer Wins!")
                print (f"You loose {values[0][i]} $")
                self.bankroll.loose(values[0][i])
                self.hands_lost += 1



        print(f"Your bankroll is {self.bankroll} $")
        game_over = True

    def print_game(self, dealer = False, open = False):
        '''
        Prints the game, if dealer is false, one of his card is hidden
        if dealer is true he reaveals all his cards_in_deck
        the terminal is renewed everytime the function is called.
        '''
        time.sleep(0.5)
        self.clear()
        width, height = os.get_terminal_size()
    #    print_header()
        self.header()
        self.dealer = dealer
        print("\n---DEALER---")
        self.dealer_hand.display_dealer() if self.dealer else self.dealer_hand.display()

        if open and self.deck.cards_left() < 18:
            self.init_deck()
        else:
            print("/"* self.deck.cards_left())

        print("\n---PLAYER---")
        if self.split:
            print("First Hand")
            self.hand_1.display()
            print ('*'* self.bet_1.get_bet())
            print("Second Hand")
            self.hand_2.display()
            print ('*'* self.bet_2.get_bet())


        else:
            self.player_hand.display()
            self.bet.display_bet()
            print("*"* self.bet.get_bet())



    def player_is_over(self, dealer = False):
        '''Check if dealer or player have busted'''
        self.dealer = dealer

        if self.dealer:
            return self.dealer_hand.get_value() > 21

        return self.player_hand.get_value() > 21


    def close(self):
        '''enters data in csv file, keeps track of bank'''
        self.clear()
        self.header()
        print("Thanks for playing!")
        with open('data.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([datetime.datetime.now(), self.hands_won, self.hands_lost, self.bankroll])
        with open('data.csv', 'r') as file:
            reader = csv.reader(file)
            csv_file = csv.DictReader(file)
            rows = list(csv_file)
            wins = []
            loose = []
            for i in rows:
                wins.append(int(i.get("Hands_Won")))
                loose.append(int(i.get("Hands_Lost")))
            total_wins = reduce(lambda x, y: x + y, wins)
            total_loose = reduce(lambda x, y: x + y, loose)
            hands_played = total_wins + total_loose
            win_percent = int((total_wins / hands_played) * 100)
            loose_percent = int((total_loose / hands_played) * 100)
            print (f"You ar winning {win_percent}% of hands")
            print (f"You are loosing {loose_percent}% of hands")
            average_hand = round((abs(10000 - self.bankroll.get_bankroll())) / hands_played, 2)
            print (f"You are winning an average of {average_hand}$ per hand") if self.bankroll.get_bankroll() >= 10000 \
            else print (f"You are loosing an average of {average_hand}$ per hand")
            print (f"Your bankroll is {self.bankroll}$")



    def header(self):
        width, height = os.get_terminal_size()
        print("#" * width)
        name = "Natural 21"
        m = " " * (int(width/2) - len(name))
        print(m + name + m)
        print("#" * width)





if __name__ == "__main__":
    g = Game()
    try:
        g.play()
    except (KeyboardInterrupt, SystemExit):
        g.close()
