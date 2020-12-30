import matplotlib.pyplot as plt
import numpy as np
import time, random
import math
import serial
from collections import deque
from scipy import signal



#Display loading 
class PlotData:
    def __init__(self, max_entries):
        self.axis_x = deque(maxlen=max_entries)             #存時間差
        self.axis_y = deque(maxlen=max_entries)             #存原始波形的變數
        self.axis_y_av=deque(maxlen=max_entries)            #存原始波形去直流過後的變數
        self.yf=deque(maxlen=max_entries)                   #存原始波形經過傅立葉轉換的變數(最後的值是去掉直流的)
        
        
        self.fre=deque(maxlen=max_entries)                  #存心跳頻率的變數
        x=5                                                #心跳平均的程度
        self.amp=deque([10 for i in range(x)], maxlen=x)    #顯示在figure上表示心跳頻率的震幅(可隨意更動)
        self.fre_av=deque([0 for i in range(x)], maxlen=x)  #存心跳頻率的平均值
        self.fre_last=0                                     #存心跳頻率的平均值的最後一個element
        self.fre_heart=0                                    #存心律的值
        self.ftime=[]                                       #存取兩個波峰的變數
        self.reg=0
        self.count=0
        self.reg2=0
        
        
        self.max_fir=0                                      #n點平均濾波器的變數預設為零
        self.yfir=deque(maxlen=max_entries)                 #存原始波形經過fir filter後的值
        self.axis_y_av_fir=deque(maxlen=max_entries)        #經過FIR filter再去掉直流的結果
        
        
        self.w=deque(maxlen=max_entries*10)                 #取frequency response的頻率變數
        self.yfreqresp=deque(maxlen=max_entries*10)         #取frequency response的y-axis變數
        
        
        self.x=np.linspace(np.random.randn(200), max_entries)             #顯示頻率時的x-axis
        
        self.angle = np.linspace(-np.pi, np.pi, 100)        #可以在一定範圍內來均勻地撒點->再-pi到pi均勻的撒50個點
        self.cirx = 0
        self.ciry = 0
        self.coeff=[]
        self.xy=[]
        
    def add(self, x, y):
        self.axis_x.append(x)
        self.axis_y.append(y)
        self.axis_y_av.append(y-np.mean(self.axis_y))
        self.yf=np.fft.fft(self.axis_y)                     #取傅立葉轉換                
        self.yf[0]=0
        self.yf=np.fft.ifft(self.yf)
    
    def f(self, y):
        if(y>self.reg and self.reg2==0):                    #儲存最大值的y和當時的時間
            self.ftime[0]=time.time()
            self.reg=y
            self.count=0
        else:
            self.count=self.count+1
            if self.count>=30:                              #連續50個y小於目前值就表示下降
                self.reg2=1
                if self.reg==y:
                    self.ftime[1]=time.time()
                    self.count=self.reg=self.reg2=0         #此時已找到兩個波峰，就把其他的值歸零
            
        if self.ftime[0]!=self.ftime[1] and self.ftime[0]<self.ftime[1]:
            self.fre.append(1/(self.ftime[1]-self.ftime[0]))
            self.ftime[0]=self.ftime[1]
            self.fre_av.append(np.mean(self.fre))
            self.fre_last=self.fre_av[-1]
            self.fre_heart=self.fre_last*60                 #從心跳頻率轉到心律
            print("即時心律: ", self.fre_heart)
            
            
    def fir(self):                                          #處理fir filter的function
        j=k=0
        if len(self.axis_y)<self.max_fir:
            for i in range(len(self.axis_y)):
                k=k+self.axis_y[i]
            k=k/self.max_fir
            self.yfir.append(k)
            self.axis_y_av_fir.append(self.yfir[-1]-np.mean(self.yfir))
        else:
            for i in range(self.max_fir):
                j=j+self.axis_y[-1-i]
            j=j/self.max_fir
            self.yfir.append(j)
            self.axis_y_av_fir.append(self.yfir[-1]-np.mean(self.yfir))
            
    def freqresp(self):                                     #取frequency response的function
        bk=[1/self.max_fir for i in range(self.max_fir)]
        self.w, self.yfreqresp = signal.freqz(bk, worN = self.axis_y)
    
