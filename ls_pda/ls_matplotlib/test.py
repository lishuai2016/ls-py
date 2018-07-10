import numpy as np
import matplotlib.pyplot as plt

# plt.plot(np.arange(10))
# print(1111)
# plt.figure()



if __name__ == '__main__':
    print(1111)
    # plt.plot(np.arange(10))

    # x = np.linspace(-np.pi, np.pi, 256, endpoint=True)
    # C, S = np.cos(x), np.sin(x)
    # plt.plot(x, C)
    # plt.plot(x, S)

    figure = plt.figure()
    x1 = figure.add_subplot(2,2,1)
    x2 = figure.add_subplot(2, 2, 2)
    x3 = figure.add_subplot(2, 2, 3)

    plt.show()