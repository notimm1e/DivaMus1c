import nekos, akinator
try:
    from akinator.async_aki import Akinator as async_akinator
except (AttributeError, ModuleNotFoundError):
    from akinator import AsyncAkinator

    class async_akinator:

        def __init__(self, *args, **kwargs):
            self.__dict__["aki"] = AsyncAkinator(*args, **kwargs)

        def __getattr__(self, k):
            try:
                return self.__getattribute__(k)
            except AttributeError:
                return getattr(self.aki, k)

        def __setattr__(self, k, v):
            try:
                return setattr(self.aki, k, v)
            except AttributeError:
                self.__dict__[k] = v

print = PRINT


try:
    alexflipnote_key = AUTH["alexflipnote_key"]
    if not alexflipnote_key:
        raise
except:
    alexflipnote_key = None
    print("WARNING: alexflipnote_key not found. Unable to use API to generate images.")
try:
    giphy_key = AUTH["giphy_key"]
    if not giphy_key:
        raise
except:
    giphy_key = None
    print("WARNING: giphy_key not found. Unable to use API to search images.")


class GameOverError(OverflowError):
    pass


# Represents and manages an N-dimensional game of 2048, with many optional settings.
class ND2048(collections.abc.MutableSequence):

    digit_ratio = 1 / math.log2(10)
    spl = b"_"
    __slots__ = ("data", "history", "shape", "flags")

    # Loads a new instance from serialised data
    @classmethod
    def load(cls, data):
        spl = data.split(cls.spl)
        i = spl.index(b"")
        shape = [int(x) for x in spl[:i - 1]]
        flags = int(spl[i - 1])
        spl = spl[i + 1:]
        self = cls(flags=flags)
        self.data = np.frombuffer(b642bytes(spl.pop(0), 1), dtype=np.int8).reshape(shape)
        if not self.data.flags.writeable:
            self.data = self.data.copy()
        if self.flags & 1:
            self.history = deque(maxlen=max(1, int(800 / np.prod(self.data.size) - 1)))
            while spl:
                self.history.append(np.frombuffer(b642bytes(spl.pop(0), 1), dtype=np.int8).reshape(shape))
        return self

    # serialises gamestate data to base64
    def serialise(self):
        s = (self.spl.join(str(i).encode("utf-8") for i in self.data.shape)) + self.spl + str(self.flags).encode("utf-8") + self.spl * 2 + bytes2b64(self.data.tobytes(), 1)
        if self.flags & 1 and self.history:
            s += self.spl + self.spl.join(bytes2b64(b.tobytes(), 1) for b in self.history)
        return s

    # Initializes new game
    def __init__(self, *size, flags=0):
        if not size:
            self.data = None
            self.flags = flags
            return
        elif len(size) <= 1:
            try:
                size = int(size)
            except (ValueError, TypeError):
                size = list(reversed(size))
            else:
                size = [size, size]
        self.data = np.tile(np.int8(0), size)
        if flags & 1:
            # Maximum undo steps based on the size of the game board
            self.history = deque(maxlen=max(1, int(800 / np.prod(size) - 1)))
        self.flags = flags
        self.spawn(max(2, self.data.size // 6), flag_override=0)

    __repr__ = lambda self: self.__class__.__name__ + ".load(" + repr(self.serialise()) + ")"

    # Displays game board for dimensions N <= 4
    def __str__(self):
        m = 64
        a = self.data
        nd = max(3, 1 + int(self.digit_ratio * np.max(a)), 2 + int(-self.digit_ratio * np.min(a)))
        w = len(a) * (nd + 1) - 1
        shape = list(a.shape)
        if a.ndim <= 2:
            if a.ndim == 1:
                a = [a]
            else:
                a = np.moveaxis(a, 0, 1)
            return "+" + ("-" * nd + "+") * shape[0] + "\n" + "\n".join("|" + "|".join(self.display(x, nd) for x in i) + "|\n+" + ("-" * nd + "+") * shape[0] for i in a)
        curr = 3
        horiz = 1
        while a.ndim >= curr:
            w2 = shape[a.ndim - curr - 1]
            c = (w + 1) * w2 - 1
            if c <= m:
                w = c
                horiz += 1
            curr += 2
        if a.ndim <= 4:
            dim = len(a)
            if a.ndim == 3:
                a = np.expand_dims(np.rollaxis(a, 0, 3), 0)
                shape.insert(3, 1)
            else:
                a = np.swapaxes(a, 0, 3)
            horiz = 2
            if horiz > 1:
                return "\n".join("\n".join((("+" + ("-" * nd + "+") * shape[0] + " ") * shape[2])[:-1] + "\n" + " ".join("|" + "|".join(self.display(x, nd) for x in i) + "|" for i in j) for j in k) + "\n" + (("+" + ("-" * nd + "+") * shape[0] + " ") * shape[2])[:-1] for k in a)
            return str(horiz)
        return self.data.__str__()

    # Calulates effective total score (value of a tile 2 ^ x is (2 ^ x)(x - 1)
    score = lambda self: np.sum([(g - 1) * (1 << g) for g in [self.data[self.data > 1].astype(object)]])

    # Randomly spawns tiles on a board, based on the game's settings. May be overridden by the flag_override argument.
    def spawn(self, count=1, flag_override=None):
        try:
            flags = flag_override if flag_override is not None else self.flags
            if 0 not in self:
                raise IndexError
            if flags & 4:
                # Scale possible number spawns to highest number on board
                high = max(4, np.max(self.data)) - 1
                choices = [np.min(self.data[self.data > 0])] + [max(1, i) for i in range(high - 4, high)]
            else:
                # Default 2048 probabilities: 90% ==> 2, 10% ==> 4
                choices = [1] * 9 + [2]
            if flags & 2:
                # May spawn negative numbers if special tiles mode is on
                neg = max(1, np.max(self.data))
                neg = 1 if neg <= 1 else random.randint(1, neg)
                neg = -1 if neg <= 1 else -random.randint(1, neg)
                for i in range(len(choices) >> 2):
                    if neg >= 0:
                        break
                    choices[i + 1] = neg
                    neg += 1
            # Select a list from possible spawns and distribute them into random empty locations on the game board
            spawned = deque(choice(choices) for i in range(count))
            fi = self.data.flat
            empty = [i for i in range(self.data.size) if not fi[i]]
            random.shuffle(empty)
            empty = deque(empty)
            while spawned:
                i = empty.popleft()
                if not fi[i]:
                    fi[i] = spawned.popleft()
        except IndexError:
            raise RuntimeError("Unable to spawn tile.")
        return self

    # Recursively splits the game board across dimensions, then performs a move across each column, returns True if game board was modified
    def recurse(self, it):
        if it.ndim > 1:
            return any([self.recurse(i) for i in it])
        done = modified = False
        while not done:
            done = True
            for i in range(len(it) - 1):
                if it[i + 1]:
                    # If current tile is empty, move next tile into current position
                    if not it[i]:
                        it[i] = it[i + 1]
                        it[i + 1] = 0
                        done = False
                    # If current tile can combine with adjacent tile, add them
                    elif it[i] == it[i + 1] or (it[i + 1] < 0 and it[i]):
                        it[i] += (1 if it[i] >= 0 else -1) * (1 if it[i + 1] >= 0 else -it[i + 1])
                        it[i + 1] = 0
                        done = False
                    elif it[i] < 0:
                        it[i] = it[i + 1] - it[i]
                        it[i + 1] = 0
                        done = False
                if not done:
                    modified = True
        return modified

    # Performs a single move across a single dimension.
    def move(self, dim=0, rev=False, count=1):
        # Creates backup copy of game data if easy mode is on
        if self.flags & 1:
            temp = copy.deepcopy(self.data)
        moved = False
        for i in range(count):
            # Random move selector
            if dim < 0:
                dim = xrand(self.data.ndim)
                rev = xrand(2)
            # Selects a dimension to move against
            it = np.moveaxis(self.data, dim, -1)
            if rev:
                it = np.flip(it)
            m = self.recurse(it)
            if m:
                self.spawn()
            moved |= m
        if moved:
            if self.flags & 1:
                self.history.append(temp)
            # If board is full, attempt a move in both directions of every dimension, and announce game over if none are possible
            if 0 not in self.data:
                valid = False
                for dim in range(self.data.ndim):
                    temp = np.moveaxis(copy.deepcopy(self.data), dim, -1)
                    if self.recurse(temp) or self.recurse(np.flip(temp)):
                        valid = True
                        break
                if not valid:
                    raise GameOverError("Game Over.")
        return moved

    def valid_moves(self):
        valid = 0
        for dim in range(self.data.ndim):
            temp = np.moveaxis(copy.deepcopy(self.data), dim, -1)
            if self.recurse(temp.copy()):
                valid |= 1 << dim * 2
            if self.recurse(np.flip(temp)):
                valid |= 1 << dim * 2 + 1
        return valid

    # Attempt to perform an undo
    def undo(self):
        if self.flags & 1 and self.history:
            self.data = self.history.pop()
            return True

    # Creates a display of a single number in a text box of a fixed length, align centre then right
    def display(self, num, length):
        if num > 0:
            numlength = 1 + int(num * self.digit_ratio)
            out = str(1 << int(num))
        elif num < 0:
            numlength = 2 - int(num * self.digit_ratio)
            out = "×" + str(1 << int(-num))
        else:
            return " " * length
        x = length - numlength
        return " " * (1 + x >> 1) + out + " " * (x >> 1)

    __len__ = lambda self: self.data.__len__()
    __iter__ = lambda self: self.data.flat
    __reversed__ = lambda self: np.flip(self.data).flat
    __contains__ = lambda self, *args: self.data.__contains__(*args)
    __getitem__ = lambda self, *args: self.data.__getitem__(*args)
    __setitem__ = lambda self, *args: self.data.__setitem__(*args)
    __delitem__ = lambda self, *args: self.data.__delitem__(*args)
    insert = lambda self, *args: self.data.insert(*args)
    render = lambda self: self.__str__()


class Text2048(Command):
    time_consuming = True
    name = ["2048", "🎮"]
    description = "Plays a game of 2048 using buttons. Gained points are rewarded as gold."
    usage = "<0:dimension_sizes(4x4)>* <1:dimension_count(2)>? <public{?p}|special_tiles{?s}|insanity_mode{?i}|easy_mode{?e}>*"
    flags = "pies"
    rate_limit = (3, 9)
    reacts = ("⬅️", "➡️", "⬆️", "⬇️", "⏪", "⏩", "⏫", "⏬", "◀️", "▶️", "🔼", "🔽", "👈", "👉", "👆", "👇")
    directions = demap((r.encode("utf-8"), i) for i, r in enumerate(reacts))
    directions[b'\xf0\x9f\x92\xa0'] = -2
    directions[b'\xe2\x86\xa9\xef\xb8\x8f'] = -1
    slash = ("2048",)

    buttons = {
        2: [
            [
                cdict(emoji="▪️", style=2),
                cdict(emoji="⬆️", style=1),
                cdict(emoji="▪️", style=2),
            ],
            [
                cdict(emoji="⬅️", style=1),
                cdict(emoji="💠", style=1),
                cdict(emoji="➡️", style=1),
            ],
            [
                cdict(emoji="▪️", style=2),
                cdict(emoji="⬇️", style=1),
                cdict(emoji="▪️", style=2),
            ],
        ],
        3: [
            [
                cdict(emoji="▪️", style=2),
                cdict(emoji="▪️", style=2),
                cdict(emoji="⬆️", style=1),
                cdict(emoji="▪️", style=2),
                cdict(emoji="▪️", style=2),
            ],
            [
                cdict(emoji="⏪", style=1),
                cdict(emoji="⬅️", style=1),
                cdict(emoji="💠", style=1),
                cdict(emoji="➡️", style=1),
                cdict(emoji="⏩", style=1),
            ],
            [
                cdict(emoji="▪️", style=2),
                cdict(emoji="▪️", style=2),
                cdict(emoji="⬇️", style=1),
                cdict(emoji="▪️", style=2),
                cdict(emoji="▪️", style=2),
            ],
        ],
        4: [
            [
                cdict(emoji="▪️", style=2),
                cdict(emoji="▪️", style=2),
                cdict(emoji="⏫", style=1),
                cdict(emoji="▪️", style=2),
                cdict(emoji="▪️", style=2),
            ],
            [
                cdict(emoji="▪️", style=2),
                cdict(emoji="▪️", style=2),
                cdict(emoji="⬆️", style=1),
                cdict(emoji="▪️", style=2),
                cdict(emoji="▪️", style=2),
            ],
            [
                cdict(emoji="⏪", style=1),
                cdict(emoji="⬅️", style=1),
                cdict(emoji="💠", style=1),
                cdict(emoji="➡️", style=1),
                cdict(emoji="⏩", style=1),
            ],
            [
                cdict(emoji="▪️", style=2),
                cdict(emoji="▪️", style=2),
                cdict(emoji="⬇️", style=1),
                cdict(emoji="▪️", style=2),
                cdict(emoji="▪️", style=2),
            ],
            [
                cdict(emoji="▪️", style=2),
                cdict(emoji="▪️", style=2),
                cdict(emoji="⏬", style=1),
                cdict(emoji="▪️", style=2),
                cdict(emoji="▪️", style=2),
            ],
        ],
    }

    async def _callback_(self, bot, message, reaction, argv, user, perm, vals, **void):
        u_id, mode = list(map(int, vals.split("_", 1)))
        if reaction is not None and u_id != user.id and u_id != 0 and perm < 3:
            return
        spl = argv.split("-")
        size = [int(x) for x in spl.pop(0).split("_")]
        data = None
        if reaction is None:
            return
            # If game has not been started, add reactions and create new game
            # for react in self.directions.a:
            #     r = self.directions.a[react]
            #     if r == -2 or (r == -1 and mode & 1) or r >= 0 and r >> 1 < len(size):
            #         await message.add_reaction(as_str(react))
            g = ND2048(*size, flags=mode)
            data = g.serialise()
            r = -1
            score = 0
        else:
            # Get direction of movement
            data = "-".join(spl).encode("utf-8")
            reac = reaction
            if reac not in self.directions:
                return
            r = self.directions[reac]
            score = 0
            try:
                # Undo action only works in easy mode
                if r == -1:
                    if not mode & 1:
                        return
                    g = ND2048.load(data)
                    if not g.undo():
                        return
                    data = g.serialise()
                # Random moves
                elif r == -2:
                    g = ND2048.load(data)
                    if not g.move(-1, count=16):
                        return
                    data = g.serialise()
                # Regular moves; each dimension has 2 possible moves
                elif r >> 1 < len(size):
                    g = ND2048.load(data)
                    score = g.score()
                    if not g.move(r >> 1, r & 1):
                        return
                    data = g.serialise()
            except GameOverError:
                if u_id == 0:
                    u = None
                elif user.id == u_id:
                    u = user
                else:
                    u = bot.get_user(u_id, replace=True)
                emb = discord.Embed(colour=discord.Colour(1))
                if u is None:
                    emb.set_author(name="@everyone", icon_url=bot.discord_icon)
                else:
                    emb.set_author(**get_author(u))
                emb.description = ("**```fix\n" if mode & 6 else "**```\n") + g.render() + "```**"
                fscore = g.score()
                if r < 0:
                    score = None
                if score is not None:
                    xp = max(0, fscore - score) * 16 / np.prod(g.data.shape)
                    if mode & 1:
                        xp /= math.sqrt(2)
                    elif mode & 2:
                        xp /= 2
                    elif mode & 4:
                        xp /= 3
                    bot.data.users.add_gold(user, xp)
                    rew = await bot.as_rewards(xp)
                    if rew:
                        emb.description += "+" + rew
                emb.set_footer(text=f"Score: {fscore}")
                # Clear buttons and announce game over message
                sem = getattr(message, "sem", None)
                if not sem:
                    try:
                        sem = EDIT_SEM[message.channel.id]
                    except KeyError:
                        sem = EDIT_SEM[message.channel.id] = Semaphore(5.15, 256, rate_limit=5)
                async with sem:
                    return await Request(
                        f"https://discord.com/api/{api}/channels/{message.channel.id}/messages/{message.id}",
                        data=dict(
                            content="**```\n2048: GAME OVER```**",
                            embeds=[emb.to_dict()],
                            components=None,
                        ),
                        method="PATCH",
                        authorise=True,
                        aio=True,
                    )
        if data is not None:
            # Update message if gamestate has been changed
            if u_id == 0:
                u = None
            elif user.id == u_id:
                u = user
            else:
                u = bot.get_user(u_id, replace=True)
            colour = await bot.get_colour(u)
            emb = discord.Embed(colour=colour)
            if u is None:
                emb.set_author(name="@everyone", icon_url=bot.discord_icon)
            else:
                emb.set_author(**get_author(u))
            content = "*```callback-fun-text2048-" + str(u_id) + "_" + str(mode) + "-" + "_".join(str(i) for i in size) + "-" + as_str(data) + "\nPlaying 2048...```*"
            emb.description = ("**```fix\n" if mode & 6 else "**```\n") + g.render() + "```**"
            fscore = g.score()
            if r < 0:
                score = None
            if score is not None:
                xp = max(0, fscore - score) * 16 / np.prod(g.data.shape)
                if mode & 1:
                    xp /= math.sqrt(2)
                elif mode & 2:
                    xp /= 2
                elif mode & 4:
                    xp /= 3
                bot.data.users.add_gold(user, xp)
                rew = await bot.as_rewards(xp)
                if rew:
                    emb.description += "+" + rew
            emb.set_footer(text=f"Score: {fscore}")
            create_task(bot.ignore_interaction(message))
            dims = max(2, len(g.data.shape))
            buttons = copy.deepcopy(self.buttons[dims])
            vm = g.valid_moves()
            # print(vm)
            dis = set()
            if dims == 2:
                if not vm & 1:
                    dis.add((0, 1))
                if not vm & 2:
                    dis.add((-1, 1))
                if not vm & 4:
                    dis.add((1, 0))
                if not vm & 8:
                    dis.add((1, -1))
            elif dims == 3:
                if not vm & 1:
                    dis.add((1, 1))
                if not vm & 2:
                    dis.add((-2, 1))
                if not vm & 4:
                    dis.add((2, 0))
                if not vm & 8:
                    dis.add((2, -1))
                if not vm & 16:
                    dis.add((0, 1))
                if not vm & 32:
                    dis.add((-1, 1))
            elif dims == 4:
                if not vm & 1:
                    dis.add((1, 2))
                if not vm & 2:
                    dis.add((-2, 2))
                if not vm & 4:
                    dis.add((2, 1))
                if not vm & 8:
                    dis.add((2, -2))
                if not vm & 16:
                    dis.add((0, 2))
                if not vm & 32:
                    dis.add((-1, 2))
                if not vm & 64:
                    dis.add((2, 0))
                if not vm & 128:
                    dis.add((2, -1))
            for x, y in dis:
                buttons[y][x].disabled = True
            sem = getattr(message, "sem", None)
            if not sem:
                try:
                    sem = EDIT_SEM[message.channel.id]
                except KeyError:
                    sem = EDIT_SEM[message.channel.id] = Semaphore(5.15, 256, rate_limit=5)
            async with sem:
                return await Request(
                    f"https://discord.com/api/{api}/channels/{message.channel.id}/messages/{message.id}",
                    data=dict(
                        content=content,
                        embeds=[emb.to_dict()],
                        components=restructure_buttons(buttons),
                    ),
                    method="PATCH",
                    authorise=True,
                    aio=True,
                )
        await bot.ignore_interaction(message)

    async def __call__(self, bot, argv, args, user, flags, message, guild, **void):
        # Input may be nothing, a single value representing board size, a size and dimension count input, or a sequence of numbers representing size along an arbitrary amount of dimensions
        if not len(argv.replace(" ", "")):
            size = [4, 4]
        else:
            if "x" in argv:
                size = await recursive_coro([bot.eval_math(i) for i in argv.split("x")])
            else:
                if len(args) > 1:
                    dims = args.pop(-1)
                    dims = await bot.eval_math(dims)
                else:
                    dims = 2
                if dims <= 0:
                    raise ValueError("Invalid amount of dimensions specified.")
                width = await bot.eval_math(" ".join(args))
                size = list(repeat(width, dims))
        if len(size) > 8:
            raise OverflowError("Board size too large.")
        items = 1
        for x in size:
            items *= x
            if items > 256:
                raise OverflowError("Board size too large.")
        # Prepare game settings, send callback message to schedule game start
        mode = 0
        if "p" in flags:
            u_id = 0
            mode |= 8
        else:
            u_id = user.id
        if "i" in flags:
            mode |= 4
        if "s" in flags:
            mode |= 2
        if "e" in flags:
            mode |= 1
        if len(size) <= 2:
            buttons = self.buttons[2]
        elif len(size) == 3:
            buttons = self.buttons[3]
        elif len(size) == 4:
            buttons = self.buttons[4]
        else:
            raise ValueError("Button and board configuration for issued size is not yet implemented.")
        reacts = []
        if mode & 1:
            reacts.append("↩️")
        g = ND2048(*size, flags=mode)
        data = g.serialise()
        u = user
        colour = await bot.get_colour(u)
        emb = discord.Embed(colour=colour)
        if u is None:
            emb.set_author(name="@everyone", icon_url=bot.discord_icon)
        else:
            emb.set_author(**get_author(u))
        content = "*```callback-fun-text2048-" + str(u_id) + "_" + str(mode) + "-" + "_".join(str(i) for i in size) + "-" + as_str(data) + "\nPlaying 2048...```*"
        emb.description = ("**```fix\n" if mode & 6 else "**```\n") + g.render() + "```**"
        emb.set_footer(text="Score: 0")
        await send_with_react(message.channel, content, embed=emb, reacts=reacts, buttons=buttons, reference=message)


class Snake(Command):
    time_consuming = True
    name = ["Snaek", "🐍"]
    rate_limit = (3, 9)
    description = "Plays a game of Snake using buttons!"
    usage = "<dimensions(8x8)>* <public{?p}|insanity_mode{?i}>*"
    flags = "pi"
    slash = True

    buttons = [
        [
            cdict(emoji="▪️", style=2),
            cdict(emoji="⬆️", style=1),
            cdict(emoji="▪️", style=2),
        ],
        [
            cdict(emoji="⬅️", style=1),
            cdict(emoji="💠", style=1, disabled=True),
            cdict(emoji="➡️", style=1),
        ],
        [
            cdict(emoji="▪️", style=2),
            cdict(emoji="⬇️", style=1),
            cdict(emoji="▪️", style=2),
        ],
    ]
    icons = {
        0: "▪",
        1: "🐍",
        2: "🍎",
        4: "🍏",
    }
    playing = {}

    async def __call__(self, bot, message, args, flags, **void):
        if len(args) >= 2:
            size = list(map(int, args[:2]))
        elif args:
            argv = args[0]
            if "x" in argv:
                args = argv.split("x")
                size = list(map(int, args[:2]))
            else:
                size = [int(argv)] * 2
        else:
            size = [8, 8]
        cells = product(size)
        if cells > 199:
            raise OverflowError(f"Board size too large ({cells} > 199)")
        elif cells < 2:
            raise ValueError(f"Board size too small ({cells} < 2)")
        create_task(self.generate_snaek_game(message, size, flags))

    async def _callback_(self, bot, message, reaction, user, vals, perm, **void):
        if message.id not in self.playing:
            return
        u_id = int(vals)
        if u_id != user.id and u_id != 0 and perm < 3:
            return
        emoji = as_str(reaction)
        game = self.playing[message.id]
        if emoji == "⬅️":
            d = (-1, 0)
        elif emoji == "➡️":
            d = (1, 0)
        elif emoji == "⬆️":
            d = (0, -1)
        elif emoji == "⬇️":
            d = (0, 1)
        else:
            return
        d = np.array(d, dtype=np.int8)
        if game.dir is None or np.any(game.dir + d):
            game.dir = d
        await bot.ignore_interaction(message)

    async def generate_snaek_game(self, message, size, flags):
        bot = self.bot
        user = message.author
        cells = np.prod(size)
        try:
            if cells > 160:
                raise KeyError
            bot.cache.emojis[881073412297068575]
        except KeyError:
            tails = "💙💜❤🧡💛💚"
        else:
            ids = (
                797359354314620939,
                797359351509549056,
                797359341157482496,
                797359328826490921,
                797359322773454870,
                797359309121519626,
                797359306542284820,
                797359273914138625,
            )
            tails = [f"<a:_:{e}>" for e in ids]
            self.icons[1] = f"<a:_:881073412297068575>"

        def snaek_bwain(game):
            output = ""
            for y in game.grid.T:
                line = ""
                for x in y:
                    if x >= 0:
                        line += self.icons[x]
                    else:
                        i = (x - game.tick) % len(tails)
                        line += tails[i]
                output += line + "\n"
            return output
        
        def spawn_apple(game):
            p = tuple(xrand(x) for x in game.size)
            for i in range(cells * 16):
                if not game.grid[p]:
                    break
                p = tuple(xrand(x) for x in game.size)
            else:
                return
            t = 2
            if "i" in flags and xrand(2):
                t = 4
            grid[p] = t

        pos = tuple(x // 2 - (0 if x & 1 else random.randint(0, 1)) for x in size)
        game = cdict(
            size=size,
            grid=np.zeros(size, dtype=np.int8),
            pos=pos,
            tick=0,
            dir=None,
            len=1,
            alive=True,
        )
        grid = game.grid
        grid[game.pos] = 1
        spawn_apple(game)

        u_id = user.id if "p" not in flags else 0
        colour = await bot.get_colour(user)
        description = f"```callback-fun-snake-{u_id}-\nPlaying Snake...```"
        embed = discord.Embed(
            colour=colour,
            title="🐍 Snake 🐍",
            description=description + snaek_bwain(game),
        )
        embed.set_author(**get_author(user))
        embed.set_footer(text="Score: 0")
        message = await send_with_reply(None, message, embed=embed, buttons=self.buttons)
        self.playing[message.id] = game
        channel = message.channel

        while game.alive:
            if game.dir is not None:
                grid[grid < 0] += 1
                grid[game.pos] = 1 - game.len
                game.pos = tuple(game.dir + game.pos)
                if np.min(game.pos) < 0:
                    game.alive = False
                    break
                try:
                    colliding_with = grid[game.pos]
                except IndexError:
                    game.alive = False
                    break
                if colliding_with == 4 and game.len < cells:
                    spawn_apple(game)
                    spawn_apple(game)
                elif colliding_with == 2 and game.len < cells:
                    game.len += 1
                    spawn_apple(game)
                elif colliding_with < 0:
                    game.alive = False
                    break
                grid[game.pos] = 1
                embed.description = description + snaek_bwain(game)
                embed.set_footer(text=f"Score: {game.len - 1}")
                await message.edit(embed=embed)
                tailc = np.sum(game.grid < 0)
                if tailc >= cells - 1:
                    rew = cells ** 2 / 32 * 4
                    if "i" in flags:
                        rew /= 4
                    if rew >= 1:
                        s = await bot.as_rewards(rew, 0)
                        bot.data.users.add_diamonds(user, rew)
                    else:
                        rew *= 1024
                        s = await bot.as_rewards(rew)
                        bot.data.users.add_gold(user, rew)
                    await send_with_reply(None, message, f"{user.mention}, congratulations, **you won**! You earned {s}!")
                    break
                if tailc:
                    if len(tails) == 6:
                        game.tick += 2
                    else:
                        game.tick += len(tails) // 2 + 2
                    game.tick %= len(tails)
            await asyncio.sleep(1)
        
        if not game.alive:
            rew = (np.sum(game.grid < 0) ** 2 + 1) * 32
            if "i" in flags:
                rew /= 4
            s = await bot.as_rewards(rew)
            bot.data.users.add_gold(user, rew)
            await send_with_reply(None, message, f"{user.mention}, **game over**! You earned {s}.")
        else:
            game.alive = False
        self.playing.pop(message.id, None)


class SlotMachine(Command):
    name = ["Slots"]
    description = "Plays a slot machine game. Costs gold to play, can yield gold and diamonds."
    usage = "<bet{50}>? <skip_animation{?s}>?"
    flags = "s"
    rate_limit = (5, 10)
    emojis = {
        "❤️": 20,
        "🍒": 6,
        "💎": None,
        "🍎": 4,
        "🍇": 5,
        "🍋": 2,
        "🍉": 1,
        "🍌": 3,
    }
    slash = ("Slots",)

    def select(self):
        x = random.random()
        if x < 1 / 32:
            return "💎"
        elif x < 3 / 32:
            return "❤️"
        return choice("🍒🍎🍇🍋🍉🍌")

    def generate(self, rate=0.5, count=3):
        x = random.random()
        if x < rate ** sqrt(5):
            count = 3
        elif x < rate:
            count = 2
        else:
            count = 1
        out = alist((self.select(),) * count)
        while len(out) < 3:
            out.append(choice(self.emojis))
        return shuffle(out)

    async def as_emojis(self, wheel):
        out = ""
        for item in wheel:
            if item is None:
                out += await create_future(self.bot.data.emojis.emoji_as, "slot_machine.gif")
            else:
                out += item
        return out

    async def __call__(self, argv, user, flags, **void):
        b1 = 50
        if argv:
            bet = await self.bot.eval_math(argv)
            if bet < b1:
                raise ValueError(f"Minimum bet is {b1} coins.")
        else:
            bet = b1
        if not bet <= self.bot.data.users.get(user.id, {}).get("gold", 0):
            raise OverflowError("Bet cannot be greater than your balance.")
        self.bot.data.users.add_gold(user, -bet)
        skip = int("s" in flags)
        return f"*```callback-fun-slotmachine-{user.id}_{bet}_{skip}-\nLoading Slot Machine...```*"

    async def _callback_(self, bot, message, reaction, user, perm, vals, **void):
        spl = list(map(int, vals.split("_", 2)))
        if len(spl) < 3:
            spl.append(0)
        u_id, bet, skip = spl
        if reaction is None or as_str(reaction) == "⤵️":
            if reaction is None:
                create_task(message.add_reaction("⤵️"))
                user = await bot.fetch_user(u_id)
            else:
                if bet > bot.data.users.get(user.id, {}).get("gold", 0):
                    raise OverflowError("Bet cannot be greater than your balance.")
                bot.data.users.add_gold(user, -bet)
            rate = 0.5 - max(0, min(1, ((bet - 64) / 4032))) / 14
            wheel_true = self.generate(rate)
            wheel_display = [None] * 3 if not skip else wheel_true
            wheel_order = deque(shuffle(range(3))) if not skip else deque((0, ))
            colour = await bot.get_colour(user)
            emb = discord.Embed(colour=colour).set_author(**get_author(user))
            if not skip:
                async with Delay(2):
                    emoj = await self.as_emojis(wheel_display)
                    gold = bot.data.users.get(user.id, {}).get("gold", 0)
                    bets = await bot.as_rewards(bet)
                    bals = await bot.as_rewards(gold)
                    emb.description = f"```css\n[Slot Machine]```{emoj}\nBet: {bets}\nBalance: {bals}"
                    await message.edit(content=None, embed=emb)
            ctx = Delay(1) if not skip else emptyctx
            while wheel_order:
                async with ctx:
                    i = wheel_order.popleft()
                    wheel_display[i] = wheel_true[i]
                    if not wheel_order:
                        gold = diamonds = 0
                        start = f"```callback-fun-slotmachine-{user.id}_{bet}-\n"
                        if wheel_true[0] == wheel_true[1] == wheel_true[2]:
                            gold = self.emojis[wheel_true[0]]
                            if gold is None:
                                diamonds = bet / 5
                            else:
                                gold *= bet
                        bot.data.users.add_diamonds(user, diamonds)
                        bot.data.users.add_gold(user, gold)
                        rewards = await bot.as_rewards(diamonds, gold)
                        end = f"\nRewards:\n{rewards}\n"
                    else:
                        start = "```ini\n"
                        end = ""
                    emoj = await self.as_emojis(wheel_display)
                    gold = bot.data.users.get(user.id, {}).get("gold", 0)
                    bets = await bot.as_rewards(bet)
                    bals = await bot.as_rewards(gold)
                    emb.description = f"{start}[Slot Machine]```{emoj}\nBet: {bets}\nBalance: {bals}{end}"
                    await message.edit(embed=emb)


barter_values = demap(
    enchanted_book=0,
    enchanted_iron_boots=1,
    splash_fire_resistance=2,
    fire_resistance=3,
    water_bottle=4,
    iron_nugget=5,
    ender_pearl=6,
    string=7,
    nether_quartz=8,
    obsidian=9,
    crying_obsidian=10,
    fire_charge=11,
    leather=12,
    soul_sand=13,
    nether_brick=14,
    spectral_arrow=15,
    gravel=16,
    blackstone=17,
)
barter_weights = {
    0: (5, 1, 1),
    1: (8, 1, 1),
    2: (8, 1, 1),
    3: (8, 1, 1),
    4: (10, 1, 1),
    5: (10, 10, 36),
    6: (10, 2, 4),
    7: (20, 3, 9),
    8: (20, 5, 12),
    9: (40, 1, 1),
    10: (40, 1, 3),
    11: (40, 1, 1),
    12: (40, 2, 4),
    13: (40, 2, 8),
    14: (40, 2, 8),
    15: (40, 6, 12),
    16: (40, 8, 16),
    17: (40, 8, 16),
}
barter_seeding = []
for i, d in barter_weights.items():
    barter_seeding.extend((i,) * d[0])
barter_seeding = np.array(barter_seeding, dtype=np.uint32)
barter_lowers = np.array([d[1] for d in barter_weights.values()], dtype=np.uint32)
barter_uppers = np.array([d[2] for d in barter_weights.values()], dtype=np.uint32) + 1


class Barter(Command):
    description = "Simulates a Minecraft Piglin barter. Uses gold ingots; see ~shop and ~bal for more!"
    usage = "<amount>"
    rate_limit = 1

    async def __call__(self, bot, channel, message, user, argv, **void):
        if not argv:
            amount = 1
        else:
            amount = await bot.eval_math(argv)
        ingots = bot.data.users.get(user.id, {}).get("ingots", 0)
        if amount > ingots:
            raise OverflowError(f"Barter amount cannot be greater than your balance ({amount} > {ingots}). See ~shop for more information.")
        elif not amount >= 1:
            raise ValueError("Please input a valid amount of ingots.")
        data = bot.data.users[user.id]
        data["ingots"] -= amount
        if amount >= 18446744073709551616:
            dtype = np.float80
        elif amount >= 4294967296:
            dtype = np.uint64
        else:
            dtype = np.uint32
        itype = np.uint64 if dtype is not np.uint32 else np.uint32
        # ftype = np.float64 if dtype is not np.uint32 else np.float32
        totals = np.zeros(len(barter_weights), dtype=dtype)
        rand = np.random.default_rng(ts_us())
        if amount > 16777216:
            for i in range(16):
                count = 1048576
                seeds = await create_future(rand.integers, 0, len(barter_seeding), size=count, dtype=itype)
                ids = barter_seeding[seeds]
                counts = await create_future(rand.integers, barter_lowers[ids], barter_uppers[ids], dtype=itype)
                counts = counts.astype(dtype)
                await create_future(np.add.at, totals, ids, counts)
            mult, amount = divmod(amount, 16777216)
            if not is_finite(amount):
                amount = 0
            mult = dtype(mult)
            totals = np.multiply(totals, mult, out=totals)
        else:
            mult = 1
        for i in range(amount + 1048575 >> 20):
            count = min(1048576, amount - i * 1048576)
            seeds = await create_future(rand.integers, 0, len(barter_seeding), size=count, dtype=itype)
            ids = barter_seeding[seeds]
            counts = await create_future(rand.integers, barter_lowers[ids], barter_uppers[ids], dtype=itype)
            counts = counts.astype(dtype)
            await create_future(np.add.at, totals, ids, counts)
        rewards = deque()
        data.setdefault("minecraft", {})
        for i, c in enumerate(totals):
            if c:
                with suppress(TypeError, OverflowError, ValueError):
                    c = round_random(c)
                try:
                    data["minecraft"][i] += c
                except KeyError:
                    data["minecraft"][i] = c
                s = await create_future(bot.data.emojis.emoji_as, barter_values[i] + ".gif")
                if c != 1:
                    s += f" {c}"
                rewards.append(s)
        out = "\n".join(rewards)
        footer = thumbnail = None
        if amount == 1:
            w = barter_weights[ids[0]][0]
            p = round(w * 100 / 459, 7)
            footer = cdict(
                text=f"{w} in 459 ({p}%) chance",
            )
            thumbnail = await create_future(bot.data.emojis.get, barter_values[ids[0]] + ".gif")
            thumbnail = str(thumbnail.url)
        bot.send_as_embeds(
            channel,
            out,
            footer=footer,
            thumbnail=thumbnail,
            reference=message,
        )


class Uno(Command):
    description = "Play a game of UNO with me, or with friends!"
    rate_limit = 2

    async def __call__(self, bot, message, user, flags, **void):
        # players ~ hands ~ current-card
        h = self.hand_repr([self.sort(shuffle(self.deck)[:7])])
        content = f"```callback-fun-uno-[{user.id}]_{h}_[]_0_Z_0_0_-\nUNO game prepared:```"
        c = await bot.get_colour(user)
        embed = discord.Embed(colour=c)
        embed.title = "Current players"
        embed.description = "👑 " + user.mention
        embed.set_footer(text="Click ✋ to join, ✅ to start!")
        await send_with_react(
            message.channel,
            content,
            embed=embed,
            buttons=[[cdict(emoji="✋", style=1), cdict(emoji="✅", style=3)]],
        )

    deck = [c + "0" for c in "RYGB"] + ([f"{c}{i}" for c in "RYGB" for i in range(1, 10)] + [c + t for c in "RYGB" for t in "SRD"]) * 2 + ["WX", "WY"] * 4
    symbols = {
        "Y": " ",
        "X": " ",
        "S": "🚫",
        "R": "🔄",
        "D": "‼",
    }
    colours = dict((
        ("R", "🟥"),
        ("Y", "🟨"),
        ("G", "🟩"),
        ("B", "🟦"),
        ("W", "🔳"),
    ))

    def uno_emoji(self, v):
        if v.isnumeric():
            return v + as_str(b"\xef\xb8\x8f\xe2\x83\xa3")
        return self.symbols[v]

    card_repr = lambda self, c: self.colours[c[0]] + self.uno_emoji(c[1:])
    hand_repr = lambda self, hands: "x".join("".join(s) for s in hands)
    played_repr = lambda self, played: "".join(played)

    def sort(self, hand):
        hand.sort(key=lambda c: (int(c[1]) if c[1].isnumeric() else 256 - ord(c[1])) * len(self.colours) + (list(self.colours).index(c[0]) if c[0] != "W" else 4096))
        return hand

    async def _callback_(self, message, reaction, user, vals, perm, **void):
        if not reaction:
            return
        bot = self.bot
        vals = vals.split("_")
        players = orjson.loads(vals[0])
        hands = [list(chain(x + y for x, y in zip(s[::2], s[1::2]))) for s in vals[1].split("x")]
        winners = orjson.loads(vals[2])
        turn = int(vals[3])
        last = vals[4]
        td = 1 if vals[5] == "0" else -1
        draw = int(vals[6])
        played = list(chain(x + y for x, y in zip(vals[7][::2], vals[7][1::2])))
        r = as_str(reaction)
        print(user, r, players, hands, winners, turn, last, td, draw, played)
        if r == "✋":
            # Joining a game
            if user.id not in players and last == "Z":
                # Joining as a new player
                players.append(user.id)
                hand = shuffle(self.deck)[-7:]
                self.sort(hand)
                hands.append(hand)

                content = f"```callback-fun-uno-{players}_{self.hand_repr(hands)}_[]_0_Z_0_0_-\nUNO game prepared:```"
                embed = message.embeds[0]
                embed.description = "\n".join(("👑 ", "▪️ ")[bool(i)] + user_mention(u) for i, u in enumerate(players))
                embed.set_footer(text="Click ✋ to join, ✅ to start!")
                s = ""
                for c in hand:
                    s += await create_future(bot.data.emojis.emoji_as, c + ".png")
                c = await bot.get_colour(user)
                emb = discord.Embed(
                    colour=c,
                    description=f"Here is your deal hand. Please wait for {user_mention(players[0])} to begin the game!",
                )

                create_task(interaction_response(
                    bot=bot,
                    message=message,
                    content=s,
                    embed=emb,
                ))
                return await message.edit(content=content, embed=embed)
            # Already joined
            hand = hands[players.index(user.id)]
            s = ""
            for c in hand:
                s += await create_future(bot.data.emojis.emoji_as, c + ".png")
            c = await bot.get_colour(user)
            if user.id == players[0]:
                d = f"Begin the game with ✅ when all players are ready!"
            else:
                d = f"Please wait for {user_mention(players[0])} to begin the game!"
            emb = discord.Embed(
                colour=c,
                title="⚠️ Error: Already playing. ⚠️",
                description=d,
            )
            return await interaction_response(
                bot=bot,
                message=message,
                content=s,
                embed=emb,
            )
        if r == "✅":
            # Start game
            if user.id == players[0] or not perm < 3:
                # Has permission to start game
                try:
                    hand = hands[players.index(user.id)]
                except ValueError:
                    players.append(user.id)
                    hand = shuffle(self.deck)[-7:]
                    self.sort(hand)
                    hands.append(hand)
                last = choice(self.deck)
                turn = xrand(len(players))
                if last[-1] == "D":
                    for card in hands[turn]:
                        if card[-1] == "D" or card == "WY":
                            draw = 2
                    if not draw:
                        hands[turn].extend(self.deck[:2])
                        self.sort(hands[turn])
                        turn = (turn + 1) % len(players)
                elif last[-1] == "R":
                    td = -td
                elif last == "WY":
                    for card in hands[turn]:
                        if card == "WY":
                            draw = 4
                    if not draw:
                        hands[turn].extend(self.deck[:4])
                        self.sort(hands[turn])
                        turn = (turn + 1) % len(players)

                content = f"```callback-fun-uno-{players}_{self.hand_repr(hands)}_[]_{turn}_{last}_{'-01'[td]}_{draw}_-\nUNO game in progress...```"
                embed = message.embeds[0]
                embed.description = "\n".join(("➡️ ", "▪️ ")[bool(i)] + user_mention(u) + f" `{len(hands[(i - turn) % len(players)])}`" for i, u in enumerate(players[turn:] + players[:turn]))
                emoji = await create_future(bot.data.emojis.get, last + ".png")
                embed.set_thumbnail(url=str(emoji.url))
                embed.set_footer(text="Click 🔻 to play if it's your turn, ✖ to leave!")
                s = ""
                for c in hand:
                    s += await create_future(bot.data.emojis.emoji_as, c + ".png")

                create_task(interaction_response(
                    bot=bot,
                    message=message,
                    content=s,
                ))
                sem = getattr(message, "sem", None)
                if not sem:
                    try:
                        sem = EDIT_SEM[message.channel.id]
                    except KeyError:
                        sem = EDIT_SEM[message.channel.id] = Semaphore(5.15, 256, rate_limit=5)
                async with sem:
                    return await Request(
                        f"https://discord.com/api/{api}/channels/{message.channel.id}/messages/{message.id}",
                        data=dict(
                            content=content,
                            embeds=[embed.to_dict()],
                            components=restructure_buttons([[
                                cdict(emoji="🔻", style=1),
                                cdict(emoji="✖", style=4),
                            ]]),
                        ),
                        method="PATCH",
                        authorise=True,
                        aio=True,
                    )
            # Does not have permission to start game
            s = ""
            d = f"Please wait for {user_mention(players[0])} to begin the game!"
            try:
                hand = hands[players.index(user.id)]
            except ValueError:
                s = d
                emb = None
            else:
                for c in hand:
                    s += await create_future(bot.data.emojis.emoji_as, c + ".png")
                c = await bot.get_colour(user)
                emb = discord.Embed(
                    colour=c,
                    title="⚠️ Error: Insufficient privileges. ⚠️",
                    description=d,
                )
            return await interaction_response(
                bot=bot,
                message=message,
                content=s,
                embed=emb,
            )
        if r == "🔻":
            # Begins turn
            if user.id == players[turn]:
                # Current turn matches
                hand = hands[turn]
                s = ""
                if last == "WY":
                    playable = ("WY",)
                elif last == "WX":
                    playable = set(hand)
                    for c in hand:
                        s += await create_future(bot.data.emojis.emoji_as, c + ".png")
                else:
                    playable = set()
                    for card in hand:
                        s += await create_future(bot.data.emojis.emoji_as, card + ".png")
                        if card == "WY":
                            playable.add(card)
                        elif draw:
                            if last[-1] == card[-1] == "D":
                                playable.add(card)
                        elif card == "WX":
                            playable.add(card)
                        elif last[0] == card[0] or last[-1] == card[-1]:
                            playable.add(card)
                playable = list(playable)
                self.sort(playable)
                pickup = max(1, draw)
                buttons = [cdict(emoji=bot.data.emojis.get(c + ".png"), custom_id=f"~{message.id}~{c}", style=3) for c in playable]
                buttons.append(cdict(emoji="📤", name=f"Pickup {pickup}", custom_id=f"~{message.id}~!", style=4))

                return await interaction_response(
                    bot=bot,
                    message=message,
                    content=s,
                    buttons=buttons,
                )
            # Not your turn
            hand = hands[players.index(user.id)]
            s = ""
            for c in hand:
                s += await create_future(bot.data.emojis.emoji_as, c + ".png")
            c = await bot.get_colour(user)
            d = f"Please wait for {user_mention(players[turn])} to complete their turn!"
            emb = discord.Embed(
                colour=c,
                title="⚠️ Error: Please wait your turn. ⚠️",
                description=d,
            )
            return await interaction_response(
                bot=bot,
                message=message,
                content=s,
                embed=emb,
            )
        if r == "~!":
            if user.id != players[turn]:
                raise asyncio.InvalidStateError("Error: Please wait your turn.")
            hand = hands[turn]
            # Draw a certain amount of cards based on played draw cards
            if not draw or last[1] not in "DY":
                draw = 1
            if draw:
                hands[turn].extend(shuffle(self.deck)[:draw])
                self.sort(hands[turn])
                if draw > 1:
                    buttons = ()
                else:
                    s = ""
                    if last == "WY":
                        playable = ("WY",)
                    elif last == "WX":
                        playable = set(hand)
                        for c in hand:
                            s += await create_future(bot.data.emojis.emoji_as, c + ".png")
                    else:
                        playable = set()
                        for card in hand:
                            s += await create_future(bot.data.emojis.emoji_as, card + ".png")
                            if card == "WY":
                                playable.add(card)
                            elif draw:
                                if last[-1] == card[-1] == "D":
                                    playable.add(card)
                            elif card == "WX":
                                playable.add(card)
                            elif last[0] == card[0] or last[-1] == card[-1]:
                                playable.add(card)
                    playable = list(playable)
                    if playable:
                        self.sort(playable)
                        buttons = [cdict(emoji=bot.data.emojis.get(c + ".png"), custom_id=f"~{message.id}~{c}", style=3) for c in playable]
                        buttons.append(cdict(emoji="⏭️", name=f"Pass", custom_id=f"~{message.id}~@", style=4))
                    else:
                        buttons = ()
                draw = 0
                content = f"```callback-fun-uno-{players}_{self.hand_repr(hands)}_{winners}_{turn}_{last}_{'-01'[td]}_{draw}_{self.played_repr(played)}-\nUNO game in progress...```"
                content += user_mention(players[turn])
                embed = message.embeds[0]
                embed.description = "\n".join(("➡️ ", "▪️ ")[bool(i)] + user_mention(u) + f" `{len(hands[(i - turn) % len(players)])}`" for i, u in enumerate(players[turn:] + players[:turn]))
                emoji = await create_future(bot.data.emojis.get, last + ".png")
                embed.set_thumbnail(url=str(emoji.url))
                t = ""
                for card in played:
                    t += await create_future(bot.data.emojis.emoji_as, card + ".png")
                embed.clear_fields()
                embed.add_field(name="Previous turn", value=t or "\xad")

                create_task(message.edit(content=content, embed=embed))
                return await interaction_response(
                    bot=bot,
                    message=message,
                    content=s,
                    buttons=buttons,
                )
        if r in ("~!", "~@"):
            if user.id != players[turn]:
                raise asyncio.InvalidStateError("Error: Please wait your turn.")
            hand = hands[turn]
            s = ""
            for c in hand:
                s += await create_future(bot.data.emojis.emoji_as, c + ".png")
            # Skip turn
            if last[0] == "W":
                # Select a colour if last card played was wild
                playable = [c + last[-1] for c in "RYGB"]
                buttons = []
                for c in playable:
                    emoji = await create_future(bot.data.emojis.get, c + ".png")
                    button = cdict(emoji=emoji, custom_id=f"~{message.id}~{c}", style=3)
                    buttons.append(button)

                content = f"```callback-fun-uno-{players}_{self.hand_repr(hands)}_{winners}_{turn}_{last}_{'-01'[td]}_{draw}_{self.played_repr(played)}-\nUNO game in progress...```"
                content += user_mention(players[turn])
                embed = message.embeds[0]
                embed.description = "\n".join(("➡️ ", "▪️ ")[bool(i)] + user_mention(u) + f" `{len(hands[(i - turn) % len(players)])}`" for i, u in enumerate(players[turn:] + players[:turn]))
                emoji = await create_future(bot.data.emojis.get, last + ".png")
                embed.set_thumbnail(url=str(emoji.url))
                t = ""
                for card in played:
                    t += await create_future(bot.data.emojis.emoji_as, card + ".png")
                embed.clear_fields()
                embed.add_field(name="Previous turn", value=t or "\xad")

                create_task(message.edit(content=content, embed=embed))
                return await interaction_patch(
                    bot=bot,
                    message=message,
                    content=s,
                    buttons=buttons,
                )
            # Process end of turn
            if not hands[turn]:
                winners.append(players.pop(turn))
                hands.pop(turn)
            else:
                turn = (turn + td) % len(players)
            if last[-1] == "D":
                newdraw = 0
                for card in hands[turn]:
                    if card[-1] == "D" or card == "WY":
                        newdraw = draw
                if not newdraw:
                    hands[turn].extend(shuffle(self.deck)[:draw])
                    self.sort(hands[turn])
                    turn = (turn + td) % len(players)
                draw = newdraw
            elif last[-1] == "S":
                turn = (turn + td * draw) % len(players)
                draw = 0
            content = f"```callback-fun-uno-{players}_{self.hand_repr(hands)}_{winners}_{turn}_{last}_{'-01'[td]}_{draw}_-\nUNO game in progress...```"
            embed = message.embeds[0]
            embed.description = "\n".join(("➡️ ", "▪️ ")[bool(i)] + user_mention(u) + f" `{len(hands[(i - turn) % len(players)])}`" for i, u in enumerate(players[turn:] + players[:turn]))
            emoji = await create_future(bot.data.emojis.get, last + ".png")
            embed.set_thumbnail(url=str(emoji.url))
            t = ""
            for card in played:
                t += await create_future(bot.data.emojis.emoji_as, card + ".png")
            embed.clear_fields()
            embed.add_field(name="Previous turn", value=t or "\xad")
            create_task(message.edit(content=content, embed=embed))
            return await interaction_patch(
                bot=bot,
                message=message,
                content=s,
                buttons=(),
            )
        if r[0] == "~":
            # Process a card play
            if user.id != players[turn]:
                raise asyncio.InvalidStateError("Error: Please wait your turn.")
            # Current turn matches
            hand = hands[turn]
            card = r[1:]
            s = ""
            for c in hand:
                s += await create_future(bot.data.emojis.emoji_as, c + ".png")
            if last[0] == "W" and card[1] == last[1]:
                if card[0] != "W":
                    # Player chooses a +4 colour
                    last = card
                    if not hand:
                        winners.append(players.pop(turn))
                        hands.pop(turn)
                    else:
                        turn = (turn + td) % len(players)
                    newdraw = 0
                    for card in hands[turn]:
                        if card[-1] == "Y":
                            newdraw = draw
                    if not newdraw:
                        hands[turn].extend(shuffle(self.deck)[:draw])
                        self.sort(hands[turn])
                        turn = (turn + td) % len(players)
                    draw = newdraw
                    content = f"```callback-fun-uno-{players}_{self.hand_repr(hands)}_{winners}_{turn}_{last}_{'-01'[td]}_{draw}_-\nUNO game in progress...```"
                    embed = message.embeds[0]
                    embed.description = "\n".join(("➡️ ", "▪️ ")[bool(i)] + user_mention(u) + f" `{len(hands[(i - turn) % len(players)])}`" for i, u in enumerate(players[turn:] + players[:turn]))
                    emoji = await create_future(bot.data.emojis.get, last + ".png")
                    embed.set_thumbnail(url=str(emoji.url))
                    t = ""
                    for card in played:
                        t += await create_future(bot.data.emojis.emoji_as, card + ".png")
                    embed.clear_fields()
                    embed.add_field(name="Previous turn", value=t or "\xad")
                    create_task(message.edit(content=content, embed=embed))
                    return await interaction_patch(
                        bot=bot,
                        message=message,
                        content=s,
                        buttons=(),
                    )
            # Otherwise make sure card is playable (since interactions can be spoofed)
            if card != "WY" and last[0] != "W":
                if draw and last[1] in "DY":
                    if card[1] not in "DY":
                        raise TypeError(f"illegal play sequence ({last} => {card})")
                elif card != "WX":
                    if card[0] != last[0] and card[1] != last[1]:
                        raise TypeError(f"illegal play sequence ({last} => {card})")
            hand.remove(card)
            last = card
            played.append(card)
            # Modify game state if playing an action card
            if card[-1] == "D":
                draw += 2
            elif card[-1] == "R":
                td = -td
                if len(hands) < 2:
                    draw = 1
            elif card[-1] == "S":
                if len(hands) < 2:
                    draw = 1
                else:
                    draw += 1
            elif card[1] == "Y":
                draw += 4
            s = ""
            for c in hand:
                s += await create_future(bot.data.emojis.emoji_as, c + ".png")
            if last[0] != "W":
                playable = [c for c in set(hand) if c[1] == last[1]]
                if playable:
                    self.sort(playable)
                    buttons = [cdict(emoji=bot.data.emojis.get(c + ".png"), custom_id=f"~{message.id}~{c}", style=3) for c in playable]
                    buttons.append(cdict(emoji="⏭️", name=f"Pass", custom_id=f"~{message.id}~@", style=4))

                    content = f"```callback-fun-uno-{players}_{self.hand_repr(hands)}_{winners}_{turn}_{last}_{'-01'[td]}_{draw}_{self.played_repr(played)}-\nUNO game in progress...```"
                    embed = message.embeds[0]
                    embed.description = "\n".join(("➡️ ", "▪️ ")[bool(i)] + user_mention(u) + f" `{len(hands[(i - turn) % len(players)])}`" for i, u in enumerate(players[turn:] + players[:turn]))
                    emoji = await create_future(bot.data.emojis.get, last + ".png")
                    embed.set_thumbnail(url=str(emoji.url))
                    t = ""
                    for card in played:
                        t += await create_future(bot.data.emojis.emoji_as, card + ".png")
                    embed.clear_fields()
                    embed.add_field(name="Previous turn", value=t or "\xad")

                    create_task(message.edit(content=content, embed=embed))
                    return await interaction_patch(
                        bot=bot,
                        message=message,
                        content=s,
                        buttons=buttons,
                    )
                if not hand:
                    winners.append(players.pop(turn))
                    hands.pop(turn)
                else:
                    turn = (turn + td) % len(players)
                if last[-1] == "D":
                    newdraw = 0
                    for card in hands[turn]:
                        if card[-1] in "DY":
                            newdraw = draw
                    if not newdraw:
                        hands[turn].extend(shuffle(self.deck)[:draw])
                        self.sort(hands[turn])
                        turn = (turn + td) % len(players)
                    draw = newdraw
                elif last[-1] in "RS":
                    turn = (turn + td * draw) % len(players)
                    draw = 0
                content = f"```callback-fun-uno-{players}_{self.hand_repr(hands)}_{winners}_{turn}_{last}_{'-01'[td]}_{draw}_-\nUNO game in progress...```"
                embed = message.embeds[0]
                embed.description = "\n".join(("➡️ ", "▪️ ")[bool(i)] + user_mention(u) + f" `{len(hands[(i - turn) % len(players)])}`" for i, u in enumerate(players[turn:] + players[:turn]))
                emoji = await create_future(bot.data.emojis.get, last + ".png")
                embed.set_thumbnail(url=str(emoji.url))
                t = ""
                for card in played:
                    t += await create_future(bot.data.emojis.emoji_as, card + ".png")
                embed.clear_fields()
                embed.add_field(name="Previous turn", value=t or "\xad")
                create_task(message.edit(content=content, embed=embed))
                return await interaction_patch(
                    bot=bot,
                    message=message,
                    content=s,
                    buttons=(),
                )
            playable = [c for c in set(hand) if c == last or last[1] == "X" and c[1] == "Y"]
            if playable:
                self.sort(playable)
                buttons = [cdict(emoji=bot.data.emojis.get(c + ".png"), custom_id=f"~{message.id}~{c}", style=3) for c in playable]
                buttons.append(cdict(emoji="⏭️", name=f"Pass", custom_id=f"~{message.id}~@", style=4))

                content = f"```callback-fun-uno-{players}_{self.hand_repr(hands)}_{winners}_{turn}_{last}_{'-01'[td]}_{draw}_{self.played_repr(played)}-\nUNO game in progress...```"
                embed = message.embeds[0]
                embed.description = "\n".join(("➡️ ", "▪️ ")[bool(i)] + user_mention(u) + f" `{len(hands[(i - turn) % len(players)])}`" for i, u in enumerate(players[turn:] + players[:turn]))
                emoji = await create_future(bot.data.emojis.get, last + ".png")
                embed.set_thumbnail(url=str(emoji.url))
                t = ""
                for card in played:
                    t += await create_future(bot.data.emojis.emoji_as, card + ".png")
                embed.clear_fields()
                embed.add_field(name="Previous turn", value=t or "\xad")

                create_task(message.edit(content=content, embed=embed))
                return await interaction_patch(
                    bot=bot,
                    message=message,
                    content=s,
                    buttons=buttons,
                )
            playable = [c + last[-1] for c in "RYGB"]
            buttons = []
            for c in playable:
                emoji = await create_future(bot.data.emojis.get, c + ".png")
                button = cdict(emoji=emoji, custom_id=f"~{message.id}~{c}", style=3)
                buttons.append(button)

            content = f"```callback-fun-uno-{players}_{self.hand_repr(hands)}_{winners}_{turn}_{last}_{'-01'[td]}_{draw}_{self.played_repr(played)}-\nUNO game in progress...```"
            embed = message.embeds[0]
            embed.description = "\n".join(("➡️ ", "▪️ ")[bool(i)] + user_mention(u) + f" `{len(hands[(i - turn) % len(players)])}`" for i, u in enumerate(players[turn:] + players[:turn]))
            emoji = await create_future(bot.data.emojis.get, last + ".png")
            embed.set_thumbnail(url=str(emoji.url))
            t = ""
            for card in played:
                t += await create_future(bot.data.emojis.emoji_as, card + ".png")
            embed.clear_fields()
            embed.add_field(name="Previous turn", value=t or "\xad")

            create_task(message.edit(content=content, embed=embed))
            return await interaction_patch(
                bot=bot,
                message=message,
                content=s,
                buttons=buttons,
            )


class Matchmaking(Command):
    name = ["Ship"] + HEARTS
    description = "Ships two provided objects with a randomised percent."
    usage = "<objects>*"
    slash = ("Ship",)

    async def __call__(self, bot, message, channel, guild, args, **void):
        uids = deque()
        users = deque()
        for u_id in map(verify_id, args):
            try:
                user = await bot.fetch_member_ex(u_id, guild, allow_banned=False, fuzzy=None)
            except:
                users.append(as_str(u_id).capitalize())
            else:
                users.append(user.display_name)
                uids.append(user.id)
        while len(users) < 2:
            users.append(choice(guild.members).display_name)

        x = random.random()
        users = sorted(map(unicode_prune, users))
        seed = nhash("\x7f".join(users))
        seed, percentage = divmod(seed, 100)
        random.seed(seed)
        shiptargets = uni_str(" ♡ ".join(map(sqr_md, users)), 1)
        users = shuffle(users)
        shipname = users[0][:len(users[0]) + 1 >> 1]
        shipname += "".join(a[len(a) >> 2:len(a) - len(a) >> 2] for a in users[1:-1])
        shipname += users[-1][len(users[-1]) >> 1:]
        shipname = shipname.strip().capitalize()

        random.seed(utc() * x)
        heart = choice(HEARTS)
        bar = await bot.create_progress_bar(21, percentage / 100)

        markdown = choice(ini_md, lambda s: css_md(s, force=True))
        suspicious_function = lambda x: x / ((x ** 2 * 6254793562032913) // (7632048114126314 * 10 ** 24) - (x * 5638138161912547) // 2939758 + 1000000155240420236976462021787648)
        suspicious_function_2 = lambda x: int.from_bytes(bytes.fromhex(x.encode("utf-8").hex()), "little")
        s = "".join(a.capitalize() for a in sorted(users))
        if round(suspicious_function(suspicious_function_2(s))) in (13264547, 47787122) or fold(int.__and__, uids) == 38283079340654592:
            inwards_heart = [
                "00111011100",
                "01122122110",
                "01223232210",
                "01234543210",
                "00123432100",
                "00012321000",
                "00001210000",
                "00000100000"
            ]
            emoji = {
                "0": "▪",
                "1": "<a:_" + ":797359273914138625>",
                "2": "<a:_" + ":797359354314620939>",
                "3": "<a:_" + ":797359351509549056>",
                "4": "<a:_" + ":797359341157482496>",
                "5": "<:_" + ":722354192995450912>",
            }
            e_calc = lambda x: (x * 15062629995394936) // 7155909327645687 - (x ** 2 * 3014475045596449) // (2062550437214859 * 10 ** 18) + 123795804094758818
            e2 = bot.get_emoji(e_calc(guild.id))
            if e2:
                emoji["5"] = f"<:_:{e2.id}>"

            trans = "".maketrans(emoji)
            rainbow_heart = "\n".join(inwards_heart).translate(trans)
            description = markdown(f"{shiptargets}❔ They score an [{uni_str('infinite%', 1)}]❕ 💜") + rainbow_heart
        else:
            if all(a == users[0] for a in users[1:]):
                description = markdown(f"{shiptargets}❔ They [{percentage}%] love themselves❕ " + get_random_emoji()) + bar
            else:
                description = markdown(f"{shiptargets} ({uni_str(shipname, 1)})❔ They score a [{percentage}%]❕ " + get_random_emoji()) + bar
        author = get_author(message.author)
        author.name = heart + uni_str(" MATCHMAKING ", 12) + heart
        colour = await bot.get_colour(message.author)
        colour = discord.Colour(colour)

        bot.send_as_embeds(channel, description, colour=colour, author=author, reference=message)


class Pay(Command):
    name = ["GiveCoins", "GiveGold"]
    description = "Pays a specified amount of coins to the target user."
    usage = "<0:user> <1:amount(1)>?"
    rate_limit = 0.5

    async def __call__(self, bot, user, args, guild, **void):
        if not args:
            raise ArgumentError("Please input target user.")
        target = await bot.fetch_user_member(args.pop(0), guild)
        if target.id == bot.id:
            return "\u200bI appreciate the generosity, but I have enough already :3"
        if args:
            amount = await bot.eval_math(" ".join(args))
        else:
            amount = 1
        if amount <= 0:
            raise ValueError("Please input a valid amount of coins.")
        if not amount <= bot.data.users.get(user.id, {}).get("gold", 0):
            raise OverflowError("Payment cannot be greater than your balance.")
        bot.data.users.add_gold(user, -amount)
        bot.data.users.add_gold(target, amount)
        if user.id != target.id:
            bot.data.dailies.progress_quests(user, "pay", amount)
        return css_md(f"{sqr_md(user)} has paid {sqr_md(amount)} coins to {sqr_md(target)}.")


class React(Command):
    server_only = True
    name = ["AutoReact"]
    min_level = 2
    description = "Causes ⟨MIZA⟩ to automatically assign a reaction to messages containing the substring."
    usage = "<0:react_to>? <1:react_data>? <disable{?d}>?"
    flags = "aedzf"
    no_parse = True
    directions = [b'\xe2\x8f\xab', b'\xf0\x9f\x94\xbc', b'\xf0\x9f\x94\xbd', b'\xe2\x8f\xac', b'\xf0\x9f\x94\x84']
    dirnames = ["First", "Prev", "Next", "Last", "Refresh"]
    rate_limit = (1, 2)
    slash = True

    async def __call__(self, bot, flags, guild, message, user, argv, args, **void):
        update = self.data.reacts.update
        following = bot.data.reacts
        curr = set_dict(following, guild.id, mdict())
        if type(curr) is not mdict:
            following[guild.id] = curr = mdict(curr)
        if not argv:
            if "d" in flags:
                # This deletes all auto reacts for the current guild
                if "f" not in flags and len(curr) > 1:
                    return css_md(sqr_md(f"WARNING: {len(curr)} ITEMS TARGETED. REPEAT COMMAND WITH ?F FLAG TO CONFIRM."), force=True)
                if guild.id in following:
                    following.pop(guild.id)
                return italics(css_md(f"Successfully removed all {sqr_md(len(curr))} auto reacts for {sqr_md(guild)}."))
            # Set callback message for scrollable list
            buttons = [cdict(emoji=dirn, name=name, custom_id=dirn) for dirn, name in zip(map(as_str, self.directions), self.dirnames)]
            await send_with_reply(
                None,
                message,
                "*```" + "\n" * ("z" in flags) + "callback-fun-react-"
                + str(user.id) + "_0"
                + "-\nLoading React database...```*",
                buttons=buttons,
            )
            return
        if "d" in flags:
            a = full_prune(args[0])
            if a in curr:
                curr.pop(a)
                update(guild.id)
                return italics(css_md(f"Removed {sqr_md(a)} from the auto react list for {sqr_md(guild)}."))
            else:
                raise LookupError(f"{a} is not in the auto react list.")
        lim = 64 << bot.is_trusted(guild.id) * 2 + 1
        if curr.count() >= lim:
            raise OverflowError(f"React list for {guild} has reached the maximum of {lim} items. Please remove an item to add another.")
        # Limit substring length to 64
        a = unicode_prune(" ".join(args[:-1])).casefold()[:64]
        e_id = await bot.id_from_message(args[-1])
        if isinstance(e_id, int):
            emoji = await bot.fetch_emoji(e_id)
        else:
            emoji = e_id
        emoji = str(emoji)
        # This reaction indicates that the emoji was valid
        await message.add_reaction(emoji)
        curr.append(a, emoji)
        following[guild.id] = mdict({i: curr[i] for i in sorted(curr)})
        return css_md(f"Added {sqr_md(a)} ➡️ {sqr_md(emoji)} to the auto react list for {sqr_md(guild)}.")

    async def _callback_(self, bot, message, reaction, user, perm, vals, **void):
        u_id, pos = list(map(int, vals.split("_", 1)))
        if reaction not in (None, self.directions[-1]) and u_id != user.id and perm < 3:
            return
        if reaction not in self.directions and reaction is not None:
            return
        guild = message.guild
        user = await bot.fetch_user(u_id)
        following = bot.data.reacts
        curr = following.get(guild.id, mdict())
        page = 16
        last = max(0, len(curr) - page)
        if reaction is not None:
            i = self.directions.index(reaction)
            if i == 0:
                new = 0
            elif i == 1:
                new = max(0, pos - page)
            elif i == 2:
                new = min(last, pos + page)
            elif i == 3:
                new = last
            else:
                new = pos
            pos = new
        content = message.content
        if not content:
            content = message.embeds[0].description
        i = content.index("callback")
        content = "*```" + "\n" * ("\n" in content[:i]) + (
            "callback-fun-react-"
            + str(u_id) + "_" + str(pos)
            + "-\n"
        )
        if not curr:
            content += f"No currently assigned auto reactions for {str(guild).replace('`', '')}.```*"
            msg = ""
        else:
            content += f"{len(curr)} auto reactions currently assigned for {str(guild).replace('`', '')}:```*"
            key = lambda x: "\n" + ", ".join(x)
            msg = ini_md(iter2str({k: curr[k] for k in tuple(curr)[pos:pos + page]}, key=key))
        colour = await self.bot.data.colours.get(worst_url(guild))
        emb = discord.Embed(
            description=content + msg,
            colour=colour,
        )
        emb.set_author(**get_author(user))
        more = len(curr) - pos - page
        if more > 0:
            emb.set_footer(text=f"{uni_str('And', 1)} {more} {uni_str('more...', 1)}")
        create_task(message.edit(content=None, embed=emb, allowed_mentions=discord.AllowedMentions.none()))
        if hasattr(message, "int_token"):
            await bot.ignore_interaction(message)


class UpdateReacts(Database):
    name = "reacts"

    async def _nocommand_(self, text, text2, edit, orig, message, **void):
        if message.guild is None or not orig:
            return
        g_id = message.guild.id
        data = self.data
        if g_id not in data:
            return
        with tracebacksuppressor(ZeroDivisionError):
            following = self.data[g_id]
            if type(following) != mdict:
                following = self.data[g_id] = mdict(following)
            reacting = {}
            words = clean_words = None
            full = clean_full = None
            for k in following:
                if is_alphanumeric(k) and " " not in k:
                    if words is None:
                        words = text.split()
                    x = words
                    if clean_words is None:
                        clean_words = text2.split()
                    y = clean_words
                else:
                    if full is None:
                        full = full_prune(message.content)
                    x = full
                    if clean_full is None:
                        clean_full = full_prune(message.clean_content)
                    y = clean_full
                # Store position for each keyword found
                if k in x:
                    emojis = following[k]
                    reacting[x.index(k) / len(x)] = emojis
                elif k in y:
                    emojis = following[k]
                    reacting[y.index(k) / len(y)] = emojis
            # Reactions sorted by their order of appearance in the message
            for r in sorted(reacting):
                for react in reacting[r]:
                    try:
                        await message.add_reaction(react)
                    except discord.HTTPException as ex:
                        if "10014" in repr(ex):
                            emojis.remove(react)
                            self.update(g_id)


class Dogpile(Command):
    server_only = True
    min_level = 2
    description = "Causes ⟨MIZA⟩ to automatically imitate users when 3+ of the same messages are posted in a row. Grants XP and gold when triggered."
    usage = "(enable|disable)?"
    flags = "aed"
    rate_limit = 0.5

    async def __call__(self, flags, guild, name, **void):
        update = self.data.dogpiles.update
        bot = self.bot
        following = bot.data.dogpiles
        curr = following.get(guild.id, False)
        if "d" in flags:
            if guild.id in following:
                following.pop(guild.id)
            return css_md(f"Disabled dogpile imitating for {sqr_md(guild)}.")
        if "e" in flags or "a" in flags:
            following[guild.id] = True
            return css_md(f"Enabled dogpile imitating for {sqr_md(guild)}.")
        if curr:
            return ini_md(f"Dogpile imitating is currently enabled in {sqr_md(guild)}.")
        return ini_md(f'Dogpile imitating is currently disabled in {sqr_md(guild)}. Use "{bot.get_prefix(guild)}{name} enable" to enable.')


class UpdateDogpiles(Database):
    name = "dogpiles"

    async def _nocommand_(self, edit, message, **void):
        if edit or message.guild is None or not message.content:
            return
        g_id = message.guild.id
        following = self.data
        dogpile = following.get(g_id)
        if not dogpile:
            return
        u_id = message.author.id
        c_id = message.channel.id
        content = zwremove(message.content)
        if not content:
            return
        try:
            number = round_min(content)
        except ValueError:
            if len(content) == 1:
                last_number = number = content
                add = None
            else:
                number = None
        else:
            numbers = deque((number,))
        curr = content
        fix = None
        mcount = 0
        count = 0
        last_author_id = u_id
        stopped = False
        async for m in self.bot.history(message.channel, limit=100):
            if m.id == message.id:
                continue
            c = zwremove(m.content)
            if not c:
                break
            if number is not None:
                if type(number) is str:
                    if len(c) != 1:
                        break
                    n = ord(c)
                    if add is None:
                        add = n - ord(number)
                    elif n - add != ord(number):
                        break
                    number = c
                else:
                    try:
                        n = round_min(c)
                    except:
                        break
                    numbers.appendleft(n)
            elif c not in curr:
                break
            else:
                spl = curr.split(c)
                if not fix:
                    fix = spl
                elif fix != spl:
                    break
                curr = c
            if m.author.id == last_author_id:
                break
            if m.author.id == self.bot.id:
                stopped = True
            elif not stopped:
                count += 1
            mcount += 1
            if mcount >= 11:
                break
            last_author_id = m.author.id
        # print(content, count)
        if count < 2:
            return
        n = None
        if number and type(number) is not str:
            n = await create_future(predict_next, numbers)
            if type(n) is int:
                s = str(n)
                for i in range(3, len(s) + 1):
                    x = predict_next(list(map(int, s)), limit=i)
                    if x is not None:
                        count = (not x) + count << 1
        if random.random() >= 3 / (count + 0.5):
            if not xrand(4096):
                content = "https://cdn.discordapp.com/attachments/321524006316539904/843707932989587476/secretsmall.gif"
                create_task(message.add_reaction("💎"))
                self.bot.data.users.add_diamonds(message.author, 1000)
            elif number is not None:
                if type(number) is str:
                    content = chr(ord(last_number) - add)
                else:
                    if n is None:
                        n = await create_future(predict_next, numbers)
                    if not n:
                        return
                    content = str(n)
                content = content.strip()
                if not content:
                    return
            elif fix:
                content = content.join(fix)
            print(message.channel, content, mcount)
            if content[0].isascii() and content[:2] != "<:" and not is_url(content):
                content = lim_str("\u200b" + content, 2000)
            create_task(message.channel.send(content, tts=message.tts))
            self.bot.data.users.add_xp(message.author, len(content) / 2 + 16)
            self.bot.data.users.add_gold(message.author, len(content) / 4 + 32)


class Daily(Command):
    name = ["Quests", "Quest", "Tasks", "Challenges", "Dailies"]
    description = "Shows your list of daily quests."
    rate_limit = 1

    async def __call__(self, bot, user, channel, **void):
        data = bot.data.dailies.get(user)
        colour = await bot.get_colour(user)
        emb = discord.Embed(title="Daily Quests", colour=colour).set_author(**get_author(user))
        bal = await bot.data.users.get_balance(user)
        c = len(data['quests'])
        emb.description = f"```callback-fun-daily-{user.id}-\n{c} task{'' if c == 1 else 's'} available\n{sec2time(86400 - utc() + data['time'])} remaining```Balance: {bal}"
        for field in data["quests"][:5]:
            bar = await bot.create_progress_bar(10, field.progress / field.required)
            rewards = await bot.as_rewards(field.get("diamonds", None), field.get("gold", None))
            emb.add_field(name=field.name, value=f"{bar} `{int(field.progress)}/{field.required}`\nRewards: {rewards}", inline=False)
        message = await channel.send(embed=emb)
        create_task(message.add_reaction("✅"))

    async def _callback_(self, bot, user, reaction, message, perm, vals, **void):
        if reaction is None:
            return
        if as_str(reaction) != "✅":
            return
        u_id = vals
        if str(user.id) != u_id:
            return
        data = bot.data.dailies.collect(user)
        colour = await bot.get_colour(user)
        emb = discord.Embed(title="Daily Quests", colour=colour).set_author(**get_author(user))
        bal = await bot.data.users.get_balance(user)
        c = len(data['quests'])
        emb.description = f"```callback-fun-daily-{user.id}-\n{c} task{'' if c == 1 else 's'} available\n{sec2time(86400 - utc() + data['time'])} remaining```Balance: {bal}"
        for field in data["quests"][:5]:
            bar = await bot.create_progress_bar(10, field.progress / field.required)
            rewards = await bot.as_rewards(field.get("diamonds", None), field.get("gold", None))
            emb.add_field(name=field.name, value=f"{bar} `{floor(field.progress)}/{field.required}`\nRewards: {rewards}", inline=False)
        return await message.edit(embed=emb)


class UpdateDailies(Database):
    name = "dailies"

    def __load__(self, **void):
        self.typing = {}
        self.generator = alist()
        self.initialize()

    def get(self, user):
        data = self.data.get(user.id)
        if not data or utc() - data.get("time", 0) >= 86400:
            data = self.data[user.id] = dict(quests=self.generate(user), time=zerot())
        return data

    def collect(self, user):
        data = self.get(user)
        quests = data["quests"]
        pops = set()
        for i, quest in enumerate(quests):
            if quest.progress >= quest.required:
                self.bot.data.users.add_diamonds(user, quest.get("diamonds"))
                self.bot.data.users.add_gold(user, quest.get("gold"))
                pops.add(i)
        if pops:
            quests.pops(pops)
            self.update(user.id)
        return data
    
    def add_quest(self, weight, action, name, x=1, gold=0, diamonds=0, **kwargs):
        if weight > 0:

            def func(action, name, level, x, gold, diamonds, **kwargs):
                if callable(x):
                    x = x(level)
                x = round_random(x)
                if callable(gold):
                    gold = gold(x)
                if callable(diamonds):
                    diamonds = diamonds(x)
                if callable(name):
                    name = name(x)
                elif "{x}" in name:
                    name = name.format(x=x)
                quest = cdict(
                    action=action,
                    name=name,
                    progress=0,
                    required=x,
                    gold=round_random(gold),
                    diamonds=round_random(diamonds),
                )
                quest.update(kwargs)
                return quest

            self.generator.extend(repeat(lambda level: func(action, name, level, x, gold, diamonds, **kwargs), weight))

    def initialize(self):
        add_quest = self.add_quest
        scale = lambda low, high, level_bonus=0, multiple=0: lambda level: round_random_multiple(random.randint(low, high) + level * level_bonus * random.random(), multiple)
        add_quest(100, "send", "Post {x} messages", gold=lambda x: x << 1,
            x=scale(70, 180, 3, 3))
        add_quest(70, "music", lambda x: f"Listen to {sec2time(x)} of my music", gold=nofunc, diamonds=lambda x: xrand(1, x) / 60,
            x=scale(180, 480, 13, 60))
        for catg in "main string voice image fun".split():
            add_quest(13, "category", "Use {x} " + catg + " commands", catg=catg, gold=lambda x: x * 9,
                x=scale(9, 17, 0.3))
        add_quest(60, "typing", lambda x: f"Type for {sec2time(x)}", gold=lambda x: x * 2.5,
            x=scale(150, 400, 11, 30))
        add_quest(52, "first", lambda x: f"Be the first to post in a channel since {sec2time(x)} ago", gold=lambda x: x >> 3, diamonds=1,
            x=scale(1800, 3600, 240, 300))
        add_quest(50, "reply", "Reply to {x} messages", gold=lambda x: x * 12,
            x=scale(23, 40, 1.1))
        add_quest(50, "channel", "Send messages in {x} different channels", gold=lambda x: x * 24,
            x=scale(5, 8, 0.06))
        add_quest(45, "react", "Add {x} reactions", gold=lambda x: x * 5,
            x=scale(20, 39, 1, 2))
        add_quest(45, "reacted", "Have {x} reactions added to your messages by other users", gold=lambda x: x * 15, diamonds=lambda x: xrand(1, x) / 8,
            x=scale(15, 31, 0.75, 2))
        add_quest(42, "xp", "Earn {x} experience", gold=lambda x: x >> 2, diamonds=1,
            x=scale(1000, 2000, 80, 50))
        add_quest(40, "word", "Send {x} total words of text", gold=lambda x: x / sqrt(5),
            x=scale(400, 600, 15, 5))
        add_quest(40, "text", "Send {x} total characters of text", gold=lambda x: x >> 3,
            x=scale(1600, 2400, 60, 10))
        add_quest(37, "url", "Send {x} attachments or links", gold=lambda x: x * 16,
            x=scale(12, 25, 0.15))
        add_quest(35, "command", "Use {x} commands", gold=lambda x: x * 9,
            x=scale(24, 40, 0.4))
        add_quest(30, "talk", "Talk to me {x} times", gold=lambda x: x * 7, diamonds=xrand(2, 4),
            x=lambda level: xrand(10, 21))
        add_quest(20, "pay", "Pay {x} to other users", gold=lambda x: x >> 1, diamonds=lambda x: xrand(0, 2),
            x=scale(400, 900, 70, 100))
        add_quest(18, "diamond", "Earn 1 diamond", required=1, gold=lambda x: x * 50, diamonds=1,
            x=nofunc)
        add_quest(15, "invite", "Invite me to a server and/or react to the join message", required=1, diamonds=lambda x: 50 + x * 2 / 3,
            x=nofunc)

    def generate(self, user):
        if user.id == self.bot.id or self.bot.is_blacklisted(user.id):
            return ()
        xp = self.bot.data.users.get_xp(user)
        if not is_finite(xp):
            return ()
        level = self.bot.data.users.xp_to_level(xp)
        quests = alist()
        req = min(20, level + 5 >> 1)
        att = 0
        while len(quests) < req and att < req << 1:
            q = choice(self.generator)(level)
            if not quests or q.action not in (e.action for e in quests[-5:]):
                q.progress = 0
                quests.append(q)
            att += 1
        return quests.appendleft(cdict(action=None, name="Daily rewards", progress=1, required=1, gold=level * 30 + 400))

    def progress_quests(self, user, action, value=1):
        if user.id == self.bot.id or self.bot.is_blacklisted(user.id):
            return
        data = self.get(user)
        quests = data["quests"]
        for i in range(min(5, len(quests))):
            quest = quests[i]
            if quest.action == action:
                if callable(value):
                    value(quest)
                else:
                    quest.progress += value
                self.update(user.id)

    async def valid_message(self, message):
        user = message.author
        self.progress_quests(user, "send")
        self.progress_quests(user, "text", get_message_length(message))
        self.progress_quests(user, "word", get_message_words(message))
        self.progress_quests(user, "url", len(message.attachments) + len(message.embeds) + len(find_urls(message.content)))
        if getattr(message, "reference", None):
            self.progress_quests(user, "reply")
        
        def progress_channel(quest):
            channels = quest.setdefault("channels", set())
            channels.add(message.channel.id)
            quest.progress = len(channels)

        self.progress_quests(user, "channel", progress_channel)
        if user.id in self.typing:
            t = utc()
            self.progress_quests(user, "typing", t - self.typing.pop(user.id, t))
        last = await self.bot.get_last_message(message.channel, key=lambda m: m.id < message.id)
        since = id2td(message.id - last.id)
        self.progress_quests(user, "first", lambda quest: quest.__setitem__("progress", max(quest.progress, since)))

    def _command_(self, user, command, loop=False, **void):
        if not loop:
            self.progress_quests(user, "command")

            def progress_category(quest):
                if quest.catg == command.catg.casefold():
                    quest.progress += 1

            self.progress_quests(user, "category", progress_category)

    def _typing_(self, user, **void):
        if user.id not in self.data:
            self.typing.pop(user.id, None)
            return
        if user.id in self.typing:
            if utc() - self.typing[user.id] > 10:
                self.progress_quests(user, "typing", 10)
                self.typing[user.id] = utc()
        else:
            self.typing[user.id] = utc()

    def _reaction_add_(self, message, user, **void):
        self.progress_quests(user, "react")
        if message.author.id != user.id and user.id != self.bot.id:
            self.progress_quests(message.author, "reacted")


class Wallet(Command):
    name = ["Level", "Bal", "Balance"]
    description = "Shows the target users' wallet."
    usage = "<users>*"
    rate_limit = 1
    multi = True
    slash = ("Wallet", "Bal")

    async def __call__(self, bot, args, argv, argl, user, guild, channel, **void):
        users = await bot.find_users(argl, args, user, guild)
        if not users:
            raise LookupError("No results found.")
        for user in users:
            data = bot.data.users.get(user.id, {})
            xp = bot.data.users.get_xp(user)
            level = bot.data.users.xp_to_level(xp)
            xp_curr = bot.data.users.xp_required(level)
            xp_next = bot.data.users.xp_required(level + 1)
            ratio = (xp - xp_curr) / (xp_next - xp_curr)
            gold = data.get("gold", 0)
            diamonds = data.get("diamonds", 0)
            bar = await bot.create_progress_bar(18, ratio)
            xp = floor(xp)
            bal = await bot.as_rewards(diamonds, gold)
            description = f"{bar}\n`Lv {level}`\n`XP {xp}/{xp_next}`\n{bal}"
            ingots = data.get("ingots", 0)
            if ingots:
                ingot = await create_future(bot.data.emojis.emoji_as, "gold_ingot.gif")
                description += f" {ingot} {ingots}"
            minecraft = data.get("minecraft", 0)
            if minecraft:
                items = deque()
                for i, c in sorted(minecraft.items()):
                    s = await create_future(bot.data.emojis.emoji_as, barter_values[i] + ".gif")
                    s += f" {c}"
                    items.append(s)
                description += "\n" + " ".join(items)
            url = await self.bot.get_proxy_url(user)
            bot.send_as_embeds(channel, description, thumbnail=url, author=get_author(user))

    join_cache = {}

    async def _callback_(self, bot, message, reaction, user, vals, **void):
        ts = int(float(vals))
        if utc() - ts > 86400:
            self.join_cache.pop(message.id, None)
            return
        if reaction is None or as_str(reaction) != "✅":
            return
        cache = set_dict(self.join_cache, message.id, set())
        if len(cache) > 256:
            cache.pop()
        if user.id in cache:
            return
        cache.add(user.id)
        bot.data.dailies.progress_quests(user, "invite")


class Shop(Command):
    description = "Displays the shop system, or purchases an item."
    usage = "<item[]>"
    rate_limit = 1

    products = cdict(
        upgradeserver=cdict(
            name="Upgrade Server",
            cost=[240, 30720],
            description="Upgrades the server's privilege level, granting access to all command categories and reducing command cooldown.",
        ),
        goldingots=cdict(
            name="Gold Ingots",
            cost=[0, 100],
            description="Gold ingots for the ~barter command.",
        ),
    )

    async def __call__(self, bot, guild, channel, user, message, argv, **void):
        if not argv:
            desc = deque()
            for product in self.products.values():
                cost = await bot.as_rewards(*product.cost)
                desc.append(f"**{product.name}** {cost}\n{product.description}")
            bot.send_as_embeds(channel, "\n\n".join(desc), title="Shop", author=get_author(user), reference=message)
            return
        item = argv.replace("-", "").replace("_", "").replace(" ", "").casefold()
        try:
            product = self.products[item]
        except KeyError:
            raise LookupError(f"Sorry, we don't sell {argv} here...")
        data = bot.data.users.get(user.id, {})
        gold = data.get("gold", 0)
        diamonds = data.get("diamonds", 0)
        if len(product.cost) < 2 or diamonds >= product.cost[0]:
            if gold >= product.cost[-1]:
                if product.name == "Upgrade Server":
                    if hasattr(guild, "ghost"):
                        return "```\nThis item can only be purchased in a server.```"
                    if bot.is_trusted(guild):
                        return "```\nThe current server's privilege level is already at the highest available level. However, you may still purchase this item for other servers.```"
                    await send_with_react(channel, f"```callback-fun-shop-{user.id}_{item}-\nYou are about to upgrade the server's privilege level from 0 to 1.\nThis is irreversible. Please choose wisely.```", reacts="✅", reference=message)
                    return
                if product.name == "Gold Ingots":
                    reacts = deque()
                    for i in range(5):
                        reacts.append(str(i) + as_str(b"\xef\xb8\x8f\xe2\x83\xa3"))
                    await send_with_react(channel, f"```callback-fun-shop-{user.id}_{item}-\nPlease choose how many ingots are desired;\n0: 100\n1: 1,000\n2: 10,000\n3: 100,000\n4: 1,000,000```", reacts=reacts, reference=message)
                    return
                raise NotImplementedError(f"Target item {product.name} has not yet been implemented.")
        raise ValueError(f"Insufficient funds. Use {bot.get_prefix(guild)}shop for product list and cost.")

    async def _callback_(self, bot, message, reaction, user, vals, **void):
        if reaction is None or as_str(reaction) != "✅" and b"\xef\xb8\x8f\xe2\x83\xa3" not in reaction:
            return
        u_id, item = vals.split("_", 1)
        u_id = int(u_id)
        if u_id != user.id:
            return
        guild = message.guild
        try:
            product = self.products[item]
        except KeyError:
            raise LookupError(f"Sorry, we don't sell {argv} here...")
        data = bot.data.users.get(user.id, {})
        gold = data.get("gold", 0)
        diamonds = data.get("diamonds", 0)
        if len(product.cost) < 2 or diamonds >= product.cost[0]:
            if gold >= product.cost[-1]:
                if product.name == "Upgrade Server":
                    if bot.is_trusted(guild):
                        await message.channel.send("```\nThe current server's privilege level is already at the highest available level. However, you may still purchase this item for other servers.", reference=message)
                        return
                    bot.data.users.add_diamonds(user, -product.cost[0])
                    bot.data.users.add_gold(user, -product.cost[-1])
                    bot.data.trusted[guild.id] = True
                    await message.channel.send(f"```{sqr_md(guild)} has been successfully elevated from 0 to 1 privilege level.```", reference=message)
                    return
                if product.name == "Gold Ingots":
                    magnitude = int(as_str(reaction)[0])
                    ingots = 10 ** (magnitude + 2)
                    if gold < ingots:
                        raise ValueError(f"Insufficient funds. Use {bot.get_prefix(guild)}shop for product list and cost.")
                    else:
                        bot.data.users.add_gold(user, -ingots)
                        bot.data.users[user.id].setdefault("ingots", 0)
                        bot.data.users[user.id]["ingots"] += ingots
                    return
                raise NotImplementedError(f"Target item {product.name} has not yet been implemented.")
        raise ValueError(f"Insufficient funds. Use {bot.get_prefix(guild)}shop for product list and cost.")


class Cat(ImagePool, Command):
    description = "Pulls a random image from thecatapi.com, api.alexflipnote.dev/cats, or cdn.nekos.life/meow, and embeds it. Be sure to check out ⟨WEBSERVER⟩/cats!"
    database = "cats"
    name = ["🐱", "Gato", "Meow", "Kitty", "Kitten"]
    slash = True
    http_nums = {
        100, 101, 102,
        200, 201, 202, 203, 204, 206, 207,
        300, 301, 302, 303, 304, 305, 307, 308,
        400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 420, 421, 422, 423, 424, 425, 426, 429, 431, 444,
        450, 451, 497, 498, 499,
        500, 501, 502, 503, 504, 506, 507, 508, 509, 510, 511, 521, 523, 525,
        599,
    }

    async def fetch_one(self):
        if random.random() > 2 / 3:
            if random.random() > 2 / 3:
                x = 0
                url = await create_future(nekos.cat, timeout=8)
            else:
                x = 1
        else:
            x = 2
        if x:
            if x == 1 and alexflipnote_key:
                d = await Request("https://api.alexflipnote.dev/cats", headers={"Authorization": alexflipnote_key}, json=True, aio=True)
            else:
                d = await Request("https://api.thecatapi.com/v1/images/search", json=True, aio=True)
            if type(d) is list:
                d = choice(d)
            url = d["file" if x == 1 and alexflipnote_key else "url"]
        return url

    async def __call__(self, bot, channel, flags, argv, **void):
        if argv.isnumeric() and int(argv) in self.http_nums:
            url = f"https://http.cat/{int(argv)}"
            self.bot.send_as_embeds(channel, image=url)
            return
        return await super().__call__(bot, channel, flags)


class Dog(ImagePool, Command):
    description = "Pulls a random image from images.dog.ceo, api.alexflipnote.dev/dogs, or cdn.nekos.life/woof, and embeds it. Be sure to check out ⟨WEBSERVER⟩/dogs!"
    database = "dogs"
    name = ["🐶", "Woof", "Doggy", "Doggo", "Puppy", "Puppo"]
    slash = True

    async def fetch_one(self):
        if random.random() > 2 / 3:
            if random.random() > 2 / 3:
                x = 0
                url = await create_future(nekos.img, "woof", timeout=8)
            else:
                x = 1
        else:
            x = 2
        if x:
            if x == 1 and alexflipnote_key:
                d = await Request("https://api.alexflipnote.dev/dogs", headers={"Authorization": alexflipnote_key}, json=True, aio=True)
            else:
                d = await Request("https://dog.ceo/api/breeds/image/random", json=True, aio=True)
            if type(d) is list:
                d = choice(d)
            url = d["file" if x == 1 and alexflipnote_key else "message"]
            if "\\" in url:
                url = url.replace("\\/", "/").replace("\\", "/")
            while "///" in url:
                url = url.replace("///", "//")
        return url


class _8Ball(ImagePool, Command):
    description = "Pulls a random image from cdn.nekos.life/8ball, and embeds it."
    database = "8ball"
    name = ["🎱"]

    def __call__(self, channel, flags, **void):
        e_id = choice(
            "Absolutely",
            "Ask_Again",
            "Go_For_It",
            "It_is_OK",
            "It_will_pass",
            "Maybe",
            "No",
            "No_doubt",
            "Not_Now",
            "Very_Likely",
            "Wait_For_It",
            "Yes",
            "Youre_hot",
            "cannot_tell_now",
            "count_on_it",
        )
        url = f"https://cdn.nekos.life/8ball/{e_id}.png"
        if "v" in flags:
            return escape_roles(url)
        self.bot.send_as_embeds(channel, image=url)


class XKCD(ImagePool, Command):
    description = "Pulls a random image from xkcd.com and embeds it."
    database = "xkcd"

    async def fetch_one(self):
        s = await create_future(Request, "https://c.xkcd.com/random/comic")
        search = b"Image URL (for hotlinking/embedding): "
        s = s[s.index(search) + len(search):]
        url = s[:s.index(b"<")].strip()
        return as_str(url)


class Turnoff(ImagePool, Command):
    description = "Pulls a random image from turnoff.us and embeds it."
    database = "turnoff"
    threshold = 1

    async def fetch_one(self):
        if self.bot.data.imagepools.data.get(self.database) and xrand(64):
            return choice(self.bot.data.imagepools[self.database])
        s = await Request("https://turnoff.us", aio=True)
        search = b"$(function() {"
        s = s[s.rindex(search) + len(search):]
        search = b"var pages = "
        s = s[s.index(search) + len(search):]
        s = s[:s.index(b'$("#random-link").attr("href", pages[parseInt(Math.random(1)*(pages.length - 1))]);')].rstrip(b" \r\n\t;")
        hrefs = orjson.loads(s)
        urls = alist("https://turnoff.us" + href.rstrip("/") + "/" for href in hrefs if href)
        data = self.bot.data.imagepools.setdefault(self.database, alist())
        for url in urls[:-1]:
            s = await Request(url, aio=True)
            search = b'<meta property="og:image" content="'
            s = s[s.index(search) + len(search):]
            url = as_str(s[:s.index(b'"')])
            data.add(url)
        url = url[-1]
        s = await Request(url, aio=True)
        search = b'<meta property="og:image" content="'
        s = s[s.index(search) + len(search):]
        url = as_str(s[:s.index(b'"')])
        return url


class Inspiro(ImagePool, Command):
    name = ["InspiroBot"]
    description = "Pulls a random image from inspirobot.me and embeds it."
    database = "inspirobot"

    async def fetch_one(self):
        return await Request("https://inspirobot.me/api?generate=true", decode=True, aio=True)

    async def __call__(self, bot, channel, flags, **void):
        url = await bot.data.imagepools.get(self.database, self.fetch_one, self.threshold)
        if "v" in flags:
            return escape_roles(url)
        embed = discord.Embed(colour=await bot.get_colour(url))
        embed.set_image(url=url)
        await send_with_react(channel, embed=embed, reacts="🔳")


class ImageSearch(ImagePool, Command):
    name = ["🖼", "🧁", "ImgSearch", "Muffin", "Muffins"]
    description = "Pulls a random image from a search on gettyimages.co.uk and unsplash.com, using tags."
    threshold = 9
    sem = Semaphore(5, 256, rate_limit=1)

    def img(self, tag=None, search_tag=None):
        file = f"imgsearch~{tag}"

        async def fetch(tag, search_tag):
            if xrand(3):
                s = await Request(f"https://www.gettyimages.co.uk/photos/{tag}?page={random.randint(1, 100)}", decode=True, aio=True)
                url = "https://media.gettyimages.com/photos/"
                spl = s.split(url)[1:]
                imageset = {url + i.split('"', 1)[0].split("?", 1)[0] for i in spl}
            else:
                d = await Request(f"https://unsplash.com/napi/search/photos?query={tag}&per_page=30&page={random.randint(1, 19)}", json=True, aio=True)
                imageset = {result["urls"]["raw"] for result in d["results"]}
            return imageset

        async def fetchall(tag, search_tag):
            await asyncio.sleep(1)
            images = set()
            for i in range(1, 100):
                async with self.sem:
                    if xrand(3):
                        s = await Request(f"https://www.gettyimages.co.uk/photos/{tag}?page={i}", decode=True, aio=True)
                        url = "https://media.gettyimages.com/photos/"
                        spl = s.split(url)[1:]
                        imageset = [url + i.split('"', 1)[0].split("?", 1)[0] for i in spl]
                    else:
                        d = await Request(f"https://unsplash.com/napi/search/photos?query={tag}&per_page=30&page={i}", json=True, aio=True)
                        imageset = [result["urls"]["raw"] for result in d["results"]]
                images.update(imageset)
                if len(imageset) < 25:
                    break
            data = set_dict(self.bot.data.imagepools, file, alist())
            for url in images:
                if url not in data:
                    data.add(url)
                    self.bot.data.imagepools.update(file)
            return images

        if file not in self.bot.data.imagepools.finished:
            create_task(fetchall(tag, search_tag))
        return self.bot.data.imagepools.get(file, fetch, self.threshold, args=(tag, search_tag))
    
    async def __call__(self, bot, channel, flags, args, name, **void):
        if not args:
            if name == "muffin":
                args = ["muffin"]
            else:
                raise ArgumentError("Input string is empty.")
        args2 = ["".join(c for c in full_prune(w) if c.isalnum()) for w in args]
        tag = "%20".join(sorted(args2))
        search_tag = "%20".join(args2)
        url = await self.img(tag, search_tag)
        if "v" in flags:
            return escape_roles(url)
        self.bot.send_as_embeds(channel, image=url)


class Giphy(ImagePool, Command):
    name = ["GIFSearch"]
    description = "Pulls a random image from a search on giphy.com using tags."
    threshold = 4
    sem = Semaphore(5, 256, rate_limit=1)

    def img(self, tag=None, search_tag=None):
        file = f"giphy~{tag}"

        async def fetch(tag, search_tag):
            resp = await Request(f"https://api.giphy.com/v1/gifs/search?offset=0&type=gifs&sort=&explore=true&api_key={giphy_key}&q={search_tag}", aio=True, json=True)
            images = {entry["images"]["source"]["url"].split("?", 1)[0] for entry in resp["data"]}
            return images

        async def fetchall(tag, search_tag):
            await asyncio.sleep(1)
            images = set()
            for i in range(1, 100):
                async with self.sem:
                    resp = await Request(f"https://api.giphy.com/v1/gifs/search?offset={i * 25}&type=gifs&sort=&explore=true&api_key={giphy_key}&q={search_tag}", aio=True, json=True)
                data = resp["data"]
                if not data:
                    break
                for entry in data:
                    url = entry["images"]["source"]["url"].split("?", 1)[0]
                    images.add(url)
                if len(data) < 25:
                    break
            data = set_dict(self.bot.data.imagepools, file, alist())
            for url in images:
                if url not in data:
                    data.add(url)
                    self.bot.data.imagepools.update(file)
            return images

        if file not in self.bot.data.imagepools.finished:
            create_task(fetchall(tag, search_tag))
        return self.bot.data.imagepools.get(file, fetch, self.threshold, args=(tag, search_tag))
    
    async def __call__(self, bot, channel, flags, args, **void):
        if not args:
            raise ArgumentError("Input string is empty.")
        args2 = ["".join(c for c in full_prune(w) if c.isalnum()) for w in args]
        tag = "%20".join(sorted(args2))
        search_tag = "%20".join(args2)
        url = await self.img(tag, search_tag)
        if "v" in flags:
            return escape_roles(url)
        self.bot.send_as_embeds(channel, image=url)


class Rickroll(Command):
    name = ["Thumbnail", "FakeThumbnail", "FakeVideo"]
    description = "Generates a link that embeds a thumbnail, but redirects to a separate YouTube video once played."
    usage = "<thumbnail>? <video>?"
    no_parse = True
    rate_limit = 1

    async def __call__(self, bot, args, message, channel, **void):
        if message.attachments:
            args = [best_url(a) for a in message.attachments] + args
        if not args:
            return "https://mizabot.xyz/view/!247184721262411780"
        if len(args) < 2:
            args.append("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        url, video = args[:2]
        video = video.strip("<>")
        urls = await bot.follow_url(url, best=True, allow=True, limit=1)
        if not urls:
            url = await bot.get_last_image(message.channel)
        else:
            url = urls[0]
        if "exec" in bot.data:
            with discord.context_managers.Typing(channel):
                mime = await create_future(bot.detect_mime, url)
                data = None
                if "image/png" not in mime:
                    if "image/jpg" not in mime:
                        if "image/jpeg" not in mime:
                            resp = await process_image(url, "resize_mult", ["-nogif", 1, 1, "auto"], timeout=60)
                            with open(resp[0], "rb") as f:
                                data = await create_future(f.read)
                            url = await bot.data.exec.uproxy(data)
                            ext = "png"
                        else:
                            ext = "jpeg"
                    else:
                        ext = "jpg"
                else:
                    ext = "png"
        b = await bot.get_request(url)
        from PIL import Image
        with Image.open(io.BytesIO(b)) as im:
            w, h = im.size
        vid = None
        mime = "text/html"
        if video.startswith("https://www.youtube.com/watch?v") and "=" in video:
            vid = video.split("=", 1)[-1].split("&", 1)[0].split("#", 1)[0]
        elif video.startswith("http://youtu.be/"):
            vid = video.split("e/", 1)[-1].split("?", 1)[0]
        elif video.startswith("http://youtube.com/v/"):
            vid = video.split("v/", 1)[-1].split("?", 1)[0]
        else:
            urls = await bot.follow_url(video, best=True, allow=True, limit=1)
            if urls:
                video = urls[0]
            mime = await create_future(bot.detect_mime, video)
            mime = mime[0]
        if vid:
            embed = f"https://www.youtube.com/embed/{vid}"
            video = f"https://www.youtube.com/watch?v={vid}"
        else:
            embed = video
        s = f"""<!DOCTYPE html>
<html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta property="og:type" content="video.other">
<meta property="twitter:player" content="{embed}">
<meta property="og:video:type" content="{mime}">
<meta property="og:video:width" content="{w}">
<meta property="og:video:height" content="{h}">
<meta name="twitter:image" content="{url}">
<meta http-equiv="refresh" content="0;url={video}">
</head><body></body></html>"""
        urls = await create_future(bot._globals["as_file"], s.encode("utf-8"))
        return urls[0].replace("/p/", "/f/", 1)


class RPS(Command):
    name = ["Rockpaperscissors"]
    description = "A randomised game of Rock-Paper-Scissors!"
    usage = "<rock>? <paper>? <scissors>?"
    slash = True
    typing = False
    rate_limit = (0.05, 0.25)

    buttons = [
        cdict(emoji="✊", style=1),
        cdict(emoji="🖐️", style=1),
        cdict(emoji="✌️", style=1),
    ]
    button_equiv = {
        "✊": "rock",
        "🖐️": "paper",
        "✌️": "scissors",
    }

    async def __call__(self, bot, user, message, channel, argv, looped, **void):
        try:
            if not argv:
                colour = await bot.get_colour(user)
                emb = discord.Embed(colour=colour)
                emb.description = (
                    "*```callback-fun-rps-" + str(user.id) + "-\n"
                    + "Let's play Rock-Paper-Scissors! Make your choice!```*"
                )
                emb.set_author(**get_author(user))
                await send_with_react(channel, "", embed=emb, buttons=self.buttons, reference=message)
                return

            argv = full_prune(argv)
            matches = dict(
                r="scissors",
                s="paper",
                p="rock",
                rock="scissors",
                scissors="paper",
                paper="rock",
            )
            if argv not in matches:
                raise KeyError
            decision = choice(self.button_equiv.values())
            response = f"I'll go with {decision}!\n"
            earned = random.randint(16, 48) * 2 ** bot.data.rps.setdefault(user.id, 0)
            if looped:
                earned = ceil(earned / 8)

            if matches[decision][0] == argv[0]:
                bot.data.rps.pop(user.id, 0)
                emoji = choice("😄", "😁", "😀", "😏")
                response += f"**I win**! {emoji}"
            elif matches[argv] == decision:
                bot.data.rps[user.id] += 1
                emoji = choice("😔", "😦", "🥺", "😧")
                if earned < 1024:
                    bot.data.users.add_gold(user, earned)
                    rew = await bot.as_rewards(earned)
                else:
                    earned /= 1024
                    bot.data.users.add_diamonds(user, earned)
                    rew = await bot.as_rewards(earned, 0)
                response += f"**I lost**... {emoji} You won {rew}."
            elif decision[0] == argv[0]:
                emoji = choice("🙃", "😉", "😮", "😳")
                bot.data.users.add_gold(user, earned / 2)
                rew = await bot.as_rewards(earned / 2)
                response += f"Wow, **we tied**! {emoji} You won {rew}."

            if looped:
                await bot.send_as_embeds(channel, response)
            else:
                await channel.send(response, reference=message)
        except KeyError:
            emoji = choice("😛", "😶‍🌫️", "😇", "😶")
            await channel.send(f"\u200b{''.join(y for x in zip(argv[::2].upper(), argv[1::2].lower() + (' ' if len(argv) & 1 else '')) for y in x if y).strip()} doesn't count! {emoji}", reference=message)

    async def _callback_(self, bot, message, reaction, argv, user, perm, vals, **void):
        u_id = int(vals)
        if u_id != user.id and u_id != 0 and perm < 3:
            return
        r = as_str(reaction)
        try:
            argv = self.button_equiv[r]
        except KeyError:
            return
        matches = dict(
            rock="scissors",
            scissors="paper",
            paper="rock",
        )
        response = f"{user.display_name} chooses {argv}!\n"
        decision = choice(self.button_equiv.values())
        response += f"I'll go with {decision}!\n"
        earned = random.randint(16, 48) * 2 ** bot.data.rps.setdefault(user.id, 0)

        if matches[decision][0] == argv[0]:
            bot.data.rps.pop(user.id, 0)
            emoji = choice("😄", "😁", "😀", "😏")
            response += f"**I win**! {emoji}"
        elif matches[argv] == decision:
            bot.data.rps[user.id] += 1
            emoji = choice("😔", "😦", "🥺", "😧")
            if earned < 1024:
                bot.data.users.add_gold(user, earned)
                rew = await bot.as_rewards(earned)
            else:
                earned /= 1024
                bot.data.users.add_diamonds(user, earned)
                rew = await bot.as_rewards(earned, 0)
            response += f"**I lost**... {emoji} You won {rew}."
        elif decision[0] == argv[0]:
            emoji = choice("🙃", "😉", "😮", "😳")
            bot.data.users.add_gold(user, earned / 2)
            rew = await bot.as_rewards(earned / 2)
            response += f"Wow, **we tied**! {emoji} You won {rew}."

        colour = await bot.get_colour(user)
        emb = discord.Embed(colour=colour)
        emb.description = (
            "*```callback-fun-rps-" + str(user.id) + "-\n"
            + "Let's play Rock-Paper-Scissors! Make your choice!```*"
            + response
        )
        emb.set_author(**get_author(user))
        create_task(message.edit(embed=emb))
        await bot.ignore_interaction(message)


class UpdateRPS(Database):
    name = "rps"


EXCLUDE_URL = "{}/exclusion?callback=jQuery331023608747682107778_{}&childMod={}&session={}&signature={}&step={}&frontaddr={}&question_filter={}&forward_answer=1&_={}"
CHOICE_URL = "{}/choice?callback=jQuery331023608747682107778_{}&childMod={}&session={}&signature={}&step={}&frontaddr={}&question_filter={}&element={}&duel_allowed=1&_={}"

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) snap Chromium/81.0.4044.92 Chrome/81.0.4044.92 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}

def _parse_response(response):
    if response == '{["completion" => "KO - UNAUTHORIZED"]}':
        return {"completion": "KO - UNAUTHORIZED"}
    return json.loads(",".join(response.replace("=>", ":").split("(", 1)[-1:])[:-1])
async_akinator.parse_response = lambda self, response: _parse_response(response)
akinator.Akinator.parse_response = lambda self, response: _parse_response(response)

class Akinator(Command):
    name = ["Aki"]
    description = "Think about a real or fictional character. I will try to guess who it is!"
    usage = "<language(en)>? <child_friendly{?c}>"
    flags = "c"
    slash = True
    rate_limit = (1, 3)
    session = None

    async def compatible_akinator(self, language, child_mode=False):
        try:
            aki = async_akinator(language=akinator.Language.from_str(language), child_mode=child_mode)
            await aki.start_game()
        except:
            aki = async_akinator()
            if not self.session:
                self.session = aiohttp.ClientSession()
            try:
                await aki.start_game(language=language, child_mode=child_mode, client_session=self.session)
            except RuntimeError:
                self.session.close()
                self.session = None
                raise
        aki.timestamp = utc()
        return aki

    buttons = [
        cdict(emoji="👍", name="Yes", style=1),
        cdict(emoji="🙂", name="Probably", style=1),
        cdict(emoji="❓", name="Don't know", style=1),
        cdict(emoji="🙁", name="Probably not", style=1),
        cdict(emoji="👎", name="No", style=1),
        cdict(emoji="↩️", name="Undo", style=1),
        cdict(emoji="🤔", name="Guess", style=1),
        cdict(emoji="🔃", name="Restart", style=1),
        cdict(emoji="⏏️", name="End", style=1),
    ]

    images = [
        "https://cdn.discordapp.com/attachments/731709481863479436/1000436949573705758/A0.png",
        "https://cdn.discordapp.com/attachments/731709481863479436/1000436949917630575/A1.png",
        "https://cdn.discordapp.com/attachments/731709481863479436/1000436950211252385/A2.png",
        "https://cdn.discordapp.com/attachments/731709481863479436/1000436950550982716/A3.png",
        "https://cdn.discordapp.com/attachments/731709481863479436/1000436950831988897/A4.png",
        "https://cdn.discordapp.com/attachments/731709481863479436/1000436951180120145/A5.png",
        "https://cdn.discordapp.com/attachments/731709481863479436/1000436951498895380/A6.png",
        "https://cdn.discordapp.com/attachments/731709481863479436/1000436970218078239/A7.png",
        "https://cdn.discordapp.com/attachments/731709481863479436/1000436970754945034/A8.png",
        "https://cdn.discordapp.com/attachments/731709481863479436/1000436971048554496/A9.png",
        "https://cdn.discordapp.com/attachments/731709481863479436/1000436971337945108/A10.png",
    ]
    default_image = "https://cdn.discordapp.com/attachments/731709481863479436/1000436949573705758/A0.png"
    defeat_image = "https://cdn.discordapp.com/attachments/731709481863479436/1000436971807715378/A11.png"
    victory_image = "https://cdn.discordapp.com/attachments/731709481863479436/1000437894768500876/A12.png"

    button_equiv = {
        "Yes": 0,
        "No": 1,
        "Don't know": 2,
        "Probably": 3,
        "Probably not": 4,
        "Undo": "undo",
        "Guess": "guess",
        "Restart": "restart",
        "End": "end",
    }

    async def __call__(self, bot, user, message, channel, args, flags, **void):
        akinators = bot.data.akinators.akinators
        if args:
            language = full_prune(args.pop(0))
        else:
            language = "en"
        if language in ("", "en", "eng", "english") and "c" not in flags and akinators:
            aki = akinators.popleft()
        else:
            aki = await self.compatible_akinator(language=language, child_mode="c" in flags)
        bot.data.akinators[aki.signature] = aki

        colour = await bot.get_colour(user)
        emb = discord.Embed(colour=colour)
        emb.title = f"Akinator: Question {aki.step + 1}"
        bar = await bot.create_progress_bar(18, 0)
        emb.description = (
            f"*```callback-fun-akinator-{user.id}_{aki.signature}_0-\n"
            + f"{aki.question}```*"
            + bar
        )
        emb.set_image(url=self.default_image)
        emb.set_author(**get_author(user))
        await send_with_react(channel, "", embed=emb, buttons=self.buttons, reference=message)

    async def _callback_(self, bot, message, reaction, argv, user, perm, vals, **void):
        u_id, sig, guessing = map(int, vals.split("_", 2))
        if u_id != user.id and u_id != 0 and perm < 3:
            return
        r = as_str(reaction)
        try:
            ans = self.button_equiv[r]
        except KeyError:
            return

        aki = bot.data.akinators.get(sig)
        if aki:
            aki.__dict__.setdefault("no", set())
        else:
            # colour = await bot.get_colour(user)
            # emb = discord.Embed(colour=colour)
            # emb.title = message.embeds[0].title
            # emb.description = message.embeds[0].description.replace("callback-", "none-")
            # if message.embeds[0].image:
            #     emb.set_image(message.embeds[0].image.url)
            # create_task(message.edit(embed=emb))
            # raise TimeoutError("Akinator game has expired. Please create a new one to proceed!")
            ans = "restart"
        create_task(bot.ignore_interaction(message))

        callback = "callback"

        win = False
        guess = False
        if guessing and ans == 0:
            ans = "end"
            await aki.win()
            for data in aki.guesses:
                if data["id"] not in aki.no:
                    guess = data
                    break
            else:
                guess = aki.first_guess
            resp = await Request(
                CHOICE_URL.format(
                    aki.server,
                    int(aki.timestamp),
                    str(aki.child_mode).lower(),
                    aki.session,
                    aki.signature,
                    aki.step,
                    aki.frontaddr,
                    aki.question_filter,
                    guess["id"],
                    int(aki.timestamp) + aki.step + 1,
                ),
                headers=HEADERS,
                decode=True,
                aio=True,
            )
            resp = aki.parse_response(resp)
            print(resp)
            if resp["completion"] != "OK":
                with tracebacksuppressor:
                    akinator.utils.raise_connection_error(resp["completion"])
            win = max(1, int(resp["parameters"]["element_informations"]["times_selected"]))
        if guessing and ans == 1:
            if aki.step >= 79:
                ans = "end"
            if not aki.guesses:
                await aki.win()
            for data in aki.guesses:
                if data["id"] not in aki.no:
                    aki.no.add(data["id"])
                    break
            else:
                aki.no.add("\x7f" + str(data["id"]))
            resp = await Request(
                EXCLUDE_URL.format(
                    aki.server,
                    int(aki.timestamp),
                    str(aki.child_mode).lower(),
                    aki.session,
                    aki.signature,
                    aki.step,
                    aki.frontaddr,
                    aki.question_filter,
                    int(aki.timestamp) + aki.step + 1,
                ),
                headers=HEADERS,
                decode=True,
                aio=True,
            )
            await aki.win()
            resp = aki.parse_response(resp)
            print(resp)
            if resp["completion"] == "OK":
                aki._update(resp)
                aki.no.clear()
            else:
                with tracebacksuppressor:
                    akinator.utils.raise_connection_error(resp["completion"])
        elif isinstance(ans, int):
            try:
                await aki.answer(ans)
            except json.JSONDecodeError:
                await aki.answer(ans)
            if not guessing and aki.step >= 79:
                guess = True
        elif ans == "undo":
            await aki.back()
            aki.no.clear()
        elif ans == "guess":
            guess = True
        elif ans == "end":
            if guessing and aki.step >= 79:
                guess = None
            else:
                guess = True
            callback = "none"
            bot.data.akinators.pop(aki.signature, None)
        elif ans == "restart":
            if aki:
                bot.data.akinators.pop(aki.signature, None)
                lang = language=aki.uri.split(".", 1)[0]
                child = aki.child_mode
            else:
                lang = "en"
                child = False
            aki = await self.compatible_akinator(language=lang, child_mode=child)
            bot.data.akinators[aki.signature] = aki
            aki.__dict__.setdefault("no", set())

        div = 1
        if (aki.progression >= 80 or guess) and not aki.step >= 79 and not win and not guessing:
            if not aki.guesses:
                await aki.win()
            for data in aki.guesses:
                if data["id"] in aki.no:
                    continue
                guess = data
                break
            else:
                if (guess or aki.progression >= 95) and aki.first_guess:
                    guess = aki.first_guess
                    if "\x7f" + str(guess["id"]) in aki.no:
                        aki.step = 79
                        guess = None
        print(aki.step, aki.progression, aki.guesses, aki.no, sep="\n")

        colour = await bot.get_colour(user)
        emb = discord.Embed(colour=colour)

        desc = ""
        if win:
            aki.progression = 100
            question = f"Great! Guessed right once more ({rank_format(win)} time with this character)! I love playing with you!"
            gold = aki.step * 4
            bot.data.users.add_gold(user, gold)
            desc = "+" + await bot.as_rewards(gold)
            emb.set_image(url=self.victory_image)
            callback = "none"
        elif guess and not guessing:
            if isinstance(guess, bool):
                if not aki.guesses:
                    await aki.win()
                for data in aki.guesses:
                    if data["id"] not in aki.no:
                        guess = data
                        break
                else:
                    guess = aki.first_guess
            if aki.progression >= 90:
                question = f"I'm {round(aki.progression, 2)}% sure it's..."
            else:
                question = f"I'm ({round(aki.progression, 1)}%) thinking of..."
            emb.title = f"Akinator"
            desc = "\xad" + bold(guess["name"]) + "\n" + italics(guess["description"])
            buttons = [self.buttons[0], self.buttons[4]]
            if guess.get("absolute_picture_path"):
                emb.set_image(url=guess["absolute_picture_path"])
        else:
            emb.title = f"Akinator: Question {aki.step + 1}"
            if aki.step >= 79:
                question = "Bravo! You have defeated me! Play the game again on the Akinator website to add the character you were thinking of, and I'll remember for next time!"
                gold = aki.step * 5
                bot.data.users.add_gold(user, gold)
                desc = "+" + await bot.as_rewards(gold)
                emb.set_image(url=self.defeat_image)
                callback = "none"
            else:
                question = aki.question
                emb.set_image(url=choice(self.images))
            buttons = self.buttons
        if callback == "none":
            emb.title = "Akinator: Game ended"
            buttons = (self.buttons[-2],)
            callback = "callback"
        if desc:
            desc += "\n"
        else:
            desc = ""

        guessing = int(bool(guess and not guessing))
        bar = await bot.create_progress_bar(18, aki.progression / 100)
        emb.description = (
            f"*```{callback}-fun-akinator-{user.id}_{aki.signature}_{guessing}-\n"
            + f"{question}```*"
            + desc
            + bar
        )
        emb.set_author(**get_author(user))
        sem = getattr(message, "sem", None)
        if not sem:
            try:
                sem = EDIT_SEM[message.channel.id]
            except KeyError:
                sem = EDIT_SEM[message.channel.id] = Semaphore(5.15, 256, rate_limit=5)
        async with sem:
            return await Request(
                f"https://discord.com/api/{api}/channels/{message.channel.id}/messages/{message.id}",
                data=dict(
                    embeds=[emb.to_dict()],
                    components=restructure_buttons(buttons),
                ),
                method="PATCH",
                authorise=True,
                aio=True,
            )


class UpdateAkinator(Database):
    name = "akinators"
    no_file = True
    no_delete = True

    sem = Semaphore(1, 1, rate_limit=60)

    def __load__(self):
        self.akinators = deque()
        create_task(self.ensure_akinators())

    async def ensure_akinators(self):
        if self.sem.busy:
            return
        t = utc()
        while self.akinators and t > self.akinators[0].timestamp + 240:
            self.akinators.popleft()
        async with self.sem:
            while len(self.akinators) < 2:
                try:
                    aki = await self.bot.commands.akinator[0].compatible_akinator(language="en", child_mode=False)
                except:
                    return
                self.akinators.append(aki)
            for k, aki in tuple(self.data.items()):
                if t > aki.timestamp + 960:
                    self.data.pop(k)

    def __call__(self, **void):
        return self.ensure_akinators()