#initial
fig, (ax, ax2, ax5, ax4, ax8, ax3) = plt.subplots(6, 1, figsize=[8, 9])     #定義一個視窗且有六個子圖
#, ax6, ax7
line,  = ax.plot(np.random.randn(100), label='Original Data')
line2, = ax2.plot(np.random.randn(100), label="Regulization Data")
line5, = ax5.plot(np.random.randn(100), label="FIR Data")
line4, = ax4.plot(np.random.randn(100), label="Heart rate Data")
line3, = ax3.plot(np.random.randn(100), label="All Frequency of Heart Data 2")
line8, = ax8.plot(np.random.randn(100), label="All Frequency of Heart Data")


fontsize1=8										             #標註每張圖片的title和axis name
ax.set_title("Original Data", fontsize=fontsize1)
ax.set_ylabel("Original Data", fontsize=fontsize1)
ax.set_xlabel("Time(s)", fontsize=fontsize1)
ax2.set_title("Regulization Data", fontsize=fontsize1)
ax2.set_ylabel("Regulization Data", fontsize=fontsize1)
ax2.set_xlabel("Time(s)", fontsize=fontsize1)
ax4.set_title("Original Data", fontsize=fontsize1)
ax4.set_ylabel("Amplitude", fontsize=fontsize1)
ax4.set_xlabel("Frequency(Hz)", fontsize=fontsize1)
ax5.set_title("FIR Data", fontsize=fontsize1)
ax5.set_ylabel("FIR Data", fontsize=fontsize1)
ax5.set_xlabel("Time(s)", fontsize=fontsize1)
ax8.set_title("Frequenct Response", fontsize=fontsize1)
ax8.set_ylabel("Angle", fontsize=fontsize1)
ax8.set_xlabel("Frequency(Hz)", fontsize=fontsize1)

'''
leg = ax.legend(loc='upper right', shadow=True, fontsize=fontsize1)
leg2 = ax2.legend(loc='upper right', shadow=True, fontsize=fontsize1)
leg4 = ax4.legend(loc='upper right', shadow=True, fontsize=fontsize1)
leg5 = ax5.legend(loc='upper right', shadow=True, fontsize=fontsize1)
leg8 = ax8.legend(loc="upper right", shadow=True, fontsize=fontsize1)
'''

plt.setp(line4,color = 'r', marker="o", markersize=12)      #設定ax4的打點方式為圓圈式


PData= PlotData(500)                                        #實例化instanciation
ax4.set_xlim(0, 200)                                        #設定 x 軸的範圍限制
PData.x=np.linspace(min(abs(np.fft.fftfreq(len(PData.x), d=0.01))), 2*max(abs(np.fft.fftfreq(len(PData.x), d=0.01))), len(PData.x))
ax3.set_xlim(min(abs(np.fft.fftfreq(len(PData.x), d=0.01))), 2*max(abs(np.fft.fftfreq(len(PData.x), d=0.01))))
ax8.set_xlim(min(abs(np.fft.fftfreq(len(PData.x), d=0.01))), 2*max(abs(np.fft.fftfreq(len(PData.x), d=0.01))))
#print(len(PData.x))
#ax3.set_xlim(0, 200)
#ax8.set_xlim(0, 200)
ax.set_ylim(0, 500)                                         #設定 y 軸的範圍限制
ax2.set_ylim(-25, 25)
ax3.set_ylim(0, 100)
ax4.set_ylim(0, 20)
ax5.set_ylim(-15, 15)
ax8.set_ylim(0, 100)
PData.ftime=[0.0, 1.0]                                      #非常重要一定要加，不然進不去PData.f()


