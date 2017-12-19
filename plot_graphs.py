# Script provides some synthetic waveforms for forward modeling
#

from scipy.signal import butter, lfilter


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y


if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib as mpl

    # Sample rate and desired cutoff frequencies (in Hz).
    fs = 20.0
    lowcut = 1.5
    highcut = 3.0

    # Filter a noisy signal.
    T = 20.0
    nsamples = T * fs
    t = np.linspace(0, T, nsamples, endpoint=False)
    a = 0.02
    f0 = 2.31

    x = 1.0 * np.random.rand(len(t))

    x[0:100] = 0
    x[-200:] = 0

    mpl.rc('figure', figsize=(15, 5))

    plt.figure(2)
    plt.clf()

    # template 1

    templates_count = 4
    templates = []
    a = [1.0, 0.8, 0.6, 0.9]
    for ii in range(templates_count):
        cur_templ = butter_bandpass_filter(x.copy(), lowcut, highcut, fs, order=3)
        cur_templ += 0.2 * (np.random.rand(len(x)) - 0.5)
        cur_templ = a[ii] * butter_bandpass_filter(cur_templ, lowcut, highcut, fs, order=3)
        templates.append(cur_templ)

    traces = []
    for cur_templ in templates:
        cur_trace = cur_templ.copy()
        cur_trace[0:100] = 0; cur_trace[-150:] = 0
        cur_trace += 0.07 * (np.random.rand(len(x)) - 0.5)
        cur_trace = butter_bandpass_filter(cur_trace, 0.2, 4, fs, order=3)
        traces.append(cur_trace)

    td = range(0, 5000)

    cc_trace = np.zeros(len(td))
    for ii in range(50):
        rand_index = np.random.randint(0, len(td))
        rand_value = 0.36 * np.random.rand() + 0.3
        cc_trace[rand_index] = rand_value

    # mpl.rc('figure', figsize=(15, 3))

    # plot traces
    for ii in range(templates_count):
        plt.subplot(templates_count, 1, ii + 1)
        plt.plot(t, traces[ii], 'r')
        plt.plot(t, templates[ii], 'b')
    plt.show()

    # plot templates
    for ii in range(templates_count):
        plt.subplot(templates_count, 1, ii + 1)
        axes = plt.gca()
        axes.set_ylim([-0.3, 0.3])
        plt.plot(t, templates[ii])
    plt.show()

    # plot cc trace
    plt.plot(td, cc_trace)
    # plt.show()

    # write templates
    for tt in range(len(templates)):
        with open('template' + str(tt) + '.bln', 'w') as file_to_write:
            file_to_write.write(str(len(t)) + '\n')
            for ii in range(len(t)):
                file_to_write.write(str(t[ii]) + ',' + str(templates[tt][ii]) + '\n')

    # write traces
    for tt in range(len(traces)):
        with open('trace' + str(tt) + '.bln', 'w') as file_to_write:
            file_to_write.write(str(len(t)) + '\n')
            for ii in range(len(t)):
                file_to_write.write(str(t[ii]) + ',' + str(traces[tt][ii]) + '\n')

    # write cc trace
    with open('cc.bln', 'w') as file_to_write:
        file_to_write.write(str(len(td)) + '\n')
        for ii in range(len(t)):
            file_to_write.write(str(td[ii]) + ',' + str(cc_trace[ii]) + '\n')