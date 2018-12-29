HMeet Documentation

This app was built in the CS50 IDE using Flask. It uses Flask-Mail, so you need to install
it and start the app via:

pip install Flask-Mail
flask run

The app opens to a login page. To create an account, follow the given link to a new form.
The email must end in @college.harvard.edu. After submitting the form
with the valid information, an email with a confirmation link is sent to the input address.
After following that link (which will expire after 1 hour), the user can log in to HMeets
through the original login page. I implemented this confirmation process for safety reasons,
since I did not want non-Harvard people to have easy access to a list of events happening on
campus.

After logging in, the user is directed to an interactive map. On the map are markers. When
clicked, a window with information regarding the event (title, location, description, time)
pops up. In the upper left is a navigation bar with three links, "Map", "Create Event", and
"Logout". The last does as its name implies. "Map" is simply a way of linking back
to the map. In order to click the "Create Event" button, the user must first select a location
on the map. He or she can do this by single-clicking anywhere on the map, which will cause
a new marker to appear. Subsequent clicks will move the marker.

If the user clicks "Create Event" when this marker is showing, he or she will be redirected
to a new form with information regarding the new event. Filling out this information is made
easy by the TimePicker popups. Upon submission, the user is redirected to the map, where the
new event is now displayed at the position of the marker.

That's it!