'''
line6, = ax6.plot(np.random.randn(100), label="Frequenct Response")
line7, = ax7.plot(np.random.randn(100), label="Frequenct Response")
ax6.set_title("Frequenct Response", fontsize=fontsize1)
ax6.set_ylabel("Amplitude", fontsize=fontsize1)
ax6.set_xlabel("Frequency(Hz)", fontsize=fontsize1)
ax7.set_title("Frequenct Response", fontsize=fontsize1)
ax7.set_ylabel("Angle(deg)", fontsize=fontsize1)
ax7.set_xlabel("Frequency(Hz)", fontsize=fontsize1)
#leg6 = ax6.legend(loc="upper right", shadow=True, fontsize=fontsize1)
#leg7 = ax7.legend(loc="upper right", shadow=True, fontsize=fontsize1)
ax6.set_xlim(320, 360)
ax7.set_xlim(320, 360)
ax6.set_ylim(0, 5)
ax7.set_ylim(-180, 180)
'''




# plot parameters
print ('plotting data...')
# open serial port
strPort='com3'
ser = serial.Serial(strPort, 115200)
ser.flush()#wait until all data is written


#----------------Z-domain---------------------------#
PData.max_fir=20    #n點平均濾波器的變數(可隨意更動)

angle = np.linspace(-np.pi, np.pi, 50)#可以在一定範圍內來均勻地撒點->再-pi到pi均勻的撒50個點
cirx = np.sin(angle)
ciry = np.cos(angle)
coeff=[1/PData.max_fir for i in range(PData.max_fir)]
xy=(np.roots(coeff))
plt.figure(figsize=(5,5))#figsize=(8,8)
plt.plot(cirx, ciry,'k-')
for i in range(PData.max_fir-1):
    plt.plot(np.real(xy[i]), np.imag(xy[i]), 'o', markersize=12)

plt.plot(0, 0, 'x', markersize=12)
plt.text(0.1,0.1,len(coeff)-1)
plt.grid()

plt.xlim((-2, 2))
plt.xlabel('Real')
plt.ylim((-2, 2))
plt.ylabel('Imag')
#----------------Z-domain---------------------------#

start = time.time()
while True:
    for ii in range(24):
        try:
            data = float(ser.readline())
            PData.add(time.time() - start, data)
            PData.fir()
            PData.f(data)
        except:
            pass
    #print(time.time()-start, PData.axis_x[0])
    
    #PData.freqresp()
    ax.set_xlim(PData.axis_x[0], PData.axis_x[0]+5)#set_xlim->Set the x-axis view limits.->設定 X 軸的範圍限制
    ax2.set_xlim(PData.axis_x[0], PData.axis_x[0]+5)
    ax5.set_xlim(PData.axis_x[0], PData.axis_x[0]+5)
    
    
    line.set_xdata(PData.axis_x)					#Original Data
    line.set_ydata(PData.axis_y)
    
    line2.set_xdata(PData.axis_x)					#Regulization Data
    line2.set_ydata(PData.axis_y_av)
    
    line4.set_xdata(PData.fre_heart)				#Heart rate Data
    line4.set_ydata(PData.amp)
    
    line5.set_xdata(PData.axis_x)					#FIR Data
    line5.set_ydata(PData.axis_y_av_fir)
    
    #line6.set_xdata(PData.w)						#Frequenct Response(amplitude)
    #line6.set_ydata(abs(PData.yfreqresp))
    
    #line7.set_xdata(PData.w)						#Frequenct Response(angle)
    #line7.set_ydata(np.angle(PData.yfreqresp, deg=True))
    
    if(len(abs(np.fft.fft(PData.axis_y))) == len(PData.x)):
        line8.set_xdata(PData.x)					#All Frequency of Heart Data
        line8.set_ydata(abs(np.fft.fft(PData.axis_y)))
        
        
    if(len(abs(np.fft.fft(PData.axis_y_av_fir))) == len(PData.x)):
        line3.set_xdata(PData.x)					#All Frequency of Heart Data
        line3.set_ydata(abs(np.fft.fft(PData.axis_y_av_fir))) 
    
    fig.canvas.draw()
    fig.canvas.flush_events()                       #更新子圖
    fig.tight_layout()                              #讓每個子圖之間都能互相錯開