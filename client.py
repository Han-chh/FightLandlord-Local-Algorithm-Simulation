import json
import socket

lang = {}


def load_lan(lang_type):
    with open(lang_type + ".json", "r", encoding="utf-8") as f:
        global lang
        lang = json.load(f)


def get_lan(info):
    print(lang)
    return lang["client"][info]


def find_server_ip():
    UDP_PORT = 41234
    BROADCAST_IP = '255.255.255.255'

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(3)  # 等待响应 3 秒

    message = "DISCOVER_SERVER".encode('utf-8')
    sock.sendto(message, (BROADCAST_IP, UDP_PORT))
    print(f"{get_lan("UDPBroadcast_to_find_server_ip")} {BROADCAST_IP}:{UDP_PORT}")

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            response = data.decode('utf-8')
            if response.startswith("SERVER_HERE"):
                ws_port = response.split(':')[1]
                print(f"{"server_found"} {addr[0]}:{ws_port}")
                return addr[0], int(ws_port)
    except socket.timeout:
        print(get_lan("server_not_found"))
    finally:
        sock.close()



class Card:
    class Suits:

        suit = ""
        is_red = True

        def __init__(self, suit, is_red):
            self.suit = suit
            self.is_red = is_red

    class Value:
        name = ""
        val = 0

        def __init__(self, val=0, joker_flag=False):
            self.joker_flag = joker_flag
            self.val = val
            if joker_flag:
                self.name = "JOKER"
            elif val == 1:
                self.name = "A"
                self.val = 14  # to be able to concatenate k
            elif val == 2:
                self.name = "2"
                self.val = 16  # can't be concatenated to A
            elif val == 11:
                self.name = "J"
            elif val == 12:
                self.name = "Q"
            elif val == 13:
                self.name = "K"
            else:
                self.name = str(val)

    suit = Suits("", True)
    val = Value(0)
    joker_flag = False

    DIAMOND = Suits("♦", True)
    HEART = Suits("♥", True)
    SPADE = Suits("♠", False)
    CLUB = Suits("♣", False)
    JOKER_R = Suits("", True)
    JOKER_B = Suits("", False)

    '''
        params = value: value of the card, suit: suit of the card, joker_flag: whether it is joker
    '''

    def __init__(self, value: Value, suit: Suits, joker_flag=False):
        self.val = value
        self.suit = suit
        self.joker_flag = joker_flag

    # to_str magic method to make the cards can be displayed
    def __str__(self):

        if self.suit.is_red:
            return "\033[1;31m" + self.suit.suit + self.val.name + "\033[0m"
        else:
            return self.suit.suit + self.val.name

    # compare the single card
    def __lt__(self, other):
        return self.val.val < other.val.val

    def __eq__(self, other):
        return self.val.name == other.val.name

    def __le__(self, other):
        return self < other or self == other

