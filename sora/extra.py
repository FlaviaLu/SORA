import matplotlib.pyplot as plt
import numpy as np
import astropy.units as u

def draw_ellipse(equatorial_radius, oblateness=0.0, center_f=0.0, center_g=0.0, position_angle=0.0, *args, **kwargs):
    """ Plots an ellipse given input parameters

    Parameters:
        radius (float, int): Semi-major axis of the ellipse.
        oblateness (float, int): Oblateness of the ellipse. Default=0.0
        center_x (float, int): Coordinate of the ellipse (abscissa). Default=0.0
        center_y (float, int): Coordinate of the ellipse (ordinate). Default=0.0
        pos_angle (float, int): Pole position angle. Default=0.0
        **kwargs: all other parameters will be parsed directly to matplotlib
    """
    equatorial_radius = np.array(equatorial_radius, ndmin=1)
    oblateness = np.array(oblateness, ndmin=1)
    center_f = np.array(center_f, ndmin=1)
    center_g = np.array(center_g, ndmin=1)
    position_angle = np.array(position_angle, ndmin=1)
    
    theta= np.linspace(-np.pi, np.pi, 1800)
    size_vals, size_theta = np.indices((len(equatorial_radius), len(theta)))
    
    
    if len(equatorial_radius) == 1:
        if 'color' not in kwargs:
            kwargs['color'] = 'black'
        if 'lw' not in kwargs:
            kwargs['lw'] = 2
    else:
        if 'color' not in kwargs:
            kwargs['color'] = 'gray'
        if 'lw' not in kwargs:
            kwargs['lw'] = 0.1
        if 'alpha' not in kwargs:
            kwargs['alpha'] = 0.1
        if 'zorder' not in kwargs:
            kwargs['zorder'] = 0.5
    for i in np.arange(len(equatorial_radius)):
        circle_x =  equatorial_radius[i]*np.cos(theta)
        circle_y =  equatorial_radius[i]*(1.0-oblateness[i])*np.sin(theta)
        plt.plot(circle_x*np.cos(position_angle[i]*u.deg) + circle_y*np.sin(position_angle[i]*u.deg) + center_f[i],
                 -circle_x*np.sin(position_angle[i]*u.deg) + circle_y*np.cos(position_angle[i]*u.deg) + center_g[i],
                 *args, **kwargs)
    plt.axis('equal')


class ChiSquare():
    """ ChiSquare stores the arrays for all inputs and given chi-square.

    Parameters:
        chi2 (array): Array with all the chi-square values
        **kwargs: any other given input must be an array with the same size as chi2.
            the keyword name will be associated as the variable name of the given data
            
    Example:
    
    chisquare = ChiSquare(chi2, immersion=t1, emersion=t2)
    t1 and t2 must be an array with the same size as chi2.
    the data can be accessed as:
    chisquare.data['immersion']

    """
    def __init__(self,chi2,npts,**kwargs):
        self.__names = ['chi2']
        self.data = {'chi2': chi2}
        data_size = len(chi2)
        self.npts = npts
        for item in kwargs.keys():
            if len(kwargs[item]) != data_size:
                raise ValueError('{} size must have the same size as given chi2')
            self.__names.append(item)
            self.data[item] = kwargs[item]
        
    def get_nsigma(self,sigma=1, key=None):
        """ Determines the interval of the chi-square within the n-th sigma

        Parameters:
            sigma (float, int): Value of sigma to calculate.
            key (str): keyword the user desire to obtain results.
            
        Return:
            - if a key is given, it returns two values: the mean value within the n-sigma
            and the error bar within the n-sigma.
            - if no key is given, it returns a dictionary with the minimum chi-square,
            the sigma required, the number of points where chi2 < chi2_min + sigma^2,
            and the mean values and errors for all keys.
        """
        
        values = np.where(self.data['chi2'] < self.data['chi2'].min() + sigma**2)[0]
        output = {'chi2_min': self.data['chi2'].min()}
        output['sigma'] = sigma
        output['n_points'] = len(values)
        for name in self.__names[1:]:
            vmax = self.data[name][values].max()
            vmin = self.data[name][values].min()
            output[name] = [(vmax+vmin)/2.0, (vmax-vmin)/2.0]
        if key is not None:
            if key not in self.__names[1:]:
                raise ValueError('{} is not one of the available keys. Please choose one of {}'
                                 .format(key, self.__names[1:]))
            return output[key]
        return output
    
    def plot_chi2(self, key=None):
        """ Plots an ellipse given input parameters

        Parameters:
            key (str): Key to plot chi square.
            if no key  is given, it will plot for all the keywords.
        """
        sigma_1 = self.get_nsigma(sigma=1)
        sigma_3 = self.get_nsigma(sigma=3)
        if key is not None and (key not in self.__names[1:]):
            raise ValueError('{} is not one of the available keys. Please choose one of {}'
                                 .format(key, self.data.keys()[1:]))
        k = np.where(self.data['chi2'] < sigma_1['chi2_min']+11)
        for name in self.__names[1:]:
            if (key is not None) and (key != name):
                continue
            plt.plot(self.data[name][k], self.data['chi2'][k], 'k.')
            plt.ylim(sigma_1['chi2_min']-1, sigma_1['chi2_min']+10)
            plt.xlim(sigma_3[name][0]-3*sigma_3[name][1], sigma_3[name][0]+3*sigma_3[name][1])
            plt.axhline(sigma_1['chi2_min']+1,linestyle='--',color='red')
            plt.axhline(sigma_3['chi2_min']+9,linestyle='--',color='red')
            #pl.axvline(t_i[chi2.argmin()],linestyle='--',color='red')
            plt.xlabel(name,fontsize=20)
            plt.ylabel('Chi2',fontsize=20)
            if key is None:
                plt.show()
                
    def to_file(self, namefile):
        """ Save the data to a file

        Parameters:
            namefile (str): Filename to save the data
        """
        data = np.vstack(([self.data[i] for i in self.__names]))
        np.savetxt(namefile, data.T, fmt='%11.5f')
        f = open(namefile+'.label', 'w')
        for i, name in enumerate(self.__names):
            f.write('Column {}: {}\n'.format(i+1,name))
        f.close()

    def get_values(self, sigma=0.0):
        values = {}
        if sigma == 0.0:
            k = np.argsort(self.data['chi2'])[0]
        else:
            k = np.where(self.data['chi2'] < self.data['chi2'].min() + sigma**2)[0]
        for name in self.__names[1:]:
            values[name] = self.data[name][k]
        return values
                
    def __str__(self):
        """ String representation of the ChiSquare Object
        """
        sigma_1 = self.get_nsigma(sigma=1)
        sigma_3 = self.get_nsigma(sigma=3)
        output = 'Minimum chi-square: {:.3f}\n'.format(sigma_1['chi2_min'])
        output += 'Number of fitted points: {}\n'.format(self.npts)
        output += 'Minimum chi-square per degree of freedom: {:.3f}\n'.format(sigma_1['chi2_min']/self.npts)
        for name in self.__names[1:]:
            output += '\n{}:\n'.format(name)
            output += '    1-sigma: {:.3f} +/- {:.3f}\n'.format(*sigma_1[name])
            output += '    3-sigma: {:.3f} +/- {:.3f}\n'.format(*sigma_3[name])
        return output
