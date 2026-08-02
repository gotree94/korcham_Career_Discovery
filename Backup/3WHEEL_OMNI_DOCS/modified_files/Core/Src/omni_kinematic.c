/**
 * @file    omni_kinematic.c
 * @brief   3-Wheel Omni Drive Kinematics Implementation
 *
 *  Wheel layout: 2 front (left+right), 1 rear (center)
 *
 *  Kinematic model:
 *
 *  Inverse Kinematics (body -> wheels):
 *    v0 = -sin(150)*vx + cos(150)*vy + R*omega
 *    v1 = -sin(30) *vx + cos(30) *vy + R*omega
 *    v2 = -sin(270)*vx + cos(270)*vy + R*omega
 *
 *  Expanded:
 *    v0 = -0.5*vx - 0.866*vy + R*omega
 *    v1 = -0.5*vx + 0.866*vy + R*omega
 *    v2 =  vx                + R*omega
 *
 *  Forward Kinematics (wheels -> body):
 *    vx    = (r/3) * (-w0 - w1 + 2*w2)
 *    vy    = (r/3) * (w1 - w0) * 2/sqrt(3)
 *    omega = (r/(3*R)) * (w0 + w1 + w2)
 */

#include "omni_kinematic.h"
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846f
#endif

/* Pre-computed constants */
#define SIN_150     0.5f
#define COS_150    -0.8660254f   /* -sqrt(3)/2 */
#define SIN_30      0.5f
#define COS_30      0.8660254f   /*  sqrt(3)/2 */
#define SIN_270    -1.0f
#define COS_270     0.0f

#define TWO_OVER_SQRT3 1.1547005f

void Omni_Init(OmniRobot_t *robot)
{
    robot->x     = 0.0f;
    robot->y     = 0.0f;
    robot->theta = 0.0f;
    robot->vx    = 0.0f;
    robot->vy    = 0.0f;
    robot->omega = 0.0f;
}

void Omni_InverseKinematics(OmniRobot_t *robot,
                            float vx, float vy, float omega,
                            Motor_t *motors)
{
    (void)robot;

    float R = WHEELBASE_RADIUS_M;

    /*
     * Wheel angular velocity [rad/s] -> stored as target linear speed [m/s]
     * We store target in m/s for the motor controller,
     * then Motor_SetSpeed converts to PWM.
     *
     * Actually, the motor SetSpeed works in m/s (linear wheel speed).
     * So we compute the linear velocity of each wheel contact point:
     * v_wheel_i = [-sin(theta_i)*vx + cos(theta_i)*vy + R*omega]
     */
    float v0 = (-SIN_150 * vx + COS_150 * vy + R * omega);   /* = -0.5*vx - 0.866*vy + R*w */
    float v1 = (-SIN_30  * vx + COS_30  * vy + R * omega);   /* = -0.5*vx + 0.866*vy + R*w */
    float v2 = (-SIN_270 * vx + COS_270 * vy + R * omega);   /* =  vx                + R*w */

    motors[MOTOR_0].target_speed = v0;
    motors[MOTOR_1].target_speed = v1;
    motors[MOTOR_2].target_speed = v2;
}

void Omni_ForwardKinematics(OmniRobot_t *robot, const Motor_t *motors)
{
    /* Read wheel linear velocities [m/s] */
    float w0 = motors[MOTOR_0].speed_mps;
    float w1 = motors[MOTOR_1].speed_mps;
    float w2 = motors[MOTOR_2].speed_mps;

    /*
     * vx    = (r/3) * (-w0 - w1 + 2*w2)
     * vy    = (r/3) * (w1 - w0) * 2/sqrt(3)
     * omega = (r/(3*R)) * (w0 + w1 + w2)
     */
    float r = WHEEL_RADIUS_M;
    float R = WHEELBASE_RADIUS_M;
    float r_over_3 = r / 3.0f;

    robot->vx    = r_over_3 * (-w0 - w1 + 2.0f * w2);
    robot->vy    = r_over_3 * (w1 - w0) * TWO_OVER_SQRT3;
    robot->omega = (r / (3.0f * R)) * (w0 + w1 + w2);
}

void Omni_UpdateOdometry(OmniRobot_t *robot, float dt)
{
    /*
     * Integrate in body frame, then rotate to global frame.
     * Simple Euler integration:
     *   x_new     = x_old     + (vx*cos(theta) - vy*sin(theta)) * dt
     *   y_new     = y_old     + (vx*sin(theta) + vy*cos(theta)) * dt
     *   theta_new = theta_old + omega * dt
     */
    float s = sinf(robot->theta);
    float c = cosf(robot->theta);

    robot->x     += (robot->vx * c - robot->vy * s) * dt;
    robot->y     += (robot->vx * s + robot->vy * c) * dt;
    robot->theta += robot->omega * dt;

    /* Normalize theta to [-PI, PI] */
    while (robot->theta > M_PI)  robot->theta -= 2.0f * M_PI;
    while (robot->theta < -M_PI) robot->theta += 2.0f * M_PI;
}

void Omni_ResetOdometry(OmniRobot_t *robot)
{
    robot->x     = 0.0f;
    robot->y     = 0.0f;
    robot->theta = 0.0f;
}