class Combo:
    combo_cards = []
    combo_name = ""
    # map, key: the times the card occurs, val: 2d-list, the cards, every element contains same cards
    combo_map_list = list()
    max_item = None
    rank = 0
    gap = 0
    cards_played_displayed = None

    def __init__(self, combo_cards):
        combo_map = dict()
        self.combo_cards = combo_cards
        i = 0
        while i < len(combo_cards):  # iterate combo_cards
            model = combo_cards[i]  # model: the card pattern to be matched
            cnt = 0
            same_list = list()  # the same cards list
            while i < len(combo_cards) and combo_cards[i] == model:
                same_list.append(combo_cards[i])
                cnt += 1
                i += 1
            if not combo_map.__contains__(cnt):
                combo_map[cnt] = list()
            combo_map[cnt].append(same_list)
        items = combo_map.items()
        self.combo_map_list = list(items)  # list of tuples, tuple[0] the num of same cards,tuple[1]list of lists
        # descending order
        self.combo_map_list.sort(reverse=True)
        self.max_item = self.combo_map_list[0]
        self.cards_played_displayed = self.get_cards_played_displayed()
        # for pair in self.combo_map_list:
        #     print("key= " + str(pair[0]), end="")
        #     for card_list in pair[1]:
        #         for card in card_list: print(card, end=" ")
        #         print("   ", end="")
        # print()

    def get_cards_played_displayed(self):
        l = list()
        for pair in self.combo_map_list:
            for card_list in pair[1]:
                for card in card_list: l.append(card)
        return l

    # deduce the combo name, return the name deduced or None if the combo is illegal
    def deduce_name(self):
        '''
        len(combo_map_list): how many different types of cards of the same amount here
        max_item: the item of the highest cards of the same amount
        max_item[0]: how many group of cards of the same amount
        max_item[1]: the list of cards
        '''
        combo_map_list = self.combo_map_list
        max_item = self.max_item

        is_single: bool = len(combo_map_list) == 1 and max_item[0] == 1 and len(max_item[1]) == 1
        is_pair: bool = (len(combo_map_list) == 1 and max_item[0] == 2 and len(max_item[1]) == 1
                         and not max_item[1][0][0].joker_flag and not max_item[1][0][1].joker_flag)
        is_triple: bool = len(combo_map_list) == 1 and max_item[0] == 3 and len(max_item[1]) == 1
        is_three_and_single: bool = (len(combo_map_list) == 2 and max_item[0] == 3 and len(max_item[1]) == 1
                                     and combo_map_list[1][0] == 1 and len(combo_map_list[1][1]) == 1)
        is_three_and_pair: bool = (len(combo_map_list) == 2 and max_item[0] == 3 and len(max_item[1]) == 1
                                   and combo_map_list[1][0] == 2 and len(combo_map_list[1][1]) == 1)
        is_continuous_single: bool = len(combo_map_list) == 1 and max_item[0] == 1 and len(max_item[1]) >= 5
        is_continuous_pair: bool = len(combo_map_list) == 1 and max_item[0] == 2 and len(max_item[1]) >= 3
        is_airplane: bool = len(combo_map_list) == 1 and max_item[0] == 3 and len(max_item[1]) >= 2
        is_airplane_single: bool = (len(combo_map_list) == 2 and max_item[0] == 3 and len(max_item[1]) >= 2
                                    and combo_map_list[1][0] == 1 and len(combo_map_list[1][1]) == len(max_item[1]))
        is_airplane_pair: bool = (len(combo_map_list) == 2 and max_item[0] == 3 and len(max_item[1]) >= 2
                                  and combo_map_list[1][0] == 2 and len(combo_map_list[1][1]) == len(max_item[1]))
        is_bomb: bool = len(combo_map_list) == 1 and max_item[0] == 4 and len(max_item[1]) == 1
        is_four_and_double_single: bool = (len(combo_map_list) == 2 and max_item[0] == 4 and len(max_item[1]) == 1
                                           and combo_map_list[1][0] == 1 and len(combo_map_list[1][1]) == 2)
        is_four_and_double_pair: bool = (len(combo_map_list) == 2 and max_item[0] == 4 and len(max_item[1]) == 1
                                         and combo_map_list[1][0] == 2 and len(combo_map_list[1][1]) == 2)
        is_rocket: bool = (len(combo_map_list) == 1 and max_item[0] == 2 and len(max_item[1]) == 1
                           and max_item[1][0][0].joker_flag and max_item[1][0][1].joker_flag)
        combo_text = lang["combos"]
        # determine whether the highest order cards is continuous
        is_continuous = True
        # max_item[1] is list of lists of cards
        pattern = self.max_item[1][0][0].val.val - 1
        # gap of the highest cards list
        for card_list in self.max_item[1]:
            if card_list[0].val.val != pattern + 1:
                is_continuous = False
                break
            self.gap += 1
            pattern += 1
        if not is_continuous: return None
        if is_single:
            self.combo_name = combo_text["single"]
        elif is_pair:
            self.combo_name = combo_text["pair"]
        elif is_triple:
            self.combo_name = combo_text["triple"]
        elif is_three_and_single:
            self.combo_name = combo_text["three_and_single"]
        elif is_three_and_pair:
            self.combo_name = combo_text["three_and_pair"]
        elif is_continuous_single:
            self.combo_name = combo_text["continuous_single"]
        elif is_continuous_pair:
            self.combo_name = combo_text["continuous_pair"]
        elif is_airplane:
            self.combo_name = combo_text["airplane"]
        elif is_airplane_single:
            self.combo_name = combo_text["airplane_single"]
        elif is_airplane_pair:
            self.combo_name = combo_text["airplane_pair"]
        elif is_four_and_double_single:
            self.combo_name = combo_text["four_and_double_single"]
        elif is_four_and_double_pair:
            self.combo_name = combo_text["four_and_double_pair"]
        elif is_bomb:
            self.combo_name = combo_text["bomb"]
            self.rank = 1
        elif is_rocket:
            self.combo_name = combo_text["rocket"]
            self.rank = 2
        else:
            return None
        return self.combo_name

    # determine whether a combo is less than another
    def is_legal(self, other):
        if other is None: return True
        if self.rank > other.rank:
            return True
        elif self.combo_name != other.combo_name:
            return False
        elif self.gap != other.gap:
            return False
        elif self.max_item[1][0][0].val.val > other.max_item[1][0][0].val.val:
            return True
        return False


