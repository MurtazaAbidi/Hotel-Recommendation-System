import eel 

@eel.expose 
def prediction( name, city):
    print (name, city)
eel.init('frontend')
eel.start ('index.html')