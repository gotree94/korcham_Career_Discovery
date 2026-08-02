/**
 * @file    omni_kinematic.h
 * @brief   3-Wheel Omni Drive Robot Kinematics
 *
 *  Coordinate system (robot body frame):
 *       Y ^
 *         |
 *    (M0) | (M1)
 *    150° |  30°
 *         |
 *   ------+------> X
 *         |
 *         |  (M2, 270deg)
 *         |      ○
 *
 *  Convention:
 *    - X forward, Y left, rotation CCW positive
 *    - All wheels at 120deg spacing
 *    - vx, vy in [m/s], omega in [rad/s]
 */

#ifndef OMNI_KINEMATIC_H
#define OMNI_KINEMATIC_H

#include "omni_config.h"
#include "motor.h"

/* Robot state */
typedef struct {
    /* Current pose (odometry, dead-reckoning) */
    float x;            /* [m] */
    float y;            /* [m] */
    float theta;        /* [rad] */

    /* Current velocity (from forward kinematics) */
    float vx;           /* [m/s] body frame */
    float vy;           /* [m/s] body frame */
    float omega;        /* [rad/s] */
} OmniRobot_t;

/**
 * @brief  Initialize robot state to zero
 */
void Omni_Init(OmniRobot_t *robot);

/**
 * @brief  Inverse Kinematics: desired body velocity -> wheel speeds
 * @param  robot   Robot state (not modified)
 * @param  vx      Desired forward velocity [m/s]
 * @param  vy      Desired lateral velocity [m/s]
 * @param  omega   Desired rotational velocity [rad/s]
 * @param  motors  Motor array (target_speed is set for each motor)
 */
void Omni_InverseKinematics(OmniRobot_t *robot,
                            float vx, float vy, float omega,
                            Motor_t *motors);

/**
 * @brief  Forward Kinematics: wheel speeds -> body velocity
 * @param  robot   Robot state (vx, vy, omega are updated)
 * @param  motors  Motor array (reads speed_mps from each)
 */
void Omni_ForwardKinematics(OmniRobot_t *robot, const Motor_t *motors);

/**
 * @brief  Update odometry by integrating velocity over dt
 * @param  robot   Robot state (x, y, theta are updated)
 * @param  dt      Time step [seconds]
 */
void Omni_UpdateOdometry(OmniRobot_t *robot, float dt);

/**
 * @brief  Convenience: full update cycle (FK + odometry)
 *         Call this every ENCODER_UPDATE_MS in the main loop
 * @param  robot   Robot state
 * @param  motors  Motor array
 */
void Omni_Update(OmniRobot_t *robot, Motor_t *motors);

#endif /* OMNI_KINEMATIC_H */