class Player:
    playing_state = False  # whether legal for send an operation
    player_pos = 0
    player_cards = list()
    is_landlord = False
    id = ""
    curr_combo = None

    def __init__(self, pos, player_cards):
        load_lan("lan_ch")
        self.player_pos = pos
        self.player_cards = player_cards
        self.id = "玩家" + str(pos)
        pass

    def init_game(self):
        self.playing_state = False  # whether legal for send an operation
        self.player_cards.clear()
        self.is_landlord = False
        self.curr_combo = None

    # total num of cards
    def total_cards(self):
        return len(self.player_cards)

    def show_all_cards(self):
        print(self.id + ": ", end="")
        for card in self.player_cards:
            print(card, end=" ")
        print(self.total_cards())

    # choose cards, return None means the cards chosen is illegal
    def choose_cards(self, indices_chosen: list, greatest_player):
        cards_played = []
        # index_chosen must be sorted
        # index is 1-indexed
        indices_chosen.sort()

        for index in indices_chosen:
            i = int(index)
            cards_played.append(self.player_cards[i - 1])
        combo = Combo(sorted(cards_played))
        if greatest_player is None:
            curr_combo = None
        else:
            curr_combo = greatest_player.curr_combo
        if not combo.deduce_name() or not combo.is_legal(curr_combo):
            return None
        else:
            del_cnt = 0
            # delete cards
            for index in indices_chosen:
                i = int(index)
                self.player_cards.pop(i - 1 - del_cnt)
                del_cnt += 1
            return combo

    # ask for operations res[0] indicates pass or play, res[1] indicates the cards played
    def oper(self, can_play, is_first, greatest_player=None):
        res = [False, None]
        if can_play:
            choose_indices = list()

            print(get_lan("choose_cards"))
            op = input()
            while True:
                if op == "N" or op == "n":
                    if is_first:
                        print(get_lan("invalid"))
                    else:
                        res[0] = False
                        self.curr_combo = None
                        return res
                elif op == "Y" or op == "y":
                    if len(choose_indices) == 0:
                        print(get_lan("invalid"))
                    else:
                        res[1] = self.choose_cards(choose_indices, greatest_player)
                        if res[1] is None:
                            print(get_lan("illegal"))
                        else:
                            self.curr_combo = res[1]
                            res[0] = True
                            return res
                elif op.strip() == "":
                    print(get_lan("invalid"))
                else:
                    # use regular expression to process and validate the operation
                    total = self.total_cards()
                    # validate operation
                    try:
                        index = int(op)
                        if index < 1 or index > total:
                            print(get_lan("invalid"))
                        else:
                            # indices is one indexed
                            if choose_indices.__contains__(index):
                                choose_indices.remove(index)
                            else:
                                choose_indices.append(index)
                    except ValueError:
                        print(get_lan("invalid"))

                op = input()
        else:
            op = input(get_lan("ask"))
            while True:
                if op == "N" or op == 'n':
                    res[0] = False
                    break
                elif op == "Y" or op == 'y':
                    res[0] = True
                    break
                else:
                    op = input(get_lan("invalid"))
        return res


if __name__ == "__main__":
    load_lan("lan_ch")
    print(get_lan("intro"))
    (ip, port) = find_server_ip()
