# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

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
