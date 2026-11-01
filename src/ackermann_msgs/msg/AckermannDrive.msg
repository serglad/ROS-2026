# Ackermann basic control message.

# Desired steering angle of the steering wheel in radians.
# Left turn is positive (i.e. left of acceptable range).
float32 steering_angle

# Desired steering angle velocity of the steering wheel in radians per second.
float32 steering_angle_velocity

# Desired speed in m/s.
float32 speed

# Desired acceleration along the path defined by speed in m/s^2.
float32 acceleration

# Desired jerk along the direction of motion in m/s^3.
float32 jerk
