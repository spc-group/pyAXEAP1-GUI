import numpy as np
from math import sqrt

rainbow = (
    (255, 0, 0),  # red
    (255, 130, 0),  # orange
    (220, 220, 0),  # yellow (lowered values so not as bright)
    (0, 255, 0),  # green
    (0, 130, 255),  # cyan
    (0, 0, 255),  # blue
    (130, 0, 255),  # purple(ish)
    (240, 0, 240),  # also purple(ish) (more pink)
)


def colourGen(
    amount: int,
    colour_type: str | int | None,
    colours: tuple | None = None,
    gradient: bool = False,
):
    """
    Generates a colour set for any number of items (amount).
    These can then be directly applied to those items.

    Parameters
    ----------
    amount: :obj:`int`
        The number of colours to return in the list.
    colour_type: :obj:`str` or :obj:`int` or :obj:`None`
        Can be the name of a colour type, or the index of that type, or :obj:`None`.
        Accepted strings:
            "Red Gradient", "Red Gradient (inverted)", "Green Gradient",
            "Green Gradient (inverted)", "Blue Gradient", "Blue Gradient (inverted)",
            "Black-White Gradient", "Black-White (inverted), "Rainbow".
        Accepted integers: 0 through 8.
        NOTE: set to None if using custom colours.
        If set to None, colours given in 'colours' will be used.
    colours: :obj:`tuple` (optional)
        Takes RGB colours ((#red1, #green1, #blue1), (#red2, #green2, #blue2),...)
        Colours to be used if no colour_type is set.
        Will loop through all colours if "gradient" is False.
        Will start on the first colour and end on the last if "gradient" is True.
        NOTE: Will be ignored if 'colour_type' is not :obj:`None`.
    gradient: :obj:`bool` (optional)
        If True, will create a gradient from 'colours'.
        NOTE: Does not work if 'colour_type' is set. Only works with 'colours'.
        WARNING: Only a gradient of two colours is currently configured.

    Returns
    -------
    :obj:`tuple`
        returns an array of colours, equal in length to 'amount'."""

    if type(amount) is not int:
        raise ValueError("'amount' must be an int")

    if colour_type is not None:
        if gradient:
            print("WARNING! 'gradient' is ignored if colour_type is not None")

        if type(colour_type) is str:
            colour_dict = {
                "Red Gradient": 0,
                "Red Gradient (inverted)": 1,
                "Green Gradient": 2,
                "Green Gradient (inverted)": 3,
                "Blue Gradient": 4,
                "Blue Gradient (inverted)": 5,
                "Black-White Gradient": 6,
                "Black-White (inverted)": 7,
                "Rainbow": 8,
            }
            try:
                index = colour_dict[colour_type]
            except KeyError:
                raise KeyError(f"The given 'colour_type' {colour_type} is not valid")

        elif type(colour_type) is int:
            if 0 <= colour_type <= 8:
                index = colour_type
            else:
                raise IndexError(
                    f"the given 'colour_type' {colour_type} is out of range: must be 0-8"
                )

        else:
            raise ValueError(
                f"colour_type must be a str, int, or None object, not {type(colour_type)}"
            )

        if index == 0:
            colour_array = tuple(
                (255 * (amount - n) / amount, 0, 0) for n in range(amount)
            )
        elif index == 1:
            colour_array = tuple((255 * n / amount, 0, 0) for n in range(amount))
        elif index == 2:
            colour_array = tuple(
                (0, 255 * (amount - n) / amount, 0) for n in range(amount)
            )
        elif index == 3:
            colour_array = tuple((0, 255 * n / amount, 0) for n in range(amount))
        elif index == 4:
            colour_array = tuple(
                (0, 0, 255 * (amount - n) / amount) for n in range(amount)
            )
        elif index == 5:
            colour_array = tuple((0, 0, 255 * n / amount) for n in range(amount))
        elif index == 6:
            colour_array = tuple(
                (
                    255 * (amount - n) / amount,
                    255 * (amount - n) / amount,
                    255 * (amount - n) / amount,
                )
                for n in range(amount)
            )
        elif index == 7:
            colour_array = tuple(
                (255 * n / amount, 255 * n / amount, 255 * n / amount)
                for n in range(amount)
            )
        elif index == 8:
            colour_array = tuple(rainbow[n % len(rainbow)] for n in range(amount))

    else:
        if colours is None:
            raise ValueError("One of 'colour_type' or 'colours' must not be None")

        if gradient:
            steps = len(colours)
            if steps == 2:
                start = colours[0]
                end = colours[1]
                try:
                    sa, sb, sc = start
                    ea, eb, ec = end
                except Exception:
                    sa, sb, sc, _ = start
                    ea, eb, ec, _ = end

                colour_array = tuple(
                    (
                        round((sa * (amount - n) + ea * (n)) / amount),
                        round((sb * (amount - n) + eb * (n)) / amount),
                        round((sc * (amount - n) + ec * (n)) / amount),
                    )
                    for n in np.arange(0, (amount + 1), (amount + 1) / amount)
                )
            else:
                raise NotImplementedError(
                    "multi 'gradient' (more than two colours) is not yet implemented"
                )

        else:
            try:
                colour_array = tuple(colours[n % amount] for n in range(amount))
            except TypeError:
                raise TypeError(
                    f"'colours' must be an array type object, not '{type(colours)}'"
                )

    return colour_array


def contourMap(num: int):
    """
    Generates a simple contour map.
    NOTE: Currently only makes a map of 10 colours and ignores 'num'.

    Parameters
    ----------
    num: :obj:`int`
        Number of colours for map.

    Returns
    -------
    :obj:`tuple` of colours, in RGB values."""

    colours = (
        (0, 0, 0),
        (10, 10, 60),
        (10, 10, 200),
        (20, 20, 255),
        (60, 60, 255),
        (0, 255, 60),
        (0, 255, 0),
        (240, 240, 0),
        (255, 50, 50),
        (255, 0, 0),
    )

    return colours
