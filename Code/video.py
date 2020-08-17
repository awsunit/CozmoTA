import cozmo
from cozmo.util import degrees, distance_mm, speed_mmps

def r(robot: cozmo.robot.Robot):
    # robot.move_lift(-5)
    # robot.drive_straight(distance_mm(150), speed_mmps(50)).wait_for_completed()
    robot.move_lift(5)
    robot.turn_in_place(degrees(210)).wait_for_completed()
    robot.drive_straight(distance_mm(150), speed_mmps(50)).wait_for_completed()
    robot.move_lift(-5)
    print("all done boss")



if __name__ == '__main__':
    # cozmo.run_program(move_relative_to_cube)
    cozmo.run_program(r)