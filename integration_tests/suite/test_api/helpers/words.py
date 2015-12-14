# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import unicode_literals

import random
import string


NAMES = [
    "Noah",
    "Liam",
    "Mason",
    "Jacob",
    "William",
    "Ethan",
    "Michael",
    "Alexander",
    "James",
    "Daniel",
    "Elijah",
    "Benjamin",
    "Logan",
    "Aiden",
    "Jayden",
    "Matthew",
    "Jackson",
    "David",
    "Lucas",
    "Joseph",
    "Anthony",
    "Andrew",
    "Samuel",
    "Gabriel",
    "Joshua",
    "John",
    "Carter",
    "Luke",
    "Dylan",
    "Christopher",
    "Isaac",
    "Oliver",
    "Henry",
    "Sebastian",
    "Caleb",
    "Owen",
    "Ryan",
    "Nathan",
    "Wyatt",
    "Hunter",
    "Jack",
    "Christian",
    "Landon",
    "Jonathan",
    "Levi",
    "Jaxon",
    "Julian",
    "Isaiah",
    "Eli",
    "Aaron",
    "Emma",
    "Olivia",
    "Sophia",
    "Isabella",
    "Ava",
    "Mia",
    "Emily",
    "Abigail",
    "Madison",
    "Charlotte",
    "Harper",
    "Sofia",
    "Avery",
    "Elizabeth",
    "Amelia",
    "Evelyn",
    "Ella",
    "Chloe",
    "Victoria",
    "Aubrey",
    "Grace",
    "Zoey",
    "Natalie",
    "Addison",
    "Lillian",
    "Brooklyn",
    "Lily",
    "Hannah",
    "Layla",
    "Scarlett",
    "Aria",
    "Zoe",
    "Samantha",
    "Anna",
    "Leah",
    "Audrey",
    "Ariana",
    "Allison",
    "Savannah",
    "Arianna",
    "Camila",
    "Penelope",
    "Gabriella",
    "Claire",
    "Aaliyah",
    "Sadie",
    "Riley",
    "Skylar",
    "Nora",
    "Sarah",
]


def name():
    return (random.choice(NAMES)
            .replace("e", "é")
            .replace("a", "à")
            .replace("i", "ï")
            .replace("o", "ô")
            .replace("u", "û"))


def alphanumeric(length=16):
    choices = string.digits + string.letters
    return "".join(random.choice(choices) for _ in range(length))
