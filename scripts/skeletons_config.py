from maya_utils import *
from anytree import Node, RenderTree


# CUSTOM SKELETON
root_custom = Node("RootJ", children=[
    Node("Child1"),
    Node("Child2"),
    ])

# BODY_25B
root_body_25b = Node("CHipJ", id=None, children=[
    Node("RHipJ", id=12, children=[
        Node("RKneeJ", id=14, children=[
            Node("RAnkleJ", id=16, children=[
                Node("RBigToeJ", id=22, children=[
                    Node("RSmallToeJ", id=23),
                ]),
                Node("RHeelJ", id=24),
            ]),
        ]),
    ]),
    Node("LHipJ", id=11, children=[
        Node("LKneeJ", id=13, children=[
            Node("LAnkleJ", id=15, children=[
                Node("LBigToeJ", id=19, children=[
                    Node("LSmallToeJ", id=20),
                ]),
                Node("LHeelJ", id=21),
            ]),
        ]),
    ]),
    Node("NeckJ", id=17, children=[
        Node("HeadJ", id=18, children=[
            Node("NoseJ", id=0),
        ]),
        Node("RShoulderJ", id=6, children=[
            Node("RElbowJ", id=8, children=[
                Node("RWristJ", id=10),
            ]),
        ]),
        Node("LShoulderJ", id=5, children=[
            Node("LElbowJ", id=7, children=[
                Node("LWristJ", id=9),
            ]),
        ]),
    ]),
])

# BODY_25
root_body_25 = Node("CHipJ", id=8, children=[
    Node("RHipJ", id=9, children=[
        Node("RKneeJ", id=10, children=[
            Node("RAnkleJ", id=11, children=[
                Node("RBigToeJ", id=22, children=[
                    Node("RSmallToeJ", id=23),
                ]),
                Node("RHeelJ", id=24),
            ]),
        ]),
    ]),
    Node("LHipJ", id=12, children=[
        Node("LKneeJ", id=13, children=[
            Node("LAnkleJ", id=14, children=[
                Node("LBigToeJ", id=19, children=[
                    Node("LSmallToeJ", id=20),
                ]),
                Node("LHeelJ", id=21),
            ]),
        ]),
    ]),
    Node("NeckJ", id=17, children=[
        Node("Nose", id=0),
        Node("RShoulderJ", id=2, children=[
            Node("RElbowJ", id=3, children=[
                Node("RWristJ", id=4),
            ]),
        ]),
        Node("LShoulderJ", id=5, children=[
            Node("LElbowJ", id=6, children=[
                Node("LWristJ", id=7),
            ]),
        ]),
    ]),
])

# COCO
root_coco = Node("CHipJ", id=None, children=[
    Node("RHipJ", id=8, children=[
        Node("RKneeJ", id=9, children=[
            Node("RAnkleJ", id=10),
        ]),
    ]),
    Node("LHipJ", id=11, children=[
        Node("LKneeJ", id=12, children=[
            Node("LAnkleJ", id=13),
        ]),
    ]),
    Node("NeckJ", id=1, children=[
        Node("Nose", id=0),
        Node("RShoulderJ", id=2, children=[
            Node("RElbowJ", id=3, children=[
                Node("RWristJ", id=4),
            ]),
        ]),
        Node("LShoulderJ", id=5, children=[
            Node("LElbowJ", id=6, children=[
                Node("LWristJ", id=7),
            ]),
        ]),
    ]),
])

# BODY_135
root_body_135 = Node("")