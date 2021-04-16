import numpy as np
import math
import Equations as eq

PI = math.pi

def inverseKine(pEnd, yaw):

    # Robot's config
    h = 80
    l1 = 350
    l2 = 350
    l3 = 135

    # Change radiant to degree
    converter = 180/PI
    yaw = yaw * (PI/180)
    # Joint limit
    jointLimit = [300, 930, 300, 270]

    q = np.array([
        [0,0,0,0],
        [0,0,0,0]
    ], dtype='f')

    if len(pEnd) != 3:

        print("Need 3 required arguments!")

        return 0
    else:

        pW = np.array([[pEnd[0]],[pEnd[1]],[pEnd[2]],[1]], dtype='f') + np.dot(eq.rot("Z",yaw), np.array([[-l3],[0],[0],[1]]))

        x = pW[0]
        y = pW[1]
        z = pW[2]

        q2 = z-h

        D = (y**(2)+ x**(2) - l1**(2) - l2**(2)) / (2*l1*l2)
        d = math.sqrt(1-(D**2))

        q3p = math.atan2(d, D)
        q3m = math.atan2(-1*d, D)

        phi_p = math.atan2(l2 * math.sin(q3p), l1+(l2*math.cos(q3p)))
        q1p_p = math.atan2(y, x) - phi_p

        phi_m = math.atan2(l2 * math.sin(q3m), l1+(l2*math.cos(q3m)))
        q1m_m = math.atan2(y, x) - phi_m

        a = np.dot(eq.rot('Z',q1p_p), eq.rot('Z',q3p)).conj().transpose()
        R34pp = np.dot(a, eq.rot('Z',yaw))

        a1 = np.dot(eq.rot('Z',q1m_m), eq.rot('Z',q3m)).conj().transpose()
        R34mm = np.dot(a1, eq.rot('Z',yaw))

        q4pp = math.atan2(R34pp[1,0], R34pp[0,0])
        q4mm = math.atan2(R34mm[1,0], R34mm[0,0])

        # All possibility stances
        q[0] = [q1p_p, q2, q3p, q4pp]
        q[1] = [q1m_m, q2, q3m, q4mm]
        print(q)
        # Add offset, covert radiant to degree unit
        # for each q < 0 then surplus with 360
        offset = [45, 0, 135, 135]
        for i in range(len(q)):
            for j in range(len(q[i])):
                if j != 1:  # Prismatics joint
                    q[i][j] *= converter
                if j == 3:  # joint 4th
                    q[i][j] = offset[j] - q[i][j]
                else:
                    q[i][j] += offset[j]

                if q[i][j] < 0:
                    q[i][j] += 360
        print(q)
        # Apply joint limit
        passed = []
        for i in range(len(q)):
            count = 0
            for j in range(len(q[i])):
                q[i][j] = round(q[i][j])
                if round(q[i][j]) <= jointLimit[j]:
                    count += 1
                else:
                    print("Joint ", j+1, " at ", i, " is over joint limit, value is ", q[i][j])
                if count == 4:
                    passed.append(q[i])

        # Find the best solution
        passedStance = len(passed)
        if passedStance == 0:
            print("There is no possible to reach that point.")
        elif passedStance > 1:
            print("PASS")
            if passed[0][0] > passed[1][0]:
                return passed[1]
            else:
                return passed[0]
        else:
            print("PASS")
            return passed[0]

a = inverseKine([350, 30, 300], PI/2)
print(a)

