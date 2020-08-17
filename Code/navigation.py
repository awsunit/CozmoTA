import os
import json
import cozmo
from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps
from cozmo.objects import CustomObject, CustomObjectMarkers, CustomObjectTypes
import flash_card_pickup as fcp


faces = {}
flashCards = {}
CUID = {'Circles2':CustomObjectMarkers.Circles2,'Diamonds2':CustomObjectMarkers.Diamonds2}
CUOT = {'Circles2':CustomObjectTypes.CustomType00,'Diamonds2':CustomObjectTypes.CustomType01}

def handle_object_appeared(evt, **kw):
    global flashCards
    # This will be called whenever an EvtObjectAppeared is dispatched -
    # whenever an Object comes into view.
    if isinstance(evt.obj, CustomObject):
        # flashCards[str(evt.obj.object_type)].pose = evt.obj.pose
        oldFc = flashCards[str(evt.obj.object_type)]
        up = evt.updated
        for u in up:
            print(u)

        fc = fcp.Flashcard(str(evt.obj.object_type), evt.obj.pose, oldFc.questions, oldFc.answers, oldFc.pickupable, oldFc.object_id)
        flashCards[str(evt.obj.object_type)] = fc
        print("Cozmo started seeing at: ",  evt.obj.pose)



def define_flash_cards(robot):
    global CUID, CUOT, flashCards
    #
    path = os.path.join(os.getcwd(), "../Flashcards/Lesson1.json")
    file = open(path, "r")
    jsonInput = file.read()
    jsonFc = json.loads(jsonInput)
    for card in jsonFc["Flashcards"]:
        # self.cozmoTA.robot.world.define_custom_cube(self.CUOT[card["cardId"]], self.CUID[card["cardId"]], 50.8 , 25.4, 25.4, True)
        robot.world.define_custom_cube(CUOT[card["cardId"]], CUID[card["cardId"]], 44.5, 44.5, 25.4, False)#######################
        # co = robot.world.define_custom_wall(CUOT[card["cardId"]], CUID[card["cardId"]], 44.5, 44.5, 25.4, True)

        # print("tried")
        id = 4#co.object_id
        # print("id'd")

        fc = fcp.Flashcard(card["cardId"], None, card["questions"], card["answers"])
        flashCards[str(CUOT[card["cardId"]])] = fc

    print(flashCards)
    file.close()

def find_cards(robot):
    global flashCards
    for f in flashCards:
        robot.move_lift(-3)
        robot.set_head_angle(degrees(5)).wait_for_completed()
        # find its pose on the table
        # kind of icky, what if card isn't on table (lost)?
        print("Looking at card: ", f)
        card = flashCards[f]
        if card.pose is None:
            fcp.cozmo_turn_in_place(robot, 360, 25)

def tutor(robot):
    global flashCards
    print("starting the tutoring")

    for fc in flashCards:
            card = flashCards[fc]
            # allowing for the possibility that CozmoTA didn't see one of the cards
            if card.pose is not None:
                pickup_card(card, robot)


def start(robot: cozmo.robot.Robot):
    global flashCards
    # get our cards
    define_flash_cards(robot)

    # event handler
    robot.add_event_handler(cozmo.objects.EvtObjectObserved, handle_object_appeared)

    # attempt to find all the cards?
    find_cards(robot)

    for c in flashCards:
        card = flashCards[c]
        print("our pose is: ", card.pose)
    # faces found in next stage dynamically

    # remove handler to prevent odd behavior
    # self.cozmoTA.robot.remove_event_handler(cozmo.objects.EvtObjectAppeared, handle_object_appeared)

    # start the round robin process
    tutor(robot)


def pickup_card(card, robot):
    print("pick up")
    # robot.pickup_object(card, num_retries=3).wait_for_completed()
    print("done")




if __name__ == '__main__':
    cozmo.run_program(start)
