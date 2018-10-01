"""
Initializes the visualization package and makes sure that the matplotlib backend is set to 'AGG'.

Without ensuring the correct backend it is possible that the third party GUI libraries, that matplotlib uses, will break CyberCaptain on headless server. To understand the matplotlib backend check out their documentation (https://matplotlib.org/faq/usage_faq.html#what-is-a-backend)
"""
import matplotlib
matplotlib.use('AGG')
