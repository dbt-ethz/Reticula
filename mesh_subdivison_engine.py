from __future__ import division
from ast import Raise
from asyncio import proactor_events
from hashlib import new
from logging import raiseExceptions
import re
import string
import sys
import os
import random
import operator
from tokenize import group
from webbrowser import get
from .core_mesh import Mesh
from .utils_face import face_normal
import mola


def filter(attr, relate, arg):
    ops = {'>': operator.gt,
           '<': operator.lt,
           '>=': operator.ge,
           '<=': operator.le,
           '==': operator.eq}

    return lambda f: ops[relate](getattr(f, attr), arg)


def selector(faces, filter, ratio):
    selected = []
    unselected_by_ratio = []
    unselected_by_filer = []
    for f in faces:
        if filter(f):
            if random.random() < ratio:
                selected.append(f)
            else:
                unselected_by_ratio.append(f)
        else:
            unselected_by_filer.append(f)
    
    return selected, unselected_by_ratio, unselected_by_filer


class Engine(Mesh):
    """
    """
    def __init__(self):
        super(Engine, self).__init__()
        self.successor_rules = {
            "block":{
                "divide_to": ["block"],
                "undivided": "plaza",
                "group_children": "group_by_default",
            },
            "plot":{
                "divide_to": ["road", "construct_up"],
                "undivided": "plaza",
                "group_children": "group_by_index",
            },
            "construct_up":{
                "divide_to": ["construct_up", "construct_down", "construct_side"],
                "undivided": "roof",
                "group_children": "group_by_orientation",
            },
            "construct_side":{
                "divide_to": ["construct_up", "construct_down", "construct_side"],
                "undivided": "wall",
                "group_children": "group_by_orientation",
            },
            "wall":{
                "divide_to": ["panel"],
                "undivided": "facade",
                "group_children": "group_by_default",
            },
            "panel":{
                "divide_to": ["frame", "glass"],
                "undivided": "brick",
                "group_children": "group_by_index",
            },
            "roof":{
                "divide_to": ["roof"],
                "undivided": "roof",
                "group_children": "group_by_default",
            },
        }

    @classmethod
    def from_mesh(cls, mesh):
        "convert a mola Mesh to a mola Engine"
        engine = cls()
        engine.faces = mesh.faces

        return engine

    @staticmethod
    def groups():
        _groups = [
            0, "block", "block_s", "block_ss", "block_sss", "plaza", "plot", "road", "construct_up", 
            "construct_side", "construct_down", "roof", "roof_s", "roof_f", "wall", "panel", "facade",
            "frame", "glass", "brick"
        ]
        return _groups

    @staticmethod
    def color_by_group(faces):
        values = [Engine.groups().index(f.group) for f in faces]
        mola.color_faces_by_values(faces, values)

    @staticmethod
    def group_by_index(faces, child_a, child_b):
        "assign group value child_a and child_b to a set of faces according to their index"
        for f in faces[:-1]:
            f.group = child_a
        faces[-1].group = child_b

    @staticmethod
    def group_by_orientation(faces, up, down, side):
        "assign group value up, side and down to a set of faces according to each face's orientation"
        for f in faces:
            normal_z = mola.face_normal(f).z
            if normal_z > 0.1:
                f.group = up
            elif normal_z < -0.1:
                f.group = down
            else:
                f.group = side

    @staticmethod
    def group_by_default(faces, child):
        for f in faces:
            f.group = child

    @staticmethod
    def subdivide(faces, filter, ratio, rule, labling):
        to_be_divided_faces = []
        undivided_faces = []
        unselected_faces = []
        devidied_faces = []

        for f in faces:
            if filter(f):
                if random.random() < ratio:
                    to_be_divided_faces.append(f)
                else:
                    undivided_faces.append(f)
            else:
                unselected_faces.append(f)

        for f in to_be_divided_faces:
            devidied_faces.append(rule(f))

        labling(devidied_faces, undivided_faces)

        devidied_faces = [face for faces in devidied_faces for face in faces]

        return devidied_faces + undivided_faces + unselected_faces

