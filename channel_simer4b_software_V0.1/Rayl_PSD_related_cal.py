import numpy as np
#import matplotlib.pyplot as plt

def Doppler_PSD_function(type0,Nfft,bandwidth,gauss_sigma):
    f0 = np.linspace(-1, 1, Nfft)  #-1 ~ 1的归一频率轴
    ftn0 = np.ones(Nfft)

    if type0==0:    #Flat
        pass

    elif type0 == 1: #SUI
        ftn0 = 0.785 * np.power(f0,4) - 1.72 * np.power(f0,2) + 1

    elif type0==2:  #Classic(Jakes)
        ftn0 = 1 / np.power( (1 + 1e-6 - np.power(f0,2)), 0.5)

    elif type0==3:  #triangle
        half_1=np.arange(0,512,1)
        half_2 = np.arange(511, -1, -1)
        ftn0=np.append(half_1, half_2)

    elif type0 == 4:  #Gaussian
        ftn0=np.exp( -f0*f0 / (2 * gauss_sigma * gauss_sigma) )

    # plt.plot(f0, ftn0)
    # plt.show()
    # cc=1

    ########### 按通带大小下采样 ###########

    #一种比较准（在对称性方面）的下采样方法，但和c和matlab不一样
    gap=int(1/bandwidth)
    index_=np.arange(0, 1023, gap)
    index_= np.round(index_).astype(int)   #索引号要取整
    ftn1=ftn0.take(index_)

    #和c和matlab一样的下采样方法
    # N_passband=int(bandwidth*Nfft)+1  #防止为0
    # index_=np.linspace(0, 1023, N_passband)
    # index_= np.round(index_).astype(int)   #索引号要取整
    # ftn1=ftn0.take(index_)
    #####################################

    # plt.plot(range(N_passband),ftn1)
    # plt.show()
    # cc=1

    N_padding = int((Nfft - len(ftn1)) / 2)
    ftn1=np.append(np.zeros(N_padding) , ftn1)
    ftn1 = np.append(ftn1 , np.zeros(N_padding))

    while len(ftn1)<Nfft:  #防止取整造成的少数情况
        ftn1 = np.append(0,ftn1)

    ftn1=np.fft.fftshift(ftn1)

    # plt.plot(range(1024),ftn1)
    # plt.show()
    # cc=1

    return ftn1

def gen_window_FIR(type0, bandwidth, gauss_sigma):

    fx=Doppler_PSD_function(type0, 1024, bandwidth, gauss_sigma)

    fx=np.power(fx,0.5)

    fx_time=np.fft.ifft(fx)
    fx_time=np.fft.ifftshift(fx_time)

    index_cut=np.arange(256, 768, 1).astype(int)
    fx_time=fx_time.take(index_cut)    #截断时域

    ########### 做汉明窗 ###########
    a0 = 0.53836
    hamming=a0-(1-a0)*( np.cos( 2 * np.pi * np.arange(0,512)/512) )
    ##############################

    my_win_FIR_coe=fx_time * hamming
    my_win_FIR_coe=np.real(my_win_FIR_coe)

    sss=np.power( np.sum( np.power(my_win_FIR_coe,2) ) ,0.5) #=(sqrt(sum(my_win_FIR_coe.^2)

    my_win_FIR_coe=my_win_FIR_coe/sss

    return my_win_FIR_coe




def gen_freq_domin_filter(type0, bandwidth, gauss_sigma):

    win_FIR_coe=gen_window_FIR(type0, bandwidth, gauss_sigma)

    f=np.fft.fft(win_FIR_coe,1024)

    return f

#产生瑞利衰落多普勒谱相关参数（频域滤波系数）
#变量说明：
#type：谱型 0-flat 1-SUI谱 2-Jakes经典 3-三角 4-高斯
#bandwidth：通带比例，小于1
#gauss_sigma：高斯谱的sigma/fd，决定高斯谱的胖瘦

#返回结果，I0,Q0,I1,Q1,....I255,Q255  signed 10位定点
def gen_Rayl_PSD_param(type0, bandwidth, gauss_sigma):

    f=gen_freq_domin_filter(type0, bandwidth, gauss_sigma)

    ########### 取首位256个 ###########
    index_=np.arange(0,128)
    index_=np.append( index_, np.arange(896,1024) ).astype(int)
    f_cut=f.take(index_)

    ########### 定点化 ###########
    f_I=np.round(np.real(f_cut)*1024).astype(int)
    f_Q = np.round(np.imag(f_cut) * 1024).astype(int)

    ##########   整理  ###########
    data_return=[0]*512
    for i in range(256):
        data_return[2*i]=int(f_I[i])     #numpy.int变为int
        data_return[2 * i+1] = int(f_Q[i])
    return data_return

if __name__ == "__main__":
    aa=gen_Rayl_PSD_param(4,0.2,0.3)
    bb=1