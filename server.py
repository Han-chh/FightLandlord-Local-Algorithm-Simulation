import json
import random
import socket
import sys

from client import Player
from client import Card
from client import Combo

lang = {}  # the map loads the json language
            
def load_lan(lang_type):  # load language json file
    with open(lang_type + ".json", "r", encoding="utf-8") as f:
        global lang
        lang = json.load(f)


def get_lan(info):  # get particular info by keys
    return lang["server"]["sys"] + lang["server"][info]


'''
class Card
    subclass Suits => indicates the suit of the card, whether it is red
    subclass Value => indicates the value, contains name(name of the card displayed, and the abs val)
        init method: to parse the abs value to name
    static objects of different types of suits which has to be constant, static, private
    attributes: val:Value & suit:Suits
    
'''


# static method to create the whole poker cards, which is in order and stored by global constant CARDS
def create_cards():
    cards = []
    # usual cards
    for i in range(1, 14):
        val = Card.Value(i)
        cards.append(Card(val, Card.DIAMOND))
        cards.append(Card(val, Card.HEART))
        cards.append(Card(val, Card.SPADE))
        cards.append(Card(val, Card.CLUB))
    # jokers joker.val is next to 2.val
    joker_r = Card(Card.Value(18, True), Card.JOKER_R, True)
    joker_b = Card(Card.Value(17, True), Card.JOKER_B, True)
    cards.append(joker_r)
    cards.append(joker_b)
    return cards


# global whole poker cards which is in order.
CARDS = create_cards()


# print the whole cards
def print_cards():
    for card in CARDS:
        print(card, end=" ")


