from matplotlib import pyplot as plt
import numpy as np

file = open("C:\\Users\\cncen\\AppData\\Local\\Temp\\21611-0002.csv")
result = file.readlines()

years = np.asarray( [ float(x.replace(',','.')) for x in result[6].split(';')[2:] ] )
revenue = np.asarray( [ float(x.replace(',','.')) for x in result[12].split(';')[2:] ] )
visits = np.asarray( [ float(x.replace(',','.')) for x in result[9].split(';')[2:] ] )

prices = np.asarray( [ float(x.replace(',','.')) for x in result[11].split(';')[2:] ] )

plt.plot(years, revenue/(np.max(revenue)), label='Revenue')
plt.plot(years, visits/np.max(visits), label='Visits')
plt.plot(years, prices/np.max(prices), label='Prices')
plt.legend()
plt.show()