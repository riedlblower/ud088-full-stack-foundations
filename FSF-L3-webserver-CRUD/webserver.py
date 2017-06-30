from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
      try:

        if self.path.endswith("/restaurants"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            restaurants = session.query(Restaurant).all()
            message = "<html><body>"
            # Objective 3 Step 1 - Create /restarants/new page - create a link
            message += '<p><a href="/restaurants/new">Make a New Restaurant Here</a></p></br>'
            for restaurant in restaurants:
                message += '<br>' + restaurant.name
                index = restaurant.id
                link = "/restaurants/" + str(index) + "/edit"
                message += '<p><a href=' + link + '>Edit</a></p>'
                message += '<p><a href="/restaurants/%s/delete">Delete</a></p></br>' % index
            message = message + "</body></html>"
            self.wfile.write(message)
            return



        # Objective 3 Step 2 - Create /restarants/new page - make the page
        if self.path.endswith("/restaurants/new"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            output = ""
            output += "<html><body>"
            output += "<h1>Make a New Restaurant</h1>"
            output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/new'>"
            output += "<input name = 'newRestaurantName' type = 'text' placeholder = 'New Restaurant Name' > "
            output += "<input type='submit' value='Create'>"
            output += "</form></body></html>"
            self.wfile.write(output)
            return

      # Objective 4 Step 2 - Create /restarants/x/edit - make the page
        if self.path.endswith("/edit"):
            restaurantID = self.path.split("/")[2]
            myQuery = session.query(Restaurant).filter_by(id=restaurantID).one()
            myName = str(myQuery.name)
            myId = str(myQuery.id)
            if myQuery:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Edit the Restaurant Name: " + myQuery.name +"</h1>"
                output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/" + str(myQuery.id) + "/edit'>"
                output += "<input name = 'newRestaurantName' type = 'text' placeholder = '"+ myName + ">"
                output += "<input type='submit' value='Rename'>"
                output += "</form></body></html>"
                self.wfile.write(output)
            return

      # Objective 5 Step 2 Create /restarants/delete - make the page
        if self.path.endswith("/delete"):
            restaurantID = self.path.split("/")[2]
            myQuery = session.query(Restaurant).filter_by(id=restaurantID).one()
            myName = str(myQuery.name)
            myId = str(myQuery.id)
            if myQuery:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Are you sure you want to delete %s? </h1> " % myQuery.name
                output += "<form method = 'POST' enctype='multipart/form-data' action = '/restaurants/%s/delete'>" % restaurantID
                output += "<input type='submit' value='Delete'>"
                output += "</form></body></html>"
                self.wfile.write(output)
            return

      except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    #  Objective 4 Step 3 - Update /edit page - deal with the POST submission
    def do_POST(self):
        try:
            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                    restaurantID = self.path.split("/")[2]

                    myQuery = session.query(Restaurant).filter_by(id=restaurantID).one()

                    # Update the restaurant name
                    if myQuery != []:
                        myQuery.name = messagecontent[0]
                        session.add(myQuery)
                        session.commit()
                        print messagecontent, messagecontent[0]
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()

    #  Objective 5 Step 3 - Delete /restarants/x - deal with the POST submission
            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    #messagecontent = fields.get('newRestaurantName')
                    restaurantID = self.path.split("/")[2]

                    myQuery = session.query(Restaurant).filter_by(id=restaurantID).one()

                    # Delete the restaurant name
                    if myQuery != []:
                        session.delete(myQuery)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()

    #  Objective 3 Step 3 - Create /restarants/new page - deal with the POST submission
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')

                    # Create new Restaurant Object
                    newRestaurant = Restaurant(name=messagecontent[0])
                    session.add(newRestaurant)
                    session.commit()
                    print messagecontent, messagecontent[0]

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

        except:
            pass




def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