# class of the Server
class Server:
    # union of the 3 players' cards (0-indexed)
    whole_game: list = [[], [], []]
    # players list
    players: Player = []
    # remain 3 cards
    remain: Card = []

    # configure the Server
    def __init__(self, players: list):
        self.players = players

    # print different player's cards. Index: which player's card will be displayed(1-indexed). 4 for all players
    def print_player_cards(self, index=4):
        print()
        for i in range(max(index % 4, 1), min(index + 1, 4)):
            print("p" + str(i))
            j = 1
            for card in self.whole_game[i - 1]:
                print("\033[32m" + str(j) + ":" + "\033[0m", end="")
                # print(str(j)+":",end = "")
                print(card, end=" ")
                j += 1
            print(" " + str(len(self.whole_game[i - 1])))
        print()

    # shuffle and distribute the cards
    def __shuf_and_distribute(self):
        print(get_lan("shuffle"))
        cards_played = CARDS.copy()
        random.shuffle(cards_played);
        print(get_lan("shuf_done"))
        self.whole_game[0] = cards_played[0:17]
        self.whole_game[1] = cards_played[17:34]
        self.whole_game[2] = cards_played[34:51]
        self.whole_game[0].sort()
        self.whole_game[1].sort()
        self.whole_game[2].sort()
        self.players[1].player_cards = self.whole_game[0]
        self.players[2].player_cards = self.whole_game[1]
        self.players[3].player_cards = self.whole_game[2]
        print(get_lan("start"))
        return cards_played[51:]

    # contact of server and player. can_play: bool value for whether this contact can play cards.
    def contact(self, player: Player, can_play: bool, is_first=False, greatest_player=None):
        print(get_lan("turn") + player.id + ": ")
        oper = player.oper(can_play, is_first, greatest_player)
        return oper

    # decide who to be the landlord
    def decide_landlord(self):
        start = random.randint(1, 3)  # the first one to be asked
        curr = start
        res = []
        for i in range(3):  # ask each of the player
            res.append(self.contact(self.players[curr], False)[0])
            # circular
            curr += 1
            curr %= 4
            curr = max(curr, 1)
        cnt = res.count(True)  # how many players want to be the landlord
        if cnt == 0:
            # no one wants to be landlord
            return 0

        tmp = start + res.index(True)
        if tmp > 3: tmp = tmp % 4 + 1
        first_call = tmp  # first one to call, circular
        if cnt == 1:
            return first_call
        elif cnt > 0:
            # more than one player want the landlord, so ask for the first call again.
            # if he denies, then the second call is the landlord
            new_res = self.contact(self.players[first_call], False)[0]
            if new_res:
                return first_call
            else:
                first_true = res.index(True)
                tmp = start + res.index(True, first_true + 1)
                if tmp > 3: tmp = tmp % 4 + 1
                second_call = tmp
                return second_call

    # method for the preparation. Including shuffle, distribute, and decision of landlord
    def prep(self):
        print(get_lan("prep"))
        self.remain = self.__shuf_and_distribute()

        server.print_player_cards()
        print(get_lan("landlord_decision"))
        landlord_pos = self.decide_landlord()
        return landlord_pos

    # Single Round of the game
    class Round:
        server = None
        curr_player: Player = None
        first_player: Player = None
        greatest_player: Player = None
        pass_cnt: int = 0

        # initialize the first player
        def __init__(self, first_player: Player, server):
            self.first_player = first_player
            self.greatest_player = first_player
            self.curr_player = first_player
            self.server = server

        # circular turn of the players
        def circular_next(self):
            tmp = self.curr_player.player_pos + 1
            if tmp > 3: tmp = tmp % 4 + 1
            self.curr_player = server.players[tmp]  # circular successor

        # judge the winner
        def judge_win(self):
            return self.curr_player.total_cards() == 0

        # display the cards played
        def display_cards_played(self, player):

            print(player.id + ": ", end="")
            if player.curr_combo is not None:
                for card in player.curr_combo.cards_played_displayed:
                    print(card, end=" ")
                print(" " + player.curr_combo.combo_name)
            else: print()

    # process the operation
    def processing_order(self, single_round, is_first):
        if not is_first:
            print("greatest: ",end="")
            single_round.display_cards_played(single_round.greatest_player)
        if is_first:
            g_player = None
        else:
            g_player = single_round.greatest_player
        res = self.contact(single_round.curr_player, True, is_first, g_player)
        # res[0]: whether there are cards; res[1] the combo object
        if not res[0]:
            single_round.pass_cnt += 1
        else:
            single_round.pass_cnt = 0
            single_round.greatest_player = single_round.curr_player

        single_round.display_cards_played(single_round.curr_player)

        self.print_player_cards()

    # method for the game process
    def play(self, landlord_pos):
        if not landlord_pos:
            print(get_lan("nolandlord"))
            self.init_game()
            self.play(self.prep())
        else:
            print(get_lan("remain"), end=" ")
            # display the remain cards
            for card in self.remain: print(card, end=" ")
            print()
            # display the groups
            self.players[landlord_pos].is_landlord = True
            landlord = self.players[landlord_pos]  # landlord
            print(get_lan("landlord") + landlord.id)
            print(get_lan("farmer"), end="")
            farmers = []  # all the farmers' id
            for player in self.players[1:]:
                if not player.is_landlord:
                    farmers.append(player.id)
                    print(player.id, end=" ")
            print()
            # insert the remain cards to landlords' cards. Can be optimised by Bi Search.
            for card in self.remain:
                flag = False  # determine whether card is inserted
                for i in range(landlord.total_cards()):
                    if card <= landlord.player_cards[i]:
                        landlord.player_cards.insert(i, card)
                        flag = True
                        break
                if not flag:
                    landlord.player_cards.insert(landlord.total_cards(), card)
            self.print_player_cards()
            print(get_lan("begin"))
            single_round = self.Round(landlord, self)  # create round object
            while not single_round.judge_win():
                self.processing_order(single_round, True)
                while not single_round.judge_win() and not single_round.pass_cnt == 2:
                    single_round.circular_next()
                    self.processing_order(single_round, False)
                if single_round.judge_win(): break

                single_round.circular_next()
                single_round.curr_player = single_round.greatest_player
                single_round.pass_cnt = 0
            print(get_lan("end"))
            if single_round.curr_player.is_landlord:
                print(f"{get_lan("landlord_win")}({landlord.id})")
            else:
                print(f"{get_lan("farmer_win")}({farmers[0]} {farmers[1]})")

    def init_game(self):
        for cards in self.whole_game: cards.clear()
        for player in self.players[1:]: player.init_game()
        pass


if __name__ == "__main__":

    load_lan("lan_ch")
    print(get_lan('intro'))

    while True:
        order = input()
        if order == "p" or order == "P":
            # 3 players
            p1 = Player(1, None)
            p2 = Player(2, None)
            p3 = Player(3, None)
            server = Server([None, p1, p2, p3])  # 1-indexed player list
            server.play(server.prep())
            server.init_game()
            print(get_lan('intro'))
        elif order == "e" or order == "E":
            exit()
        else:
            print(get_lan("invalid"))
