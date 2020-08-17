import cozmo
import Robot
import Tutor


def r(robot: cozmo.robot.Robot):
    cozmo = Robot.RobotTA(robot, None)
    tutor = Tutor(cozmo)

    # need to initialize then test just like it was normally called
    tutor.define_flash_cards()

if __name__ == '__main__':
    cozmo.run_program(r)