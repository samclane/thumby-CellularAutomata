import thumby

def lorenz(xyz, *, s=10, r=28, b=2.667):
    """
    Parameters
    ----------
    xyz : array-like, shape (3,)
       Point of interest in three-dimensional space.
    s, r, b : float
       Parameters defining the Lorenz attractor.

    Returns
    -------
    xyz_dot : array, shape (3,)
       Values of the Lorenz attractor's partial derivatives at *xyz*.
    """
    x, y, z = xyz
    x_dot = s*(y - x)
    y_dot = r*x - y - x*z
    z_dot = x*y - b*z
    return x_dot, y_dot, z_dot

x = 0
y = 1 
z = 1.05
dt = 0.01
dots = []
for n in range(10000):
    x_dot, y_dot, z_dot = lorenz((x, y, z))
    x += x_dot * dt
    y += y_dot * dt
    z += z_dot * dt
    print(x, y, z)
    dots.append((x, y, z))
    # thumby.display.setPixel(int(7*x + 30), int(5*y), 1)
    thumby.display.setPixel(int(x) + 30, int(y) + 20, 1)
    if len(dots) > 100:
        erase = dots.pop(0)
        thumby.display.setPixel(int(erase[0]) + 30, int(erase[1]) + 20, 0)
    thumby.display.update()
